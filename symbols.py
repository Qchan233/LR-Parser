from enum import Enum
from collections import namedtuple

class Symbol_Type(Enum):
    TERMINAL = 0
    NONTERMINAL = 1
    EOF = 2

LR_Entry = namedtuple('LR_Entry', ['symbol', 'left', 'right', 'lookahead'])

class Symbol:
    def __init__(self, name, symbol_type: Symbol_Type):
        self.name = name
        self.symbol_type = symbol_type
    
    def __str__(self) -> str:
        return self.name

Epsilon = Symbol('ε', Symbol_Type.TERMINAL)
Eof = Symbol('EOF', Symbol_Type.EOF)

class Syntax:
    def __init__(self, symbols, rules)-> None:
        self.symbols = symbols
        self.terminals = [symbol for symbol in symbols if symbol.symbol_type == Symbol_Type.TERMINAL]
        self.nonterminals = [symbol for symbol in symbols if symbol.symbol_type == Symbol_Type.NONTERMINAL]

        self.rules = rules
        self._build_rule_dict(rules)
        self.first_set = self._compute_first_set()
    
    def _build_rule_dict(self, rules):
        self.rule_dict = {}
        for rule_id, rule in rules.items():
            nonterminal = rule[0]
            if nonterminal not in self.rule_dict:
                self.rule_dict[nonterminal] = []
            self.rule_dict[nonterminal].append(rule)

    def _first_set_of_list(self, s, first_set):
        assert len(s) > 0, 'rule should not be empty'
        rhs = first_set[s[0]] - {Epsilon}
        trailing = True

        last_symbol_id = len(s) - 1

        for i in range(last_symbol_id):
            if Epsilon in first_set[s[i]]:
                rhs |= (first_set[s[i+1]] - {Epsilon})
            else:
                trailing = False
                break
        
        if trailing and Epsilon in first_set[s[last_symbol_id]]:
            rhs.add(Epsilon)
        
        return rhs
    
    def _compute_first_set(self):
        first_set = {}
        for terminal in self.terminals:
            first_set[terminal] = {terminal}
        for nonterminal in self.nonterminals:
            first_set[nonterminal] = set()
        first_set[Eof] = {Eof}

        changed = True

        while changed:
            changed = False
            for rule in self.rules.values():
                nonterminal = rule[0]
                expansion = rule[1]
                rhs = self._first_set_of_list(expansion, first_set)
                
                updated_set = first_set[nonterminal] | rhs
                if updated_set != first_set[nonterminal]:
                    first_set[nonterminal] = updated_set
                    changed = True
        
        return first_set
    
    def get_first_set(self, s):
        # if s is a list
        if isinstance(s, list):
            return self._first_set_of_list(s, self.first_set)
        
        return self.first_set[s]

    def show_first_set(self):
        for symbol, first_set in self.first_set.items():
            # if first_set is empty, set name to be {}
            names = [str(s) for s in first_set] or ['{}']
            print(f'First( {symbol} ) = {names}')
    
    def closure(self, s):
        assert isinstance(s, set), 's should be a set'
        for item in s:
            assert isinstance(item, tuple), 'item should be a tuple'
        changed = True
        while changed:
            changed = False
            for item in s.copy():
                lookahead = item.lookahead
                right = item.right
                if len(right) == 0 or right[0].symbol_type == Symbol_Type.TERMINAL:
                    continue
                # A -> β·Cδ, a
                C = right[0]
                delta = list(right[1:])
                delta.append(lookahead)
                first_set = self.get_first_set(delta)
                for rule in self.rule_dict[C]:
                    for b in first_set:
                        new_item = LR_Entry(rule[0], (), tuple(rule[1]), b)
                        if new_item not in s:
                            s.add(new_item)
                            changed = True
        return s
    
    @classmethod
    def entry_str(cls, entry: LR_Entry):
        sym = entry.symbol
        left = entry.left
        right = entry.right

        left_str = ' '.join([str(symbol) for symbol in left])
        right_str = ' '.join([str(symbol) for symbol in right])

        lookahead = entry.lookahead
        return f'[{sym} -> {left_str}·{right_str}, {lookahead}]'
    

if __name__ == '__main__':
    # import everything from expr_grammar.py
    from paren_syntax import *
    syntax = Syntax(syms, rules)
    # syntax.show_first_set()
    initial_entry = LR_Entry(Goal, (), (List,), Eof)
    cc0 = syntax.closure({LR_Entry(Goal, (), (List,), Eof)})
    for item in cc0:
        print(Syntax.entry_str(item))