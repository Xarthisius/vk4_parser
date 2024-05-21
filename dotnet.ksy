meta:
  id: dotnetlist
  file-extension: dotnetlist
  endian: le
seq:
  - id: records
    type: serialized_record
    repeat: until
    repeat-until: _.record_type == record_type_enum::message_end
types:
  serialized_record:
    seq:
      - id: record_type
        type: u1
        enum: record_type_enum
      - id: record
        type:
          switch-on: record_type
          cases:
            record_type_enum::serialized_stream_header: serialization_header_record
            record_type_enum::system_class_with_members_and_types: system_class_with_members_and_types_record
            record_type_enum::member_reference: member_reference_record
            record_type_enum::array_single_primitive: array_single_primitive_record
  array_single_primitive_record:
    seq:
      - id: info
        type: array_info
      - id: value_type
        type: u1
        enum: primitive_type_enum
      - id: values
        type:
          switch-on: value_type
          cases:
            primitive_type_enum::byte: u1
            primitive_type_enum::char: u1
            primitive_type_enum::double: f8
            primitive_type_enum::int16: s2
            primitive_type_enum::int32: s4
            primitive_type_enum::int64: s8
            primitive_type_enum::single: f4
            primitive_type_enum::uint16: u2
            primitive_type_enum::uint32: u4
            primitive_type_enum::uint64: u8
        repeat: expr
        repeat-expr: info.length
  array_info:
    seq:
      - id: object_id
        type: u4
      - id: length
        type: u4
  member_reference_record:
    seq:
      - id: id_ref
        type: u4
  serialization_header_record:
    seq:
      - id: top_id
        type: u4
      - id: header_id
        type: u4
      - id: major_version
        type: u4
      - id: minor_version
        type: u4
  system_class_with_members_and_types_record:
    seq:
      - id: info
        type: class_info
      - id: type_info
        type: member_type_info(info.member_count)
  class_info:
    seq:
      - id: object_id
        type: u4
      - id: name
        type: length_prefixed_string
      - id: member_count
        type: u4
      - id: member_names
        type: length_prefixed_string
        repeat: expr
        repeat-expr: member_count
  member_type_info:
    params:
      - id: count
        type: u4
    seq:
      - id: binary_type
        type: u1
        enum: binary_type_enum
        repeat: expr
        repeat-expr: count
      - id: additional_infos
        repeat: expr
        repeat-expr: count
        type:
          switch-on: binary_type[_index]
          cases:
            binary_type_enum::primitive: primitive_type
            binary_type_enum::system_class: system_class_name
            binary_type_enum::klass: class_info
            binary_type_enum::primitive_array: primitive_type
      - id: members
        repeat: expr
        repeat-expr: count
        type:
          switch-on: binary_type[_index]
          cases:
            binary_type_enum::primitive: primitive_value(additional_infos[_index].as<primitive_type>.ptype)
            binary_type_enum::primitive_array: serialized_record
  primitive_value:
    params:
      - id: value_type
        type: u1
        enum: primitive_type_enum
    seq:
      - id: value
        type:
          switch-on: value_type
          cases:
            primitive_type_enum::byte: u1
            primitive_type_enum::char: u1
            primitive_type_enum::double: f8
            primitive_type_enum::int16: s2
            primitive_type_enum::int32: s4
            primitive_type_enum::int64: s8
            primitive_type_enum::single: f4
            primitive_type_enum::uint16: u2
            primitive_type_enum::uint32: u4
            primitive_type_enum::uint64: u8
  system_class_name:
    seq:
      - id: class_name
        type: strz
        encoding: utf-8
  primitive_type:
    seq:
      - id: ptype
        type: u1
        enum: primitive_type_enum
  length_prefixed_string:
    seq: 
      - id: length_bytes
        type: length_byte(_index)
        repeat: until
        repeat-until: _.last == true
      - id: value
        type: str
        size: length
        encoding: utf-8
    instances:
      length:
        value: length_bytes[length_bytes.size - 1].current_value
  length_byte:
    params:
      - id: idx
        type: u1
    seq:
      - id: val
        type: u1
    instances:
      last:
        value: ((val & 128) == 0)
      current_value:
        value: "idx == 0 ? val : _parent.length_bytes[idx - 1].as<length_byte>.current_value.as<u4> + (val << (idx * 8))"
enums:
  record_type_enum:
    0: serialized_stream_header
    1: class_with_id
    2: system_class_with_members
    3: class_with_members
    4: system_class_with_members_and_types
    5: class_with_members_and_types
    6: binary_object_string
    7: binary_array
    8: member_primitive_typed
    9: member_reference
    10: object_null
    11: message_end
    12: binary_library
    13: object_null_multiple_256
    14: object_null_multiple
    15: array_single_primitive
    16: array_single_object
    17: array_single_string
    21: method_call
    22: method_return
  binary_type_enum:
    0: primitive
    1: string
    2: object
    3: system_class
    4: klass
    5: object_array
    6: string_array
    7: primitive_array
  primitive_type_enum:
    1: boolean
    2: byte
    3: char
    4: empty
    5: decimal
    6: double
    7: int16
    8: int32
    9: int64
    10: sbyte
    11: single
    12: timespan
    13: datetime
    14: uint16
    15: uint32
    16: uint64
    17: null_
    18: string
