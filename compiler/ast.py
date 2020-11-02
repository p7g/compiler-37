from collections import namedtuple


class Decl:
    def __init__(self, export=False):
        self.export = export


class StructDecl(Decl):
    class Field(namedtuple("Field", ["name", "type"])):
        def __str__(self):
            return f"{self.name}: {self.type}"

    def __init__(self, name, fields, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.fields = fields

    def __str__(self):
        fields = ",\n\t".join(map(str, self.fields))
        comma = "," if self.fields else ""
        return f"struct {self.name} {{\n\t{fields}{comma}\n}}"


class FunctionDecl(Decl):
    class Arg(namedtuple("Arg", ["name", "type"])):
        def __str__(self):
            return f"{self.name}: {self.type}"

    def __init__(self, name, arguments, return_type, body, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.return_type = return_type
        self.arguments = arguments
        self.body = body

    def __str__(self):
        arguments = ", ".join(map(str, self.arguments))
        body = "\n\t".join(map(str, self.body))
        return f"function {self.name}({arguments}): {self.return_type} {{\n\t{body}\n}}"


class TypeExpr:
    pass


class NamedTypeExpr(TypeExpr):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class ArrayTypeExpr(TypeExpr):
    def __init__(self, element_type, length):
        self.element_type = element_type
        self.length = length

    def __str__(self):
        return f"{self.element_type}[{self.length}]"


class Stmt:
    pass


class VarDecl(Decl, Stmt):
    def __init__(self, name, type_, init=None):
        self.name = name
        self.type = type_
        self.init = init

    def __str__(self):
        init = f" = {self.init}" if self.init else ""
        return f"var {self.name}: {self.type}{init};"


class AssignStmt(Stmt):
    def __init__(self, target, value):
        self.target = target
        self.value = value

    def __str__(self):
        return f"{self.target} = {self.value};"


class ReturnStmt(Stmt):
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        value = f" {self.value}" if self.value else ""
        return f"return{value};"


class Expr:
    pass


class IdentExpr(Expr):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class IntExpr(Expr):
    def __init__(self, value):
        self.value = value

    def minimum_size(self):
        bit_len = self.value.bit_length()
        if self.value < 0:
            bit_len += 1
        # ceiling division: https://stackoverflow.com/a/17511341
        return -(-bit_len // 8)

    def __str__(self):
        return str(self.value)


class FieldAccessExpr(Expr):
    def __init__(self, obj, field_name):
        self.obj = obj
        self.field_name = field_name

    def __str__(self):
        return f"{self.obj}.{self.field_name}"


class File:
    def __init__(self, decls):
        self.decls = decls

    def __str__(self):
        return "\n\n".join(map(str, self.decls))
