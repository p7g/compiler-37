from abc import ABC, ABCMeta, abstractmethod
from enum import Enum, EnumMeta


class Size(Enum):
    byte = "b"
    word = "w"
    double_word = "l"
    quad_word = "q"

    @classmethod
    def from_byte_size(cls, size):
        if size == 1:
            return cls.byte
        if size == 2:
            return cls.word
        if size == 4:
            return cls.double_word
        if size == 8:
            return cls.quad_word
        raise NotImplementedError(f"Size for byte_size == {size}")

    def __str__(self):
        return self.value


class SizeMismatch(Exception):
    pass


class UnknownSize(Exception):
    pass


class Operand(ABC):
    @abstractmethod
    def size(self):
        ...

    @abstractmethod
    def with_offset(self, amount):
        ...

    @staticmethod
    def unify_size(a, b=None):
        asize = a.size()

        if b is None:
            if asize is None:
                raise UnknownSize(f"Size of {a} is not known")
            else:
                return asize

        bsize = b.size()
        unified_size = None
        if asize is None:
            unified_size = bsize
        elif bsize is None:
            unified_size = asize
        elif asize != bsize:
            raise SizeMismatch(f"Size of {a} does not match that of {b}")
        else:
            unified_size = asize

        if unified_size is None:
            raise UnknownSize(f"Unable to determine size of {a} and {b}")
        return unified_size


class Address(Operand):
    def __init__(self, register, offset):
        self.register = register
        self.offset = offset

    def size(self):
        return None

    def with_offset(self, amount):
        return Address(self.register, self.offset + amount)

    def __str__(self):
        return f"{self.offset}({self.register})"


class Immediate(Operand):
    def __init__(self, value):
        self.value = value

    def size(self):
        return None

    def with_offset(self, amount):
        return Address(self, amount)

    def __str__(self):
        return f"${self.value}"


class RegisterMeta(EnumMeta, ABCMeta):
    pass


class Register(Operand, Enum, metaclass=RegisterMeta):
    rax = "%rax"
    rbp = "%rbp"
    rsp = "%rsp"
    rdx = "%rdx"
    rcx = "%rcx"
    rsi = "%rsi"
    rdi = "%rdi"
    r8 = "%r8"
    r9 = "%r9"
    edx = "%edx"

    def size(self):
        # e.g. rax, rdx
        if self.name[0] == "r":
            return Size.quad_word
        # e.g. eax, edx
        if self.name[0] == "e":
            return Size.double_word
        # e.g. al, ah
        if self.name[-1] in ("l", "h"):
            return Size.byte
        # e.g. ax
        return Size.word

    def with_offset(self, amount):
        return Address(self, amount)

    def __str__(self):
        return self.value


class Instruction:
    pass


class Mov(Instruction):
    def __init__(self, src, dest, size=None):
        self.src = src
        self.dest = dest
        self.size = size or Operand.unify_size(src, dest)

    def __str__(self):
        return f"mov{self.size} {self.src}, {self.dest}"


class Push(Instruction):
    def __init__(self, src, size=None):
        self.src = src
        self.size = size or Operand.unify_size(src)

    def __str__(self):
        return f"push{self.size} {self.src}"


class Pop(Instruction):
    def __init__(self, dest, size=None):
        self.dest = dest
        self.size = size or Operand.unify_size(dest)

    def __str__(self):
        return f"pop{self.size} {self.dest}"


class Ret(Instruction):
    def __str__(self):
        return "ret"


class Label(Instruction):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name}:"


class Jmp(Instruction):
    def __init__(self, to):
        self.to = to

    def __str__(self):
        return f"jmp {self.to}"


class Block:
    def __init__(self, label, instructions):
        self.label = label
        self.instructions = instructions

    def __str__(self):
        buf = [f"{self.label}:"]

        def maybe_tab(inst):
            if isinstance(inst, Label):
                return str(inst)
            return f"\t{inst}"

        buf.extend(map(maybe_tab, self.instructions))
        return "\n".join(buf)


class Program:
    def __init__(self, exports, blocks):
        self.exports = exports
        self.blocks = blocks

    def __str__(self):
        buf = [f".globl {exp}" for exp in self.exports]
        buf.extend(f"\n{block}" for block in self.blocks)
        return "\n".join(buf)
