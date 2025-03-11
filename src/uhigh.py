#!/usr/bin/env python3

import sys
import re
import os
from typing import List, Dict

class UHighCompiler:
    def __init__(self):
        self.variables: Dict[str, int] = {}
        self.label_counter: int = 0
        self.current_reg: int = 0
        self.string_counter: int = 0
        self.strings: Dict[str, int] = {}
        self.output: List[str] = []
        self.next_mem_addr = 100  # Start at memory address 100
        self.const_variables: Dict[str, bool] = {}  # Track constant variables
        self.in_loop = False
        self.current_loop_start = None
        self.current_loop_end = None
        self.loop_stack = []  # For nested loops
        self.block_stack = []  # Track all blocks (if/while)
        self.current_block_end = None
        self.header_added = False  # Track if header is added
        
    def get_next_reg(self) -> str:
        reg = f"R{self.current_reg}"
        self.current_reg += 1
        if self.current_reg > 14:  # Keep space for R15 as temp
            self.current_reg = 0
        return reg
    
    def get_next_label(self) -> str:
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def get_string_address(self, string: str) -> int:
        if string not in self.strings:
            self.strings[string] = self.next_mem_addr
            self.next_mem_addr += 1
        return self.strings[string]

    def compile_line(self, line: str, base_dir: str, line_num: int) -> List[str]:
        line = line.strip()
        if not line or line.startswith("//"):
            return []

        # Include other .uh files
        if line.startswith("include "):
            filename = line.split()[1].strip('"')
            include_path = os.path.join(base_dir, filename)
            with open(include_path, 'r') as f:
                included_source = f.read()
            return self.compile(included_source, base_dir).split('\n')

        # Constant declaration
        if line.startswith("const "):
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Invalid constant declaration. Expected 'const NAME VALUE', got: {line}")
            _, var_name, value = parts
            if var_name in self.variables:
                raise ValueError(f"Variable already declared: {var_name}")
            if not value.isdigit():
                raise ValueError(f"Constant value must be a number, got: {value}")
            self.variables[var_name] = len(self.variables)
            self.const_variables[var_name] = True
            return [f"MOV R{self.variables[var_name]} {value}"]

        # Variable declaration
        if line.startswith("var "):
            var_name = line.split()[1]
            self.variables[var_name] = len(self.variables)
            return []

        # Input statement
        if line.startswith("input "):
            var_name = line.split()[1]
            if var_name not in self.variables:
                raise ValueError(f"Undefined variable: {var_name}")
            if var_name in self.const_variables:
                raise ValueError(f"Cannot modify constant: {var_name}")
            return [
                "CALL #readint",  # Assumes stdio.io provides this
                f"MOV R{self.variables[var_name]} RAX"  # Convention: readint returns in RAX
            ]

        # Print statement
        if line.startswith("print "):
            content = line[6:].strip()
            if content.startswith('"') and content.endswith('"'):
                # String literal
                string_content = content[1:-1]
                addr = self.get_string_address(string_content)
                return [
                    f"MOV RAX 1",
                    f"MOV RBX ${addr}",
                    f"CALL #printf"
                ]
            else:
                # Variable or expression
                reg = self.compile_expression(content)
                return [
                    f"MOV RAX 1",
                    f"MOV RBX {reg}",
                    f"CALL #printint"
                ]

        # If statement
        if line.startswith("if "):
            condition = line[3:].split("{")[0].strip()
            end_label = self.get_next_label()
            else_label = self.get_next_label()
            self.block_stack.append(("if", else_label, end_label))
            condition_code = self.compile_condition(condition, else_label)
            return condition_code + [f"JMP #{end_label}", f"LBL #{else_label}"]

        # Else statement
        if line.startswith("else"):
            if not self.block_stack or self.block_stack[-1][0] != "if":
                raise ValueError(f"Unexpected 'else' without matching 'if' on line {line_num}: {line}")
            _, else_label, end_label = self.block_stack.pop()
            self.block_stack.append(("else", else_label, end_label))
            return [f"JMP #{end_label}", f"LBL #{else_label}"]

        # While loop
        if line.startswith("while "):
            condition = line[6:].split("{")[0].strip()
            start_label = self.get_next_label()
            end_label = self.get_next_label()
            
            # Save current loop context if we're already in a loop
            if self.in_loop:
                self.loop_stack.append((self.current_loop_start, self.current_loop_end))
                
            self.in_loop = True
            self.current_loop_start = start_label
            self.current_loop_end = end_label
            
            self.block_stack.append(("while", start_label, end_label))
            return [
                f"LBL #{start_label}",
                *self.compile_condition(condition, end_label)
            ]

        # End of block
        if line == "}":
            if not self.block_stack:
                return []
                
            block_type, start_or_skip, end = self.block_stack.pop()
            
            if block_type == "while":
                return [
                    f"JMP #{start_or_skip}",  # Jump back to start
                    f"LBL #{end}"             # End label
                ]
            else:  # if block or else block
                return [f"LBL #{end}"]

        # Function declaration
        if line.startswith("func "):
            func_name = line.split()[1].split("(")[0]
            return [f"LBL #{func_name}"]

        # Function call
        if "(" in line and ")" in line and not line.startswith(("if", "while")):
            func_name = line.split("(")[0].strip()
            return [f"CALL #{func_name}"]

        # Return statement
        if line == "return":
            return ["RET"]
        if line == "halt":
            return ["HLT"]
        # Assignment
        if "=" in line:
            var_name, expr = line.split("=", 1)
            var_name = var_name.strip()
            if var_name not in self.variables:
                raise ValueError(f"Undefined variable: {var_name}")
            
            expr_value = expr.strip()
            dest_reg = f"R{self.variables[var_name]}"
            
            if expr_value.isdigit():
                return [f"MOV {dest_reg} {expr_value}"]
            elif expr_value.startswith('"') and expr_value.endswith('"'):
                # String assignment
                addr = self.get_string_address(expr_value[1:-1])
                return [f"MOV {dest_reg} ${addr}"]
            else:
                result_reg = self.compile_expression(expr_value)
                if result_reg != dest_reg:  # Only generate MOV if registers are different
                    return [f"MOV {dest_reg} {result_reg}"]
                return []

        raise ValueError(f"Invalid syntax: {line}")

    def compile_condition(self, condition: str, false_label: str) -> List[str]:
        ops = {
            "==": "JNE",
            "!=": "JE",
            "<": "JGE",
            ">": "JLE",
            "<=": "JG",
            ">=": "JL"
        }
        
        for op in ops:
            if op in condition:
                left, right = [x.strip() for x in condition.split(op)]
                
                # Check if both sides are strings or variables containing strings
                if (left.startswith('"') and right.startswith('"')) or (left in self.variables and right.startswith('"')):
                    left_addr = self.get_string_address(left[1:-1]) if left.startswith('"') else f"R{self.variables[left]}"
                    right_addr = self.get_string_address(right[1:-1]) if right.startswith('"') else f"R{self.variables[right]}"
                    return [
                        f"MNI StringOperations.cmp {left_addr} {right_addr}",
                        f"{ops[op]} #{false_label}"
                    ]
                
                # Clear temporary instructions
                saved_output = self.output
                self.output = []
                
                # Compile both sides
                left_reg = self.compile_expression(left)
                left_instrs = self.output
                
                self.output = []
                right_reg = self.compile_expression(right)
                right_instrs = self.output
                
                # Restore output and return compiled condition
                self.output = saved_output
                
                return [
                    *left_instrs,
                    *right_instrs,
                    f"CMP {left_reg} {right_reg}",
                    f"{ops[op]} #{false_label}"
                ]
        
        raise ValueError(f"Invalid condition: {condition}")

    def compile_expression(self, expr: str) -> str:
        expr = expr.strip()
        
        # Simple variable, constant, or number
        if expr.isdigit():
            reg = self.get_next_reg()
            self.output.append(f"MOV {reg} {expr}")
            return reg
            
        if expr in self.variables:
            reg = self.get_next_reg()
            self.output.append(f"MOV {reg} R{self.variables[expr]}")
            return reg

        if expr in self.const_variables:
            return f"R{self.variables[expr]}"

        # Basic arithmetic
        ops = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
        for op in ops:
            if op in expr:
                left, right = [x.strip() for x in expr.split(op, 1)]
                left_reg = self.compile_expression(left)
                right_reg = self.compile_expression(right)
                result_reg = self.get_next_reg()
                if left_reg != result_reg:
                    self.output.append(f"MOV {result_reg} {left_reg}")
                self.output.append(f"{ops[op]} {result_reg} {right_reg}")
                return result_reg

        raise ValueError(f"Invalid expression: {expr}")

    def compile(self, source: str, base_dir: str = '.') -> str:
        result = []
        
        if not self.header_added:
            result.extend([
                "// Generated by μHigh Compiler",
                '#include "stdio.io"',
                ""
            ])
            self.header_added = True
        
        # First pass: collect all strings
        string_definitions = []
        for line in source.split('\n'):
            if 'print' in line and '"' in line:
                start = line.find('"') + 1
                end = line.rfind('"')
                if start > 0 and end > start:
                    string_content = line[start:end]
                    addr = self.get_string_address(string_content)
                    string_definitions.append(f'DB ${addr} "{string_content}"')

        # Second pass: compile code
        current_instructions = []
        for line_num, line in enumerate(source.split('\n'), start=1):
            try:
                compiled = self.compile_line(line, base_dir, line_num)
                for instr in compiled:
                    if instr.startswith("LBL"):
                        current_instructions.append(instr)
                    elif instr.startswith("CALL"):
                        current_instructions.append(f"    {instr}")
                    elif instr.startswith("MOV") or instr.startswith("RET") or instr.startswith("HLT"):
                        current_instructions.append(f"        {instr}")
                    else:
                        current_instructions.append(instr)
            except ValueError as e:
                print(f"Error on line {line_num}: {line}\n{e}", file=sys.stderr)
                sys.exit(1)

        result.extend(string_definitions)
        result.append("")  # Empty line after string definitions
        result.extend(current_instructions)
        result.append("")  # Empty line at the end
        return '\n'.join(result)

def main():
    if len(sys.argv) != 2:
        print("Usage: uhigh.py <source_file>")
        sys.exit(1)

    source_file = sys.argv[1]
    base_dir = os.path.dirname(source_file)

    with open(source_file, 'r') as f:
        source = f.read()

    compiler = UHighCompiler()
    output = compiler.compile(source, base_dir)
    
    output_file = source_file.replace('.uh', '.masm')
    with open(output_file, 'w') as f:
        f.write(output)

if __name__ == "__main__":
    main()
