from collections import namedtuple


class Decl:
    def __init__(self, export=False):
        self.export = export


class StructDecl(Decl):
    Field = namedtuple("Field", ["name", "type"])

    def __init__(self, name, fields, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.fields = fields


class FunctionDecl(Decl):
    Arg = namedtuple("Arg", ["name", "type"])

    def __init__(self, name, arguments, return_type, body, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.return_type = return_type
        self.arguments = arguments
        self.body = body


class TypeExpr:
    pass


class NamedTypeExpr(TypeExpr):
    def __init__(self, name):
        self.name = name


class ArrayTypeExpr(TypeExpr):
    def __init__(self, element_type, length):
        self.element_type = element_type
        self.length = length


class Stmt:
    pass


class VarDecl(Decl, Stmt):
    def __init__(self, name, type_, init=None):
        self.name = name
        self.type = type_
        self.init = init


class AssignStmt(Stmt):
    def __init__(self, target, value):
        self.target = target
        self.value = value


class ReturnStmt(Stmt):
    def __init__(self, value=None):
        self.value = value


class Expr:
    pass


class IdentExpr(Expr):
    def __init__(self, name):
        self.name = name


class IntExpr(Expr):
    def __init__(self, value):
        self.value = value

    def minimum_size(self):
        bit_len = self.value.bit_length()
        if self.value < 0:
            bit_len += 1
        # ceiling division: https://stackoverflow.com/a/17511341
        return -(-bit_len // 8)


class FieldAccessExpr(Expr):
    def __init__(self, obj, field_name):
        self.obj = obj
        self.field_name = field_name


class File:
    def __init__(self, decls):
        self.decls = decls
