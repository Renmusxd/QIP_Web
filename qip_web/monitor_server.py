from qip_web.proto import *
from qip.distributed import formatsock
from qip.distributed.manager import AnnotatedSocket
from enum import Enum
from threading import RLock, Condition, Thread
from typing import Tuple, Mapping, Sequence
import socket
import ssl
import select


class HostRepr(object):
    class HostType(Enum):
        manager = 1
        worker = 2

    def __init__(self, host_type: HostType, host_id: str):
        self.host_type = host_type
        self.host_id = host_id
        self.logs = []
        self.errors = []
        self.job = None

    def get_host_type(self) -> HostType:
        return self.host_type

    def get_id(self) -> str:
        return self.host_id

    def push_logs(self, s: str):
        self.logs.append(s)

    def push_errors(self, s: str):
        self.errors.append(s)

    def pop_logs(self) -> Tuple[Sequence[str], Sequence[str]]:
        tmp_log, tmp_err = self.logs, self.errors
        self.logs = []
        self.errors = []
        return tmp_log, tmp_err


class ManagerRepr(HostRepr):
    class ManagerOperation(Enum):
        waiting_for_operation = 1
        running_operation = 2

    def __init__(self, host_info: LoggerHostInfo):
        super().__init__(HostRepr.HostType.manager, host_info.manager_info.manager_id)


class WorkerRepr(HostRepr):
    class WorkerOperation(Enum):
        waiting_for_operation = 1
        running_operation = 2
        sending_state = 3
        receiving_state = 4

    def __init__(self, host_info: LoggerHostInfo):
        super().__init__(HostRepr.HostType.worker, host_info.worker_info.worker_id)


class MonitorServer(Thread):
    INPUT_TIMEOUT = 5

    def __init__(self, host: str = '0.0.0.0', port: int = 1708, certfile: str = None, keyfile: str = None):
        super().__init__()
        self.host = host
        self.port = port

        self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpsock.bind((host, port))

        self.ssl = certfile and keyfile
        self.certfile = certfile
        self.keyfile = keyfile

        self.timeout_duration = 1

        self.manager_sockets = {}
        self.worker_sockets = {}

        self.job_hosts = {}

        self.socket_lock = RLock()
        self.socket_cond = Condition(self.socket_lock)

    def run(self):
        t = Thread(target=MonitorServer.accept, args=(self,))
        t.start()
        self.serve()
        t.join()

    def accept(self):
        self.tcpsock.listen(5)
        while True:
            clientsock, _ = self.tcpsock.accept()
            clientsock.settimeout(self.timeout_duration)
            clientsock.send(b'\x01' if self.ssl else b'\x00')
            if self.ssl:
                clientsock = ssl.wrap_socket(
                    clientsock,
                    server_side=True,
                    certfile=self.certfile,
                    keyfile=self.keyfile
                )
            clientformatsock = formatsock.FormatSocket(clientsock)
            clientformatsock.settimeout(None)
            host_info = LoggerHostInfo.FromString(clientformatsock.recv())

            # Store alongside the socket whether it's a manager or not.
            with self.socket_lock:
                if host_info.HasAttribute('manager_info'):
                    self.manager_sockets[host_info.manager_info.manager_id] = AnnotatedSocket(clientformatsock,
                                                                                              ManagerRepr(host_info))
                elif host_info.HasAttribute('worker_info'):
                    self.manager_sockets[host_info.worker_info.worker_id] = AnnotatedSocket(clientformatsock,
                                                                                            WorkerRepr(host_info))
                self.socket_cond.notify()

    def get_socks(self):
        with self.socket_lock:
            return list(self.manager_sockets.values()) + list(self.worker_sockets.values())

    def serve(self):
        while True:
            with self.socket_lock:
                socks = self.get_socks()
                while len(socks) == 0:
                    self.socket_cond.wait()
                    socks = self.get_socks()
            # Have a timeout in case new sockets come in
            rs, _, _ = select.select(socks, [], [], MonitorServer.INPUT_TIMEOUT)

            for annsock in rs:
                if annsock.info.get_host_type() == HostRepr.HostType.manager:
                    self.serve_manager(ManagerLog.FromString(annsock.sock.recv()))
                elif annsock.info.get_host_type() == HostRepr.HostType.worker:
                    self.serve_worker(WorkerLog.FromString(annsock.sock.recv()))

    def serve_manager(self, log: ManagerLog):
        man_id = log.manager_id
        with self.worker_sockets:
            manager = self.manager_sockets[man_id]

        if log.HasAttribute('string_log'):
            manager.info.push_log(log.string_log)

        elif log.HasAttribute('error_log'):
            manager.info.push_error(log.string_error)

        elif log.HasAttribute('set_job'):
            manager.job = log.set_job
            if log.set_job not in self.job_hosts:
                self.job_hosts[log.set_job] = (manager, [])
            else:
                self.job_hosts[log.set_job] = (manager, self.job_hosts[log.set_job][1])

        elif log.HasAttribute('clean_job'):
            manager.job = None
            if log.clean_job in self.job_hosts:
                self.job_hosts[log.clean_job] = (None, self.job_hosts[log.clean_job])

    def serve_worker(self, log: WorkerLog):
        worker_id = log.worker_id
        with self.worker_sockets:
            worker = self.worker_sockets[worker_id]

        if log.HasAttribute('string_log'):
            worker.info.push_log(log.string_log)

        elif log.HasAttribute('error_log'):
            worker.info.push_error(log.string_error)

        elif log.HasAttribute('set_job'):
            worker.job = log.set_job
            if log.set_job not in self.job_hosts:
                self.job_hosts[log.set_job] = (None, [worker])
            else:
                manager, workers = self.job_hosts[log.set_job]
                self.job_hosts[log.set_job] = (manager, workers + [worker])

        elif log.HasAttribute('clear_job'):
            worker.job = None
            if log.clean_job in self.job_hosts:
                if worker in self.job_hosts[log.clean_job][1]:
                    self.job_hosts[log.clean_job][1].remove(worker)

    # To get information from the server use the functions below
    def pop_manager_logs(self) -> Tuple[Mapping[str, Sequence[str]], Mapping[str, Sequence[str]]]:
        with self.worker_sockets:
            zip_dict = {k: self.manager_sockets[k].info.pop_logs() for k in self.manager_sockets}
            return {k: v[0] for k, v in zip_dict.items()}, {k: v[1] for k, v in zip_dict.items()}

    def pop_worker_logs(self) -> Tuple[Mapping[str, Sequence[str]], Mapping[str, Sequence[str]]]:
        with self.worker_sockets:
            zip_dict = {k: self.worker_sockets[k].info.pop_logs() for k in self.worker_sockets}
            return {k: v[0] for k, v in zip_dict.items()}, {k: v[1] for k, v in zip_dict.items()}
