parser: Compiler37.g4 compiler/_parser
	antlr -o compiler/_parser -no-listener -visitor Compiler37.g4

compiler/_parser:
	mkdir compiler/_parser

.PHONY: parser
