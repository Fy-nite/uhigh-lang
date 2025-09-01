from typing import List, Union, Tuple
from lexer import Lexer, Token

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

class VarDecl(ASTNode):
    def __init__(self, name: str, initial_value: Union[str, int] = None):
        self.name = name
        self.initial_value = initial_value

class ConstDecl(ASTNode):
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

class Assignment(ASTNode):
    def __init__(self, name: str, value: Union[str, int]):
        self.name = name
        self.value = value

class Print(ASTNode):
    def __init__(self, values):
        self.values = values

class IfStatement(ASTNode):
    def __init__(self, condition: ASTNode, true_block: List[ASTNode], false_block: List[ASTNode] = None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block

class WhileStatement(ASTNode):
    def __init__(self, condition: ASTNode, body: List[ASTNode]):
        self.condition = condition
        self.body = body

class FuncDecl(ASTNode):
    def __init__(self, name: str, parameters: List[str], body: List[ASTNode]):
        self.name = name
        self.parameters = parameters
        self.body = body

class FuncCall(ASTNode):
    def __init__(self, name: str, args: List[Union[str, int]] = None):
        self.name = name
        self.args = args or []

class Include(ASTNode):
    def __init__(self, filename: str):
        self.filename = filename

class InlineAsm(ASTNode):
    def __init__(self, code: str):
        self.code = code

class Parser:
    def __init__(self, tokens: List[Token], debug: bool = False):
        self.tokens = tokens
        self.current = 0
        self.debug = debug
        self.declared_vars = set()  # Track declared variables

    def parse(self) -> Program:
        statements = []
        while self.current < len(self.tokens):
            statements.append(self.statement())
        for stmt in statements:
            if isinstance(stmt, InlineAsm):
                print(f"Inline ASM detected: {stmt.code}")
        # Print the final AST for debugging
        if self.debug:
            print("\nFinal AST:")
        def print_ast(node, level=0):
            indent = "  " * level
            if isinstance(node, list):
                for item in node:
                    print_ast(item, level)
                return

            if isinstance(node, (str, int)):
                if self.debug:
                    print(f"{indent}{node}")
                return

            node_type = node.__class__.__name__
            attrs = {}

            for k, v in node.__dict__.items():
                if isinstance(v, list):
                    if self.debug:
                        print(f"{indent}{node_type}.{k}:")
                    for item in v:
                        print_ast(item, level + 1)
                elif isinstance(v, ASTNode):
                    if self.debug:
                        print(f"{indent}{node_type}.{k}:")
                    print_ast(v, level + 1)
                else:
                    attrs[k] = v             

            if attrs and self.debug:
                print(f"{indent}{node_type}: {attrs}")

        for stmt in statements:
            print_ast(stmt)
        return Program(statements)

    def statement(self) -> ASTNode:
        token = self.tokens[self.current]
        if token[0] == 'IDENT' and token[1] == 'include':
            return self.include_stmt()
        elif token[0] == 'IDENT' and token[1] == 'var':
            return self.var_decl()
        elif token[0] == 'IDENT' and token[1] == 'const':
            return self.const_decl()
        elif token[0] == 'PRINT':  # Handle the PRINT token directly
            return self.print_stmt()
        elif token[0] == 'IDENT' and token[1] == 'if':
            return self.if_stmt()
        elif token[0] == 'IDENT' and token[1] == 'while':
            return self.while_stmt()
        elif token[0] == 'IDENT' and token[1] == 'func':
            return self.func_decl()
        elif token[0] == 'ASM':  # <-- Changed from IDENT to ASM
            return self.inline_asm_stmt()
        elif token[0] == 'IDENT':
            return self.assignment_or_func_call()
        else:
            raise RuntimeError(f'Unexpected token: {token}')

    def include_stmt(self) -> Include:
        self.consume('IDENT', 'include')
        filename = self.consume('STRING')
        return Include(filename)

    def var_decl(self) -> VarDecl:
        self.consume('IDENT', 'var')
        name = self.consume('IDENT')
        self.declared_vars.add(name)
        if self.match('ASSIGN'):
            self.consume('ASSIGN')
            initial_value = self.expression()
            return VarDecl(name, initial_value)
        return VarDecl(name)

    def const_decl(self) -> ConstDecl:
        self.consume('IDENT', 'const')
        name = self.consume('IDENT')
        self.consume('ASSIGN')
        value = int(self.consume('NUMBER'))
        return ConstDecl(name, value)

    def print_stmt(self) -> Print:
        self.consume('PRINT')
        self.consume('LPAREN')
        args = [self.expression()]
        while self.current < len(self.tokens) and self.tokens[self.current][0] == 'COMMA':
            self.consume('COMMA')
            args.append(self.expression())
        self.consume('RPAREN')
        return Print(args)

    def if_stmt(self) -> IfStatement:
        self.consume('IDENT', 'if')
        condition = self.expression()
        self.consume('LBRACE')
        true_block = self.block()
        false_block = []
        if self.match('IDENT', 'else'):
            self.consume('IDENT', 'else')
            self.consume('LBRACE')
            false_block = self.block()
        return IfStatement(condition, true_block, false_block)

    def while_stmt(self) -> WhileStatement:
        self.consume('IDENT', 'while')
        condition = self.expression()
        self.consume('LBRACE')
        body = self.block()
        return WhileStatement(condition, body)

    def func_decl(self) -> FuncDecl:
        self.consume('IDENT', 'func')
        name = self.consume('IDENT')
        self.consume('LPAREN')
        parameters = []
        if not self.match('RPAREN'):
            parameters.append(self.consume('IDENT'))
            while self.match('COMMA'):
                self.consume('COMMA')
                parameters.append(self.consume('IDENT'))
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = self.block()
        return FuncDecl(name, parameters, body)

    def inline_asm_stmt(self) -> InlineAsm:
        # Print current token for debugging
        print(f"Current token in inline_asm_stmt: {self.tokens[self.current]}")
        
        # Consume the ASM token
        self.consume('ASM')  
        
        # Print next token for debugging
        print(f"Next token after ASM: {self.tokens[self.current]}")
        
        # Consume the LBRACE token
        self.consume('LBRACE')
        
        # Check for ASM_CONTENT token
        if self.match('ASM_CONTENT'):
            asm_code = self.consume('ASM_CONTENT')
        else:
            asm_code = ""
            
        # Consume the RBRACE token
        self.consume('RBRACE')
        
        return InlineAsm(asm_code)

    def assignment_or_func_call(self) -> Union[Assignment, FuncCall]:
        name = self.consume('IDENT')
        if self.match('ASSIGN'):
            if name not in self.declared_vars:
                raise RuntimeError(f"Variable '{name}' used before declaration.")
            self.consume('ASSIGN')
            value = self.expression()
            return Assignment(name, value)
        elif self.match('LPAREN'):
            self.consume('LPAREN')
            args = []
            if not self.match('RPAREN'):
                args.append(self.expression())
                while self.match('COMMA'):
                    self.consume('COMMA')
                    args.append(self.expression())
            self.consume('RPAREN')
            return FuncCall(name, args)
        else:
            raise RuntimeError(f'Unexpected token after identifier: {self.tokens[self.current]}')

    def block(self) -> List[ASTNode]:
        statements = []
        while not self.match('RBRACE'):
            # Skip any leftover NEWLINE tokens (shouldn't happen with fixed lexer)
            if self.current < len(self.tokens) and self.tokens[self.current][0] == 'NEWLINE':
                self.current += 1
                continue
                
            if self.current >= len(self.tokens):
                raise RuntimeError('Unexpected end of file while parsing block')
                
            statements.append(self.statement())
        self.consume('RBRACE')
        return statements

    def expression(self) -> Union[str, int]:
        # Support binary expressions: left op right
        token = self.tokens[self.current]
        # Handle left operand
        if token[0] == 'NUMBER':
            left = self.consume('NUMBER')
        elif token[0] == 'STRING':
            left = self.consume('STRING')
        elif token[0] == 'IDENT':
            var_name = self.consume('IDENT')
            if var_name not in self.declared_vars:
                raise RuntimeError(f"Variable '{var_name}' used before declaration.")
            left = var_name
        else:
            raise RuntimeError(f'Unexpected token in expression: {token}')

        # Check for binary operator (comparison or arithmetic)
        if self.current < len(self.tokens):
            op_token = self.tokens[self.current]
            if op_token[0] in ('EQ', 'NEQ', 'LE', 'GE', 'LT', 'GT', 'OP'):
                op = self.consume(op_token[0])
                # Right operand
                right_token = self.tokens[self.current]
                if right_token[0] == 'NUMBER':
                    right = self.consume('NUMBER')
                elif right_token[0] == 'STRING':
                    right = self.consume('STRING')
                elif right_token[0] == 'IDENT':
                    var_name = self.consume('IDENT')
                    if var_name not in self.declared_vars:
                        raise RuntimeError(f"Variable '{var_name}' used before declaration.")
                    right = var_name
                else:
                    raise RuntimeError(f'Unexpected token in binary expression: {right_token}')
                # Return as a string for the compiler to parse
                return f"{left} {op} {right}"

        # If not a binary expression, return the single value
        return left

    def consume(self, expected_type: str, expected_value: str = None) -> str:
        token = self.tokens[self.current]
        if token[0] != expected_type or (expected_value and token[1] != expected_value):
            raise RuntimeError(f'Expected {expected_type} {expected_value}, got {token}')
        self.current += 1
        return token[1]

    def match(self, expected_type: str, expected_value: str = None) -> bool:
        if self.current >= len(self.tokens):
            return False
        token = self.tokens[self.current]
        return token[0] == expected_type and (expected_value is None or token[1] == expected_value)
