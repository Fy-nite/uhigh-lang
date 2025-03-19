# μHigh Programming Language

μHigh is a simple high-level programming language that compiles to MicroASM.

## Features

- Variable declarations (var) and constants (const)
- Basic arithmetic operations (+, -, *, /)
- Print statements for strings and expressions
- Input statements for reading numbers
- Comments using //
- If/else conditionals
- While loops
- Basic functions
- Expression grouping with parentheses
- Include other .uh files

## Syntax

### Constants
```
const name value
```

### Variables
```
var name
```

### Assignment
```
name = expression
```

### Print
```
print "string literal"
print expression
```

### Input
```
input variable
```

### Control Flow
```
if condition {
    statements
}

while condition {
    statements
}
```

### Functions
```
func name() {
    statements
}
```

### Include
```
include "filename.uh"
```

### Conditions
- Equal: ==
- Not equal: !=
- Less than: <
- Greater than: >
- Less or equal: <=
- Greater or equal: >=

### Expressions
- Numbers: `42`
- Variables: `x`
- Arithmetic: `x + y`, `10 * 5`

## Usage

### Compile a single file

```bash
python3 src/uhigh.py source.uh
```

This will generate a `source.masm` file with the compiled MicroASM code.

### Build a project

```bash
python3 src/build.py examples
```

This will compile all .uh files in the `examples` directory and generate a single `output.masm` file.

## Example

```go
func main()
{
    var x
    x = 42
    print "The answer is:"
    print x
}
```
