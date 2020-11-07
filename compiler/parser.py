import sys
from antlr4 import CommonTokenStream, InputStream

from . import ast

try:
    from ._parser.Compiler37Lexer import Compiler37Lexer
    from ._parser.Compiler37Parser import Compiler37Parser
    from ._parser.Compiler37Visitor import Compiler37Visitor
except ImportError:
    print("Missing _parser module, run `make parser`", file=sys.stderr)
    raise


class ConvertAST(Compiler37Visitor):
    def visitProgram(self, ctx):
        return ast.File([c.accept(self) for c in ctx.decl()])

    def visitVarDecl(self, ctx):
        return ast.VarDecl(ctx.name.text, ctx.type_.accept(self))

    def visitFunctionDecl(self, ctx):
        return ast.FunctionDecl(
            ctx.name.text,
            ctx.args.accept(self) if ctx.args else [],
            ctx.return_type.accept(self),
            [s.accept(self) for s in ctx.body or []],
            export=True,
        )

    def visitArg(self, ctx):
        return ast.FunctionDecl.Arg(ctx.name.text, ctx.type_.accept(self))

    def visitArgList(self, ctx):
        args = [ctx.car.accept(self)]
        if ctx.cdr:
            args.extend(ctx.cdr.accept(self))
        return args

    def visitStructDecl(self, ctx):
        return ast.StructDecl(ctx.name.text, fields=ctx.fields.accept(self),)

    def visitStructField(self, ctx):
        return ast.StructDecl.Field(ctx.name.text, ctx.type_.accept(self))

    def visitStructFieldList(self, ctx):
        fields = [ctx.car.accept(self)]
        if ctx.cdr:
            fields.extend(ctx.cdr.accept(self))
        return fields

    def visitTypeExpr(self, ctx):
        if ctx.ID():
            return ast.NamedTypeExpr(str(ctx.ID()))
        return ast.ArrayTypeExpr(ctx.element_type().accept(self), int(ctx.length()))

    def visitInteger(self, ctx):
        return ast.IntExpr(int(ctx.getText()))

    def visitExpr(self, ctx):
        if ctx.ID():
            return ast.IdentExpr(str(ctx.ID()))
        if ctx.integer():
            return ctx.integer().accept(self)
        return ctx.expr().accept(self)

    def visitAssign(self, ctx):
        return ast.AssignStmt(
            ctx.assignmentTarget().accept(self), ctx.expr().accept(self)
        )

    def visitAssignmentTarget(self, ctx):
        target = ctx.assignmentTarget()
        if target:
            return ast.FieldAccessExpr(target.accept(self), str(ctx.ID()))
        return ast.IdentExpr(str(ctx.ID()))

    def visitReturn_(self, ctx):
        return ast.ReturnStmt(ctx.expr().accept(self))


def parse(input):
    input_stream = InputStream(input)
    lexer = Compiler37Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = Compiler37Parser(stream)
    return parser.program().accept(ConvertAST())
