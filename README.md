# μHigh Programming Language

μHigh is a simple high-level programming language that compiles to MicroASM.

## Table of Contents
- [Features](#features)
- [Getting Started](#getting-started)
- [Syntax](#syntax)
  - [Constants](#constants)
  - [Variables](#variables)
  - [Assignment](#assignment)
  - [Print](#print)
  - [Input](#input)
  - [Control Flow](#control-flow)
  - [Functions](#functions)
  - [Include](#include)
  - [Conditions](#conditions)
  - [Expressions](#expressions)
- [Usage](#usage)
- [Examples](#examples)
- [μHigh vs MicroASM](#μhigh-vs-microasm)

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

## Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://git.carsoncoder.com/charlie-san/uhigh-lang
   cd uhigh-lang
   ```

2. Make sure you have Python 3 installed:
   ```bash
   python3 --version
   ```

3. You're ready to create and compile μHigh programs!

### Your First μHigh Program

Create a file named `hello.uh`:

```go
func main() {
    print "Hello, μHigh!"
}
```

Compile and run it:

```bash
python3 src/uhigh.py hello.uh
# This creates hello.masm which you can run with your MicroASM interpreter
```

usualy people will use the J-masm interpreter to run the generated MicroASM code.

you can get J-masm from [here](https://git.carsoncoder.com/finite/jmasm)


## Syntax

### Constants

Define values that cannot be changed:

```go
const PI 3.14159
const MAX_COUNT 100
```

### Variables

Declare variables that can store values:

```go
var counter
var result
```

### Assignment

Assign values to variables:

```go
counter = 1
result = counter + 41
```

### Print

Print strings or expressions:

```go
print("Hello, World!")
print(result)
```

### Input

Read input from the user:

```go
input counter
```

### Control Flow

Conditional statements and loops:

```go
if counter == 1 {
    print "Counter is one"
} else {
    print "Counter is not one"
}

while counter < 10 {
    print counter
    counter = counter + 1
}
```

### Functions

Define reusable code blocks:

```go
func add(a, b) {
    return a + b
}

func main() {
    var sum
    sum = add(10, 20)
    print sum
}
```

### Include

Include other μHigh files:

```go
include "utils.uh"
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

## Examples

### Basic Example

```go
func main() {
    var x
    x = 42
    print "The answer is:"
    print x
}
```

### Input and Output Example

```go
func main() {
    var name
    print "Enter your name:"
    input name
    print "Hello, " + name + "!"
}
```

## μHigh vs MicroASM

μHigh provides a higher level of abstraction compared to MicroASM, making it easier to write and understand code. Here are some benefits:

- **Readability**: μHigh code is more readable and concise.
- **Ease of Use**: μHigh simplifies common programming tasks.
- **Maintainability**: μHigh code is easier to maintain and modify.

MicroASM, on the other hand, is a lower-level language that provides more control over hardware but requires more effort to write and understand.

though µhigh exists to provide benefits of high level programming languages, it's not a full replacement and should be used within a mixed context with MicroASM to provide the best of both worlds.