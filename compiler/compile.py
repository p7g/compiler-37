from .ast import (
    ArrayTypeExpr,
    AssignStmt,
    FieldAccessExpr,
    FunctionDecl,
    IdentExpr,
    IntExpr,
    NamedTypeExpr,
    ReturnStmt,
    StructDecl,
    VarDecl,
)
from .types_ import align, Array, Function, Integer, Struct
from . import asm as s


class Binding:
    def __init__(self, location, type_):
        self.location = location
        self.type = type_


class Compile:
    def __init__(self):
        self.exports = []
        self.blocks = []
        self.types = {
            "int8": Integer(8),
            "int16": Integer(16),
            "int32": Integer(32),
        }
        self.functions = {}

    def get_type(self, type_expr):
        if isinstance(type_expr, NamedTypeExpr):
            return self.types[type_expr.name]
        if isinstance(type_expr, ArrayTypeExpr):
            return Array(self.get_type(type_expr.element_type), type_expr.length)
        raise NotImplementedError()

    def add_file(self, ast):
        # First pass for types
        for decl in ast.decls:
            if isinstance(decl, StructDecl):
                self.types[decl.name] = Struct(
                    name=decl.name,
                    fields=[Struct.Field(n, self.get_type(t)) for n, t in decl.fields],
                )
            elif isinstance(decl, FunctionDecl):
                self.functions[decl.name] = Function(
                    argument_types=[self.get_type(t) for _, t in decl.arguments],
                    return_type=self.get_type(decl.return_type),
                )
        # Second pass to generate code
        for decl in ast.decls:
            if isinstance(decl, FunctionDecl):
                self.compile_function(decl)

    def compile_function(self, decl):
        if decl.export:
            self.exports.append(decl.name)

        stack_usage = 0
        for stmt in decl.body:
            if isinstance(stmt, VarDecl):
                stack_usage += align(self.get_type(stmt.type).size(), 8)

        # Prologue
        instructions = [
            s.Push(s.Register.rbp),
            s.Mov(s.Register.rsp, s.Register.rbp),
            s.Sub(s.Immediate(stack_usage), s.Register.rsp),
        ]

        stack_offset = 0
        need_end_label = False
        arg_reg = [
            s.Register.rdi,
            s.Register.rsi,
            s.Register.rdx,
            s.Register.rcx,
            s.Register.r8,
            s.Register.r9,
        ]
        locals_ = {
            # FIXME: Arguments are on the stack after the first N
            name: Binding(location=arg_reg[i], type_=t)
            for i, (name, t) in enumerate(decl.arguments)
        }

        def end_label():
            nonlocal need_end_label
            need_end_label = True
            return f"{decl.name}.end"

        def compile_subexpr(expr):
            if isinstance(expr, IntExpr):
                return s.Immediate(expr.value), None
            if isinstance(expr, IdentExpr):
                loc = locals_[expr.name]
                return loc.location, loc.type
            if isinstance(expr, FieldAccessExpr):
                target, target_type = compile_subexpr(expr.obj)
                return (
                    target.with_offset(target_type.field_offset(expr.field_name)),
                    target_type.field_type(expr.field_name),
                )
            raise NotImplementedError(type(expr))

        def compile_expr(expr, type_):
            value, value_type = compile_subexpr(expr)
            if isinstance(expr, IntExpr):
                if not isinstance(type_, Integer):
                    raise TypeError(f"{expr.value} is not assignable to {type_}")
                return value
            if isinstance(expr, IdentExpr):
                if type_ != value_type:
                    raise TypeError(f"{value_type} is not assignable to {type_}")
                return value
            if isinstance(expr, FieldAccessExpr):
                if value_type != type_:
                    raise TypeError(f"{value_type} is not assignable to {type_}")
                return value
            raise NotImplementedError()

        for i, stmt in enumerate(decl.body):
            if isinstance(stmt, VarDecl):
                type_ = self.get_type(stmt.type)
                size = type_.size()
                stack_offset -= align(size, 8)
                loc = locals_[stmt.name] = Binding(
                    s.Address(s.Register.rbp, stack_offset), type_
                )
                if stmt.init is not None:
                    instructions.append(
                        s.Mov(
                            compile_expr(stmt.init, type_),
                            loc.location,
                            size=s.Size.from_byte_size(type_.size()),
                        )
                    )
            elif isinstance(stmt, AssignStmt):
                if isinstance(stmt.target, IdentExpr):
                    loc = locals_[stmt.target.name]
                    dest = loc.location
                    type_ = loc.type
                elif isinstance(stmt.target, FieldAccessExpr):
                    # FIXME: need to loop to handle cases like:
                    # a[0].a.b[2].c = 123;
                    assert isinstance(stmt.target.obj, IdentExpr)
                    loc = locals_[stmt.target.obj.name]
                    assert isinstance(loc.type, Struct)
                    field_offset = loc.type.field_offset(stmt.target.field_name)
                    dest = loc.location.with_offset(field_offset)
                    type_ = loc.type.field_type(stmt.target.field_name)
                else:
                    raise NotImplementedError()
                src = compile_expr(stmt.value, type_=type_)
                instructions.append(
                    s.Mov(src, dest, size=s.Size.from_byte_size(type_.size()))
                )
            elif isinstance(stmt, ReturnStmt):
                if stmt.value:
                    type_ = self.get_type(decl.return_type)
                    src = compile_expr(stmt.value, type_=type_)
                    instructions.append(
                        s.Mov(
                            src,
                            s.Register.rax.with_size(
                                s.Size.from_byte_size(min(type_.size(), 8))
                            ),
                        )
                    )
                    if type_.size() > 16:
                        raise NotImplementedError("Really big return types")
                    elif type_.size() > 8:
                        instructions.append(
                            s.Mov(
                                src.with_offset(8),
                                s.Register.rdx.with_size(
                                    s.Size.from_byte_size(type_.size() - 8)
                                ),
                            )
                        )
                if i != len(decl.body) - 1:
                    instructions.append(s.Jmp(end_label()))

        # Epilogue
        if need_end_label:
            instructions.append(s.Label(end_label()))
        instructions.extend(
            [
                s.Leave(),
                s.Ret(),
            ]
        )

        self.blocks.append(
            s.Block(
                label=decl.name,
                instructions=instructions,
            )
        )

    def finish(self):
        return s.Program(self.exports, self.blocks)
