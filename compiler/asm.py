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


class RegisterFamily:
    def __init__(self, byte, word, double_word, quad_word, *, extra=None):
        self.sizes = {
            Size.byte: byte,
            Size.word: word,
            Size.double_word: double_word,
            Size.quad_word: quad_word,
        }
        self.extra = extra

    def __contains__(self, reg):
        return reg in set(self.sizes.values()) or (
            self.extra is not None and reg in self.extra
        )

    def size_of(self, reg):
        for size, reg2 in self.sizes.items():
            if reg is reg2:
                return size

    def with_size(self, size):
        return self.sizes[size]

    @classmethod
    def for_register(cls, reg):
        for fam in register_families:
            if reg in fam:
                return fam
        raise KeyError(reg)


class Register(Operand, Enum, metaclass=RegisterMeta):
    # 8 byte
    rax = "%rax"
    rbx = "%rbx"
    rcx = "%rcx"
    rdx = "%rdx"
    rbp = "%rbp"
    rsp = "%rsp"
    rsi = "%rsi"
    rdi = "%rdi"
    r8 = "%r8"
    r9 = "%r9"
    r10 = "%r10"
    r11 = "%r11"
    r12 = "%r12"
    r13 = "%r13"
    r14 = "%r14"
    r15 = "%r15"

    # 4 byte
    eax = "%eax"
    ebx = "%ebx"
    ecx = "%ecx"
    edx = "%edx"
    ebp = "%ebp"
    esp = "%esp"
    esi = "%esi"
    edi = "%edi"
    r8d = "%r8d"
    r9d = "%r9d"
    r10d = "%r10d"
    r11d = "%r11d"
    r12d = "%r12d"
    r13d = "%r13d"
    r14d = "%r14d"
    r15d = "%r15d"

    # 2 byte
    ax = "%ax"
    bx = "%bx"
    cx = "%cx"
    dx = "%dx"
    bp = "%bp"
    sp = "%sp"
    si = "%si"
    di = "%di"
    r8w = "%r8w"
    r9w = "%r9w"
    r10w = "%r10w"
    r11w = "%r11w"
    r12w = "%r12w"
    r13w = "%r13w"
    r14w = "%r14w"
    r15w = "%r15w"

    # 1 byte
    al = "%al"
    bl = "%bl"
    cl = "%cl"
    dl = "%dl"
    ah = "%ah"
    bh = "%bh"
    ch = "%ch"
    dh = "%dh"
    bpl = "%bpl"
    spl = "%spl"
    sil = "%sil"
    dil = "%dil"
    r8b = "%r8b"
    r9b = "%r9b"
    r10b = "%r10b"
    r11b = "%r11b"
    r12b = "%r12b"
    r13b = "%r13b"
    r14b = "%r14b"
    r15b = "%r15b"

    def size(self):
        return RegisterFamily.for_register(self).size_of(self)

    def with_offset(self, amount):
        return Address(self, amount)

    def with_size(self, size):
        return RegisterFamily.for_register(self).with_size(size)

    def __str__(self):
        return self.value


register_families = [
    RegisterFamily(
        Register.al, Register.ax, Register.eax, Register.rax, extra=[Register.ah]
    ),
    RegisterFamily(
        Register.bl, Register.bx, Register.ebx, Register.rbx, extra=[Register.bh]
    ),
    RegisterFamily(
        Register.cl, Register.cx, Register.ecx, Register.rcx, extra=[Register.ch]
    ),
    RegisterFamily(
        Register.dl, Register.dx, Register.edx, Register.rdx, extra=[Register.dh]
    ),
    RegisterFamily(Register.sil, Register.si, Register.esi, Register.rsi),
    RegisterFamily(Register.dil, Register.di, Register.edi, Register.rdi),
    RegisterFamily(Register.spl, Register.sp, Register.esp, Register.rsp),
    RegisterFamily(Register.bpl, Register.bp, Register.ebp, Register.rbp),
    RegisterFamily(Register.r8b, Register.r8w, Register.r8d, Register.r8),
    RegisterFamily(Register.r9b, Register.r9w, Register.r9d, Register.r9),
    RegisterFamily(Register.r10b, Register.r10w, Register.r10d, Register.r10),
    RegisterFamily(Register.r11b, Register.r11w, Register.r11d, Register.r11),
    RegisterFamily(Register.r12b, Register.r12w, Register.r12d, Register.r12),
    RegisterFamily(Register.r13b, Register.r13w, Register.r13d, Register.r13),
    RegisterFamily(Register.r14b, Register.r14w, Register.r14d, Register.r14),
    RegisterFamily(Register.r15b, Register.r15w, Register.r15d, Register.r15),
]


class Instruction:
    pass


class SizedBinaryInstruction(Instruction):
    def __init__(self, src, dest, size=None):
        self.src = src
        self.dest = dest
        self.size = size or Operand.unify_size(src, dest)


class SizedUnaryInstruction(Instruction):
    def __init__(self, operand, size=None):
        self.operand = operand
        self.size = size or Operand.unify_size(operand)


class Mov(SizedBinaryInstruction):
    def __str__(self):
        return f"mov{self.size} {self.src}, {self.dest}"


class Push(SizedUnaryInstruction):
    def __str__(self):
        return f"push{self.size} {self.operand}"


class Pop(SizedUnaryInstruction):
    def __str__(self):
        return f"pop{self.size} {self.operand}"


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


class Sub(SizedBinaryInstruction):
    def __str__(self):
        return f"sub{self.size} {self.src}, {self.dest}"


class Leave(Instruction):
    def __str__(self):
        return "leave"


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
