def read_source(mode: str, content: str):
    mode = mode.lower()

    if mode == 'file':
        with open(content, 'r', encoding='utf-8') as f:
            return f.read()

    elif mode == 'sequence':
        return content

    else:
        raise ValueError("Opcao Invalida")
    


import re
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    col_start: int
    col_end: int


token_specification = [
    ('nReal',  r'\d+\.\d+'),
    ('nInt',   r'\d+'),
    ('aP',     r'\('),
    ('fP',     r'\)'),
    ('opSoma', r'\+'),
    ('opSub',  r'-'),
    ('opMul',  r'\*'),
    ('opDiv',  r'/'),
    ('NEWLINE', r'\n'),
    ('TAB',   r'[ \t]+'),
    ('MISMATCH', r'.'),
]

# Cria uma lista de or`s (lógicos) para iterar sobre. Exemplo: ?P(<nInt>\d+) | ?P(<nReal>\d+\.\d+) ...
tok_regex = '|'.join(
    f'(?P<{name}>{pattern})'
    for name, pattern in token_specification
)

def lexico(sequence):
    line_num = 1
    line_start = 0

    for match in re.finditer(tok_regex, sequence):
        kind = match.lastgroup
        lexeme = match.group()
        start = match.start()
        end = match.end()

        if kind == 'NEWLINE':
            line_num += 1
            line_start = end
            continue

        if kind == 'TAB':
            continue

        if kind == 'MISMATCH':
            raise RuntimeError(
                f'Caractere fora do alfabeto "{lexeme}" na linha {line_num}'
            )

        col_start = start - line_start + 1
        col_end = end - line_start

        yield Token(kind, lexeme, line_num, col_start, col_end)

''' Kauan Loche, just if u wanna see how it should be called
if __name__ == "__main__":
    content = read_source("sequence", "123 + 123 \n123 *12 \t")
    results = list(lexico(content))

    for tk in results:
        print(
                f"Tipo: {tk.type:<8} | "
                f"Lexema: {tk.lexeme:<6} | "
                f"Linha: {tk.line:<3} | "
                f"Coluna Inicial: {tk.col_start:<3} | "
                f"Coluna Final: {tk.col_end}"
            )
'''
