from compiler.asm import *
from compiler.compile import Compile
from compiler.parser import parse
from compiler.types_ import *
from compiler import ast


program = parse(
    """
    struct BigStruct {
        thirty_two: int32,
        eight: int8,
        sixteen: int16,
        eight_two: int8,
    }

    function test(): BigStruct {
        var a: BigStruct;
        a.thirty_two = 32;
        a.eight = 8;
        a.sixteen = 16;
        a.eight_two = 82;
        return a;
    }
    """
)

c = Compile()
c.add_file(program)
print(str(c.finish()))
