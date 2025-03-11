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
            ('NUMBER',   r'\d+'),
            ('IDENT',    r'[A-Za-z_]\w*'),
            ('STRING',   r'"[^"]*"'),
            ('ASSIGN',   r'='),
            ('END',      r';'),
            ('LPAREN',   r'\('),
            ('RPAREN',   r'\)'),
            ('LBRACE',   r'\{'),
            ('RBRACE',   r'\}'),
            ('COMMA',    r','),
            ('OP',       r'[+\-*/]'),
            ('NEWLINE',  r'\n'),
            ('SKIP',     r'[ \t]+'),
            ('MISMATCH', r'.'),
        ]
        tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
        get_token = re.compile(tok_regex).match
        line_num = 1
        line_start = 0
        mo = get_token(self.source)
        while mo is not None:
            kind = mo.lastgroup
            value = mo.group(kind)
            if kind == 'NEWLINE':
                line_start = self.current
                line_num += 1
            elif kind == 'SKIP':
                pass
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpected on line {line_num}')
            else:
                self.tokens.append((kind, value))
            self.current = mo.end()
            mo = get_token(self.source, self.current)
        return self.tokens
