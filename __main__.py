import argparse
from compiler.compile import Compile
from compiler.parser import parse

argparser = argparse.ArgumentParser(description="Compiler 37")
argparser.add_argument("files", metavar="FILE", type=str, nargs="+", help="Input files")
argparser.add_argument(
    "-o",
    "--output",
    dest="out",
    type=str,
    default="-",
    help="Output assembly to a file",
)
args = argparser.parse_args()

c = Compile()

for file in args.files:
    with open(file, "r") as f:
        c.add_file(parse(f.read()))

asm = str(c.finish())
if args.out == "-":
    print(asm)
else:
    with open(args.out, "w") as f:
        f.write(asm)
