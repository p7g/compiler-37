from abc import ABC, abstractmethod
from collections import namedtuple


def align(value, to):
    if value % to == 0:
        return value
    return value + (to - (value % to))


class Type(ABC):
    @abstractmethod
    def size(self):
        ...


class Integer(Type):
    def __init__(self, size):
        assert size % 8 == 0, "Integer size must be multiple of 8"
        self._size = size

    def size(self):
        return self._size // 8


class Pointer(Type):
    def __init__(self, target_type):
        self.target_type = target_type

    def offset(self, amount):
        return self.target_type.size() * amount

    def size(self):
        return 8


class Struct(Type):
    Field = namedtuple("Field", ["name", "type"])

    def __init__(self, name, fields, *, packed=False):
        self.name = name
        assert len(fields) != 0, "Empty struct"
        assert len(set(fields)) == len(fields), "Duplicate field name"
        self.fields = fields
        self.packed = packed

    def _field_offsets(self):
        offset = 0
        for field in self.fields:
            field_size = field.type.size()
            if not self.packed and offset != 0:
                offset = align(offset, to=field_size)
                # offset += (field_size - (offset % field_size)) % field_size
            yield field, offset
            offset += field_size

    def field_offset(self, name):
        for field, offset in self._field_offsets():
            if field.name == name:
                return offset

    def field_type(self, name):
        for field in self.fields:
            if field.name == name:
                return field.type

    def size(self):
        greatest_alignment = 0

        for field, offset in self._field_offsets():
            field_size = field.type.size()
            if field_size > greatest_alignment:
                greatest_alignment = field_size

        subtotal = offset + field_size
        return align(subtotal, to=greatest_alignment)
        # if subtotal % greatest_alignment != 0:
        #     return subtotal + (greatest_alignment - (subtotal % greatest_alignment))
        # return subtotal


class Array(Type):
    def __init__(self, element_type, length):
        assert length >= 0, "Negative array length"
        self.element_type = element_type
        self.length = length

    def index_offset(self, index):
        assert abs(index) < self.length, "Index out of bounds"
        index = (self.length + index) % self.length
        return index * self.element_type.size()

    def size(self):
        return self.element_type.size() * self.length


class Function(Type):
    def __init__(self, argument_types, return_type):
        self.argument_types = argument_types
        self.return_type = return_type

    def size(self):
        return 8  # pointer
