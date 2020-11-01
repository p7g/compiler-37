from compiler.asm import *
from compiler.compile import Compile
from compiler.types import *
from compiler import ast


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


program = ast.File(
    decls=[
        ast.StructDecl(
            name="BigStruct",
            fields=[
                ast.StructDecl.Field("thirty_two", ast.NamedTypeExpr("int32")),
                ast.StructDecl.Field("eight", ast.NamedTypeExpr("int8")),
                ast.StructDecl.Field("sixteen", ast.NamedTypeExpr("int16")),
                ast.StructDecl.Field("eight_two", ast.NamedTypeExpr("int8")),
            ],
        ),
        ast.FunctionDecl(
            export=True,
            name="test",
            arguments=[],
            return_type=ast.NamedTypeExpr("BigStruct"),
            body=[
                ast.VarDecl("a", ast.NamedTypeExpr("BigStruct")),
                ast.AssignStmt(
                    ast.FieldAccessExpr(ast.IdentExpr("a"), "thirty_two"),
                    ast.IntExpr(32),
                ),
                ast.AssignStmt(
                    ast.FieldAccessExpr(ast.IdentExpr("a"), "eight"),
                    ast.IntExpr(8),
                ),
                ast.AssignStmt(
                    ast.FieldAccessExpr(ast.IdentExpr("a"), "sixteen"),
                    ast.IntExpr(16),
                ),
                ast.AssignStmt(
                    ast.FieldAccessExpr(ast.IdentExpr("a"), "eight_two"),
                    ast.IntExpr(82),
                ),
                ast.ReturnStmt(ast.IdentExpr("a")),
            ],
        ),
    ],
)

c = Compile()
c.add_file(program)
print(str(c.finish()))
