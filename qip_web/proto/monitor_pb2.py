# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: monitor.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='monitor.proto',
  package='qip_web',
  syntax='proto2',
  serialized_pb=_b('\n\rmonitor.proto\x12\x07qip_web\"!\n\x0bManagerInfo\x12\x12\n\nmanager_id\x18\x01 \x01(\t\"\x1f\n\nWorkerInfo\x12\x11\n\tworker_id\x18\x01 \x01(\t\"m\n\x0eLoggerHostInfo\x12\'\n\x07manager\x18\x01 \x01(\x0b\x32\x14.qip_web.ManagerInfoH\x00\x12%\n\x06worker\x18\x02 \x01(\x0b\x32\x13.qip_web.WorkerInfoH\x00\x42\x0b\n\thost_info\"-\n\nManagerLog\x12\x14\n\nstring_log\x18\x01 \x01(\tH\x00\x42\t\n\x07logtype\",\n\tWorkerLog\x12\x14\n\nstring_log\x18\x01 \x01(\tH\x00\x42\t\n\x07logtype')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_MANAGERINFO = _descriptor.Descriptor(
  name='ManagerInfo',
  full_name='qip_web.ManagerInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='manager_id', full_name='qip_web.ManagerInfo.manager_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=26,
  serialized_end=59,
)


_WORKERINFO = _descriptor.Descriptor(
  name='WorkerInfo',
  full_name='qip_web.WorkerInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='worker_id', full_name='qip_web.WorkerInfo.worker_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=61,
  serialized_end=92,
)


_LOGGERHOSTINFO = _descriptor.Descriptor(
  name='LoggerHostInfo',
  full_name='qip_web.LoggerHostInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='manager', full_name='qip_web.LoggerHostInfo.manager', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='worker', full_name='qip_web.LoggerHostInfo.worker', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='host_info', full_name='qip_web.LoggerHostInfo.host_info',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=94,
  serialized_end=203,
)


_MANAGERLOG = _descriptor.Descriptor(
  name='ManagerLog',
  full_name='qip_web.ManagerLog',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='string_log', full_name='qip_web.ManagerLog.string_log', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='logtype', full_name='qip_web.ManagerLog.logtype',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=205,
  serialized_end=250,
)


_WORKERLOG = _descriptor.Descriptor(
  name='WorkerLog',
  full_name='qip_web.WorkerLog',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='string_log', full_name='qip_web.WorkerLog.string_log', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='logtype', full_name='qip_web.WorkerLog.logtype',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=252,
  serialized_end=296,
)

_LOGGERHOSTINFO.fields_by_name['manager'].message_type = _MANAGERINFO
_LOGGERHOSTINFO.fields_by_name['worker'].message_type = _WORKERINFO
_LOGGERHOSTINFO.oneofs_by_name['host_info'].fields.append(
  _LOGGERHOSTINFO.fields_by_name['manager'])
_LOGGERHOSTINFO.fields_by_name['manager'].containing_oneof = _LOGGERHOSTINFO.oneofs_by_name['host_info']
_LOGGERHOSTINFO.oneofs_by_name['host_info'].fields.append(
  _LOGGERHOSTINFO.fields_by_name['worker'])
_LOGGERHOSTINFO.fields_by_name['worker'].containing_oneof = _LOGGERHOSTINFO.oneofs_by_name['host_info']
_MANAGERLOG.oneofs_by_name['logtype'].fields.append(
  _MANAGERLOG.fields_by_name['string_log'])
_MANAGERLOG.fields_by_name['string_log'].containing_oneof = _MANAGERLOG.oneofs_by_name['logtype']
_WORKERLOG.oneofs_by_name['logtype'].fields.append(
  _WORKERLOG.fields_by_name['string_log'])
_WORKERLOG.fields_by_name['string_log'].containing_oneof = _WORKERLOG.oneofs_by_name['logtype']
DESCRIPTOR.message_types_by_name['ManagerInfo'] = _MANAGERINFO
DESCRIPTOR.message_types_by_name['WorkerInfo'] = _WORKERINFO
DESCRIPTOR.message_types_by_name['LoggerHostInfo'] = _LOGGERHOSTINFO
DESCRIPTOR.message_types_by_name['ManagerLog'] = _MANAGERLOG
DESCRIPTOR.message_types_by_name['WorkerLog'] = _WORKERLOG

ManagerInfo = _reflection.GeneratedProtocolMessageType('ManagerInfo', (_message.Message,), dict(
  DESCRIPTOR = _MANAGERINFO,
  __module__ = 'monitor_pb2'
  # @@protoc_insertion_point(class_scope:qip_web.ManagerInfo)
  ))
_sym_db.RegisterMessage(ManagerInfo)

WorkerInfo = _reflection.GeneratedProtocolMessageType('WorkerInfo', (_message.Message,), dict(
  DESCRIPTOR = _WORKERINFO,
  __module__ = 'monitor_pb2'
  # @@protoc_insertion_point(class_scope:qip_web.WorkerInfo)
  ))
_sym_db.RegisterMessage(WorkerInfo)

LoggerHostInfo = _reflection.GeneratedProtocolMessageType('LoggerHostInfo', (_message.Message,), dict(
  DESCRIPTOR = _LOGGERHOSTINFO,
  __module__ = 'monitor_pb2'
  # @@protoc_insertion_point(class_scope:qip_web.LoggerHostInfo)
  ))
_sym_db.RegisterMessage(LoggerHostInfo)

ManagerLog = _reflection.GeneratedProtocolMessageType('ManagerLog', (_message.Message,), dict(
  DESCRIPTOR = _MANAGERLOG,
  __module__ = 'monitor_pb2'
  # @@protoc_insertion_point(class_scope:qip_web.ManagerLog)
  ))
_sym_db.RegisterMessage(ManagerLog)

WorkerLog = _reflection.GeneratedProtocolMessageType('WorkerLog', (_message.Message,), dict(
  DESCRIPTOR = _WORKERLOG,
  __module__ = 'monitor_pb2'
  # @@protoc_insertion_point(class_scope:qip_web.WorkerLog)
  ))
_sym_db.RegisterMessage(WorkerLog)


# @@protoc_insertion_point(module_scope)
