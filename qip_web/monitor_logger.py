from qip_web.proto import *

from qip.distributed.manager_logger import ServerLogger
from qip.distributed.worker.worker_logger import WorkerLogger
from qip.distributed.proto import HostInformation, WorkerOperation, WorkerSetup
from qip.distributed.formatsock import FormatSocket
import socket
import uuid

import time


class MonitorServerLogger(ServerLogger):
    def __init__(self, addr: str = 'localhost', port: int = 6060):
        super().__init__()
        self.addr = addr
        self.port = port
        self.server_id = str(uuid.uuid4())

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.addr, self.port))
        self.sock = FormatSocket(sock)

        host_info = LoggerHostInfo()
        host_info.manager.manager_id = self.server_id
        self.sock.send(host_info.SerializeToString())

        self.proto_arena = ManagerLog()

    def send(self):
        self.proto_arena.manager_id = self.server_id
        self.sock.send(self.proto_arena.SerializeToString())
        self.proto_arena.Clear()

    def log_string(self, s, **kwargs):
        self.proto_arena.string_log = s
        self.send()

    def log_error(self, s, **kwargs):
        self.proto_arena.string_error = s
        self.send()

    def starting_server(self):
        self.log_string("Starting server")

    def accepting_connections(self):
        self.log_string("Accepting connections.")

    def accepted_connection(self, ssl: bool = False):
        self.log_string("Accepted connection (SSL: {})".format("ON" if ssl else "OFF"))

    def received_worker(self, host_info: HostInformation):
        self.log_string("Received worker: {}".format(host_info))

    def received_client(self, host_info: HostInformation):
        self.log_string("Received client: {}".format(host_info))

    def waiting_for_setup(self):
        self.log_string("Waiting for setup.")

    def making_state(self, handle: str, n: int):
        self.proto_arena.set_job.job_id = handle
        self.proto_arena.set_job.n = n
        self.send()

    def closing_state(self, handle: str):
        self.proto_arena.clear_job = handle
        self.send()

    def waiting_for_operation(self, handle: str):
        self.log_string("Waiting for operation for job {}".format(handle))

    def running_operation(self, handle: str, op: WorkerOperation):
        self.proto_arena.running_op.handle = handle
        self.proto_arena.running_op.op = op.SerializeToString()
        self.send()

    def done_running_operation(self, handle: str, op: WorkerOperation):
        self.proto_arena.done_with_op.handle = handle
        self.send()

    def allocating_workers(self, handle: str, n: int):
        self.log_string("Allocating {} worker(s) for {}.".format(n, handle))

    def returning_workers(self, handle: str, n: int):
        self.log_string("Returning {} worker(s) from {} to pool.".format(n, handle))


class MonitorWorkerLogger(WorkerLogger):
    def __init__(self, addr: str = 'localhost', port: int = 6060):
        super().__init__()
        self.addr = addr
        self.port = port
        self.worker_id = str(uuid.uuid4())

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.addr, self.port))
        self.sock = FormatSocket(sock)

        host_info = LoggerHostInfo()
        host_info.worker.worker_id = self.worker_id
        self.sock.send(host_info.SerializeToString())

        self.proto_arena = WorkerLog()

    def send(self):
        self.proto_arena.worker_id = self.worker_id
        self.sock.send(self.proto_arena.SerializeToString())
        self.proto_arena.Clear()

    def log_string(self, s, **kwargs):
        self.proto_arena.string_log = s
        self.send()

    def log_error(self, s, **kwargs):
        self.proto_arena.string_error = s
        self.send()

    def starting_server(self):
        self.log_string("Starting server")

    def accepting_connections(self):
        self.log_string("Accepting connections.")

    def accepted_connection(self):
        self.log_string("Accepted connection")

    def waiting_for_setup(self):
        self.log_string("Waiting for setup.")

    def accepted_setup(self, setup: WorkerSetup):
        self.log_string("Setup: {}".format(setup))

    def making_state(self, handle: str, input_start: int, input_end: int, output_start: int, output_end: int):
        self.proto_arena.set_job.job_id = handle
        self.proto_arena.set_job.input_start = input_start
        self.proto_arena.set_job.input_end = input_end
        self.proto_arena.set_job.output_start = output_start
        self.proto_arena.set_job.output_end = output_end

        self.send()

    def closing_state(self, handle: str):
        self.proto_arena.clear_job = handle
        self.send()

    def waiting_for_operation(self, handle: str):
        self.log_string("Waiting for operation for job {}".format(handle))

    def running_operation(self, handle: str, op: WorkerOperation):
        self.proto_arena.running_op.handle = handle
        self.proto_arena.running_op.op = op.SerializeToString()
        self.send()

    def done_running_operation(self, handle: str, op: WorkerOperation):
        self.proto_arena.done_with_op.handle = handle
        self.send()

    def sending_state(self, handle: str):
        self.proto_arena.sending_state = handle

    def receiving_state(self, handle: str):
        self.proto_arena.receiving_state = handle

