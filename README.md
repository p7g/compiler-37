# compiler-37

Every time I fail to write a compiler, I (hopefully) get closer to succeeding.

These are the makings of a compiler written in Python that compiles a to-be-
defined language to x86_64 assembly (in GAS syntax for the moment).


As of this writing, it can take an AST representing this (there is no parser
yet):

```
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
```

And print out this:

```asm
.globl test

test:
	pushq %rbp
	movq %rsp, %rbp
	movl $32, -16(%rbp)
	movb $8, -12(%rbp)
	movw $16, -10(%rbp)
	movb $82, -8(%rbp)
	movq -16(%rbp), %rax
	movq -8(%rbp), %rdx
	popq %rbp
	ret
```

This is kinda cool (and less trivial than it may seem) because there are some
fun things at play:

- `BigStruct` is larger than 64 bits, which means that returning it requires
  two registers (RAX and RDX as defined by the System V ABI).
- The members of `BigStruct` need padding to be aligned properly. In this case,
  there is 8 bits of padding after `eight`, and 24 bits of padding after
  `eight_two` so that the total size is a multiple of the size of the largest
  field (`thirty_two`).


This assembly can be tested with a C file like this:

```c
#include <stdint.h>
#include <stdio.h>

struct result {
    int32_t thirty_two;
    int8_t eight;
    int16_t sixteen;
    int8_t eight_two;
};

extern struct result test(void);

int main(void) {
    struct result r = test();

    printf("thirty_two=%d; eight=%d; sixteen=%d; eight_two=%d\n",
           r.thirty_two, r.eight, r.sixteen, r.eight_two);

    return 0;
}
```

To compile it, run this (on Linux):

```console
$ python -c 'import compiler' | as -o from_python.o
$ cc -o try-it from_python.o the_c_file.c
$ ./try-it
thirty_two=32; eight=8; sixteen=16; eight_two=82
```


So far, this has been done without any dependencies beyond the Python standard
library. This isn't by choice this time; I couldn't find a library to make
generating assembly any easier.


## Resources

Here are some resources I am finding very helpful for this kinda thing:

- [Compiler Explorer][1]: Helpful for seeing how other compilers deal with code
  samples. So far I have been observing icc, gcc, clang, and rustc.
- Wikipedia's article about [Data structure alignment][2]
- OSDev wiki's article about the [System V ABI][3]


[1]: https://godbolt.org/
[2]: https://en.wikipedia.org/wiki/Data_structure_alignment
[3]: https://wiki.osdev.org/System_V_ABI
