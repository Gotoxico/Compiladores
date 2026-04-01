from dataclasses import dataclass
from typing import Optional

@dataclass
class Symbol:
    id: int
    name: str
    type: Optional[str] = None
    category: Optional[str] = None
    value: Optional[str] = None
    passed_as: Optional[str] = None
    used: bool = False
    lexical_level: int = 0
    scope: Optional[str] = None



class SymbolTable:
    def __init__(self):
        self.symbols = []
        self.current_level = 0
        self.scope_stack = ["global"]
        self.counter = 1

    def enter_scope(self, scope_name):
        self.current_level += 1
        self.scope_stack.append(scope_name)

    def exit_scope(self):
        self.current_level -= 1
        self.scope_stack.pop()

    def current_scope(self):
        return self.scope_stack[-1]

    def insert(self, name, type=None, category=None, value=None, passed_as=None):

        symbol = Symbol(
            id=self.counter,
            name=name,
            type=type,
            category=category,
            value=value,
            passed_as=passed_as,
            lexical_level=self.current_level,
            scope=self.current_scope()
        )

        self.symbols.append(symbol)
        self.counter += 1

        return symbol
    
    def lookup_current_scope(self, name):
        for symbol in reversed(self.symbols):
            if (symbol.name == name and 
                symbol.lexical_level == self.current_level):
                return symbol
        return None

    def mark_used(self, name):

        symbol = self.lookup(name)

        if symbol:
            symbol.used = True

    def print_table(self):

        print("ID | símbolo | tipo | categoria | valor | passada | usada | nível | escopo")

        for s in self.symbols:
            print(s.id, s.name, s.type, s.category, s.value, s.passed_as, s.used, s.lexical_level, s.scope)
