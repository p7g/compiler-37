grammar Compiler37;

options {
    language=Python3;
}

WS : [ \r\n\t]+ -> skip ;
NEWLINE : '\r'? '\n' ;
COMMENT : '//' ~[\n\r]* NEWLINE -> skip ;

POSITIVE_INTEGER : [1-9] [0-9]* | '0' ;
ID : [a-zA-Z_][a-zA-Z0-9_]* ;


program : decl* EOF ;

decl : varDecl | functionDecl | structDecl ;

varDecl : 'var' name=ID ':' type_=typeExpr ('=' init=expr)? ';' ;

functionDecl : 'function' name=ID '(' args=argList? ')' ':' return_type=typeExpr '{' body+=stmt* '}' ;

arg : name=ID ':' type_=typeExpr ;

argList : car=arg (',' cdr=argList)? ','? ;

structDecl : 'struct' name=ID '{' fields=structFieldList '}' ;

structField : name=ID ':' type_=typeExpr ;

structFieldList : car=structField (',' cdr=structFieldList)? ','? ;

typeExpr : named=ID | element_type=ID '[' length=POSITIVE_INTEGER ']' ;

integer : '-'? POSITIVE_INTEGER ;

expr : ID | integer | '(' expr ')' ;

assign : assignmentTarget '=' expr ';' ;

assignmentTarget : ID | assignmentTarget '.' ID ;

return_ : 'return' expr? ';' ;

stmt : varDecl | assign | return_ ;
