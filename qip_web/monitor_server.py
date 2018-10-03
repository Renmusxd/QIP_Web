from qip_web.proto import *
from qip.distributed import formatsock
from qip.distributed.manager import AnnotatedSocket
from qip.distributed.proto import WorkerOperation
from enum import Enum
from threading import RLock, Condition, Thread
from typing import Tuple, Mapping, Sequence, Optional, MutableMapping, Any
import socket
import ssl
import select
import json


class HostRepr(object):
    class HostType(Enum):
        manager = 1
        worker = 2

    def __init__(self, host_type: HostType, host_id: str):
        self.host_type = host_type
        self.host_id = host_id
        self.current_op = None
        self.logs = []
        self.errors = []
        self.job = None
        self.lock = RLock()

    def get_host_type(self) -> HostType:
        return self.host_type

    def get_id(self) -> str:
        return self.host_id

    def set_op(self, op: WorkerOperation):
        with self.lock:
            self.current_op = op

    def set_job(self, job_handle: str):
        with self.lock:
            self.job = job_handle

    def clear_op(self):
        with self.lock:
            self.current_op = None

    def push_log(self, s: str):
        with self.lock:
            # self.logs.append(s)
            pass

    def push_error(self, s: str):
        with self.lock:
            # self.errors.append(s)
            pass

    def pop_logs(self) -> Tuple[Sequence[str], Sequence[str]]:
        with self.lock:
            tmp_log, tmp_err = self.logs, self.errors
            self.logs = []
            self.errors = []
            return tmp_log, tmp_err

    def get_dict(self) -> MutableMapping[str, Any]:
        with self.lock:
            return {
                'host_type': self.host_type.name,
                'host_id': self.host_id,
                'job': self.job or ''
            }

    def get_json(self):
        return json.dumps(self.get_dict())


class ManagerRepr(HostRepr):
    class ManagerOperationEnum(Enum):
        waiting_for_operation = 1
        running_operation = 2

    def __init__(self, host_info: LoggerHostInfo):
        super().__init__(HostRepr.HostType.manager, host_info.manager.manager_id)
        self.op_enum = ManagerRepr.ManagerOperationEnum.waiting_for_operation

    def set_op(self, op: WorkerOperation):
        with self.lock:
            super(ManagerRepr, self).set_op(op)
            self.op_enum = ManagerRepr.ManagerOperationEnum.running_operation

    def clear_op(self):
        with self.lock:
            super(ManagerRepr, self).clear_op()
            self.op_enum = ManagerRepr.ManagerOperationEnum.waiting_for_operation

    def get_dict(self) -> MutableMapping[str, Any]:
        with self.lock:
            output_dict = super(ManagerRepr, self).get_dict()
            if self.op_enum:
                output_dict['op'] = self.op_enum.name

        return output_dict


class WorkerRepr(HostRepr):
    class WorkerOperationEnum(Enum):
        waiting_for_operation = 1
        running_operation = 2
        sending_state = 3
        receiving_state = 4

    def __init__(self, host_info: LoggerHostInfo):
        super().__init__(HostRepr.HostType.worker, host_info.worker.worker_id)
        self.op_enum = WorkerRepr.WorkerOperationEnum.waiting_for_operation
        self.input_start = 0
        self.input_end = 0
        self.output_start = 0
        self.output_end = 0

    def set_op(self, op: WorkerOperation):
        with self.lock:
            super(WorkerRepr, self).set_op(op)
            self.op_enum = WorkerRepr.WorkerOperationEnum.running_operation

    def clear_op(self):
        with self.lock:
            super(WorkerRepr, self).clear_op()
            self.op_enum = WorkerRepr.WorkerOperationEnum.waiting_for_operation

    def sending_state(self):
        with self.lock:
            self.op_enum = WorkerRepr.WorkerOperationEnum.sending_state

    def receiving_state(self):
        with self.lock:
            self.op_enum = WorkerRepr.WorkerOperationEnum.receiving_state

    def get_dict(self) -> MutableMapping[str, Any]:
        with self.lock:
            output_dict = super(WorkerRepr, self).get_dict()
            if self.op_enum:
                output_dict['op'] = self.op_enum.name
            output_dict['input_start'] = self.input_start
            output_dict['input_end'] = self.input_end
            output_dict['output_start'] = self.output_start
            output_dict['output_end'] = self.output_end

        return output_dict


class MonitorServer(Thread):
    INPUT_TIMEOUT = 5

    def __init__(self, host: str = '0.0.0.0', port: int = 6060, certfile: str = None, keyfile: str = None):
        super().__init__()
        self.host = host
        self.port = port

        self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpsock.bind((self.host, self.port))

        if self.port == 0:
            self.port = self.tcpsock.getsockname()[1]
        print("[*] Monitor port is {}".format(self.port))

        self.ssl = certfile and keyfile
        self.certfile = certfile
        self.keyfile = keyfile

        self.timeout_duration = 1

        self.manager_sockets = {}
        self.worker_sockets = {}

        self.socket_lock = RLock()
        self.socket_cond = Condition(self.socket_lock)

        self.job_hosts = {}
        self.job_lock = RLock()

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
                if host_info.HasField('manager'):
                    self.manager_sockets[host_info.manager.manager_id] = AnnotatedSocket(clientformatsock,
                                                                                         ManagerRepr(host_info))
                elif host_info.HasField('worker'):
                    self.worker_sockets[host_info.worker.worker_id] = AnnotatedSocket(clientformatsock,
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
        with self.socket_lock:
            manager = self.manager_sockets[man_id].info

        if log.HasField('string_log'):
            manager.push_log(log.string_log)

        elif log.HasField('string_error'):
            manager.push_error(log.string_error)

        elif log.HasField('set_job'):
            manager.set_job(log.set_job.job_id)
            with self.job_lock:
                if log.set_job.job_id not in self.job_hosts:
                    self.job_hosts[log.set_job.job_id] = (log.set_job.n, manager, [])
                else:
                    _, _, workers = self.job_hosts[log.set_job.job_id]
                    self.job_hosts[log.set_job.job_id] = (log.set_job.n, manager, workers)

        elif log.HasField('clear_job'):
            manager.job = None
            with self.job_lock:
                if log.clear_job in self.job_hosts:
                    _, _, workers = self.job_hosts[log.clear_job]
                    if workers:
                        self.job_hosts[log.clear_job] = (0, None, workers)
                    else:
                        self.job_hosts.pop(log.clear_job)

        elif log.HasField('running_op'):
            op = WorkerOperation.FromString(log.running_op.op)
            manager.set_op(op)

        elif log.HasField('done_with_op'):
            manager.clear_op()

    def serve_worker(self, log: WorkerLog):
        worker_id = log.worker_id
        with self.socket_lock:
            worker = self.worker_sockets[worker_id].info

        if log.HasField('string_log'):
            worker.push_log(log.string_log)

        elif log.HasField('string_error'):
            worker.push_error(log.string_error)

        elif log.HasField('set_job'):
            worker.set_job(log.set_job.job_id)
            worker.input_start = log.set_job.input_start
            worker.input_end = log.set_job.input_end
            worker.output_start = log.set_job.output_start
            worker.output_end = log.set_job.output_end
            with self.job_lock:
                if log.set_job.job_id not in self.job_hosts:
                    self.job_hosts[log.set_job.job_id] = (0, None, [worker])
                else:
                    job_n, manager, workers = self.job_hosts[log.set_job.job_id]
                    workers.append(worker)

        elif log.HasField('clear_job'):
            worker.job = None
            with self.job_lock:
                if log.clear_job in self.job_hosts:
                    job_n, manager, workers = self.job_hosts[log.clear_job]
                    if worker in workers:
                        workers.remove(worker)
                    if not job_n and not manager and not workers:
                        self.job_hosts.pop(log.clear_job)

        elif log.HasField('running_op'):
            op = WorkerOperation.FromString(log.running_op.op)
            worker.set_op(op)

        elif log.HasField('done_with_op'):
            worker.clear_op()

        elif log.HasField('sending_state'):
            worker.sending_state()

        elif log.HasField('receiving_state'):
            worker.receiving_state()

    # To get information from the server use the functions below
    def list_jobs(self) -> Sequence[str]:
        with self.job_lock:
            return list(self.job_hosts.keys())

    def job_details(self, job_handle: str) -> Optional[Mapping[str, Any]]:
        with self.job_lock:
            if job_handle not in self.job_hosts:
                return None
            job_n, manager, workers = self.job_hosts[job_handle]
        return {
            'manager': manager.get_dict() if manager else dict(),
            'workers': [worker.get_dict() for worker in workers] if workers else [],
            'n': job_n
        }

    def all_jobs(self):
        with self.job_lock:
            return {handle: self.job_details(handle) for handle in self.list_jobs()}

    def pop_manager_logs(self) -> Tuple[Mapping[str, Sequence[str]], Mapping[str, Sequence[str]]]:
        with self.socket_lock:
            zip_dict = {k: self.manager_sockets[k].info.pop_logs() for k in self.manager_sockets}
            return {k: v[0] for k, v in zip_dict.items()}, {k: v[1] for k, v in zip_dict.items()}

    def pop_worker_logs(self) -> Tuple[Mapping[str, Sequence[str]], Mapping[str, Sequence[str]]]:
        with self.socket_lock:
            zip_dict = {k: self.worker_sockets[k].info.pop_logs() for k in self.worker_sockets}
            return {k: v[0] for k, v in zip_dict.items()}, {k: v[1] for k, v in zip_dict.items()}
