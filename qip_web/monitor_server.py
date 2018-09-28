from qip_web.proto import *
from qip.distributed import formatsock
from qip.distributed.manager import AnnotatedSocket
import socket
import ssl
import select
from threading import RLock, Condition, Thread


class HostRepr(object):
    def __init__(self, host_type: str):
        self.host_type = host_type

    def get_host_type(self):
        return self.host_type


class ManagerRepr(HostRepr):
    def __init__(self, host_info: LoggerHostInfo):
        super().__init__('manager')


class WorkerRepr(HostRepr):
    def __init__(self, host_info: LoggerHostInfo):
        super().__init__('worker')


class MonitorServer(Thread):
    INPUT_TIMEOUT = 5

    def __init__(self, host='0.0.0.0', port=1708, certfile: str = None, keyfile: str = None):
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
            clientsock, (ip, port) = self.tcpsock.accept()
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
                if annsock.info.get_host_type() == 'manager':
                    self.serve_manager(ManagerLog.FromString(annsock.sock.recv()))
                elif annsock.info.get_host_type() == 'worker':
                    self.serve_worker(WorkerLog.FromString(annsock.sock.recv()))

    def serve_manager(self, log: ManagerLog):
        pass

    def serve_worker(self, log: WorkerLog):
        pass
