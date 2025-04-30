import re
from typing import List, Tuple

Token = Tuple[str, str]

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.current = 0

    def tokenize(self) -> List[Token]:
        token_specification = [
            ('NEQ',      r'!='),     # Not equal
            ('EQ',       r'=='),    # Equal
            ('LE',       r'<='),    # Less than or equal
            ('GE',       r'>='),    # Greater than or equal
            ('LT',       r'<'),     # Less than
            ('GT',       r'>'),     # Greater than
            ('NUMBER',   r'\d+'),
            ('PRINT',    r'print'),  # Match 'print' first
            ('ASM',      r'asm'),     # Match 'asm' keyword
            ('IDENT',    r'[A-Za-z_]\w*'),  # Match identifiers after reserved keywords
            ('STRING',   r'"[^"]*"'),
            ('ASSIGN',   r'='),
            ('END',      r';'),
            ('LPAREN',   r'\('),     # Recognize '('
            ('RPAREN',   r'\)'),     # Recognize ')'
            ('LBRACE',   r'\{'),
            ('RBRACE',   r'\}'),
            ('COMMA',    r','),
            ('OP',       r'[+\-*/]'),
            ('COMMENT',  r'//.*|;.*'),  # Match comments
            ('NEWLINE',  r'\n'),
            ('SKIP',     r'[ \t]+'),
            ('MISMATCH', r'.'),      # Should match any other character
        ]
        tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
        get_token = re.compile(tok_regex).match
        line_num = 1
        line_start = 0
        mo = get_token(self.source)
        
        while mo is not None:
            kind = mo.lastgroup
            value = mo.group(kind)
            
            # Special handling for asm blocks
            if kind == 'ASM':
                # Look ahead for the LBRACE
                next_pos = mo.end()
                while next_pos < len(self.source):
                    ch = self.source[next_pos]
                    if not ch.isspace():
                        break
                    next_pos += 1
                
                # Add the ASM token
                self.tokens.append((kind, value))
                
                # If we find '{' immediately after 'asm', capture the entire block
                if next_pos < len(self.source) and self.source[next_pos] == '{':
                    # Manually add the LBRACE token
                    self.tokens.append(('LBRACE', '{'))
                    
                    # Start after the '{'
                    pos = next_pos + 1
                    
                    # Collect everything until the matching '}'
                    depth = 1
                    asm_text = ""
                    
                    while depth > 0 and pos < len(self.source):
                        char = self.source[pos]
                        if char == '{':
                            depth += 1
                        elif char == '}':
                            depth -= 1
                            if depth == 0:  # Don't include the closing brace in asm content
                                break
                        
                        if char == '\n':
                            line_num += 1
                        
                        if depth > 0:  # Only add content if we're still inside the block
                            asm_text += char
                        pos += 1
                    
                    if depth > 0:
                        raise RuntimeError(f'Unclosed assembly block starting at line {line_num}')
                    
                    # Add the assembly content as a single token
                    if asm_text:
                        self.tokens.append(('ASM_CONTENT', asm_text))
                    
                    # Add the closing brace
                    self.tokens.append(('RBRACE', '}'))
                    
                    # Update position and get next token
                    self.current = pos + 1
                    mo = get_token(self.source, self.current)
                    continue
            elif kind == 'NEWLINE':
                line_start = self.current
                line_num += 1
                # Skip newlines, don't add them as tokens
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value} unexpected on line {line_num}')
                
            if not (kind == 'SKIP' or kind == 'NEWLINE' or kind == 'COMMENT'):
                self.tokens.append((kind, value))
                
            self.current = mo.end()
            mo = get_token(self.source, self.current)
            
        
        # For debugging, print tokens
        if __debug__:
            print("Tokens:")
            for token in self.tokens:
                print(token)

        return self.tokens
