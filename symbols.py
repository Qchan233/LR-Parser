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

class Action(Enum):
    SHIFT = 0
    REDUCE = 1
    ACCEPT = 2

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
        return frozenset(s)
    
    def goto(self, s, x):
        for item in s:
            assert isinstance(item, LR_Entry), 'item should be a LR_Entry'
        assert isinstance(x, Symbol), 'x should be a Symbol'
        t = set()
        for item in s:
            right = item.right 
            if right and right[0] == x:
                beta = list(item.left)
                beta_x = beta + [right[0]]
                new_item = LR_Entry(item.symbol, tuple(beta_x), item.right[1:], item.lookahead)
                t.add(new_item)

        return self.closure(t)
    
    def build_collection(self):
        initial_rule = self.rules[0] 
        intial_entry = LR_Entry(initial_rule[0], (), tuple(initial_rule[1]), Eof)

        cc0 = self.closure({intial_entry})
        CC = {cc0}
        state_lst = [cc0]
        state2idx = {cc0: 0}
        
        unmarked = {cc0} 
        changed = True
        transitions = {}
        while changed:
            changed = False
            for cc in unmarked.copy():
                unmarked.remove(cc)
                for entry in cc:
                    right = entry.right
                    if not right:
                        continue
                    x = right[0]
                    tmp = self.goto(cc, x)
                    if tmp not in CC:
                        changed = True
                        idx = len(CC)
                        CC.add(tmp)
                        state2idx[tmp] = idx 
                        state_lst.append(tmp)
                        unmarked.add(tmp)
                    
                    transitions[(state2idx[cc], x)] = idx
                    
        return state_lst, state2idx, transitions

    def build_table(self):
        states, state2idx, transitions = self.build_collection()
        self.lr_states = states
        action_table = {}
        goto_table = {}

        for state in states:
            state_idx = state2idx[state]
            for entry in state:
                if entry.right:
                    x = entry.right[0]
                    if x.symbol_type == Symbol_Type.TERMINAL:
                        j = transitions[(state_idx, x)]
                        action_table[(state_idx, x)] = (Action.SHIFT, j)
                elif entry.symbol == Goal and entry.lookahead == Eof:
                    action_table[(state_idx, Eof)] = (Action.ACCEPT, None)
                else:
                    a = entry.lookahead
                    action_table[(state_idx, a)] = (Action.REDUCE, entry)

            
            for symbol in self.nonterminals:
                if (state_idx, symbol) in transitions:
                    goto_table[(state_idx, symbol)] = transitions[(state_idx, symbol)]

        return action_table, goto_table
    

    def visualiz_table(self, action_table, goto_table):
        n_state = len(self.lr_states)
        action_table_lst = [[None] * len(self.symbols) for _ in range(n_state + 1)]
        print('State:', end='\t')
        terminals = [Eof] + self.terminals
        for symbol in terminals:
            if symbol == Epsilon:
                continue
            print(symbol, end='\t')
        print()
        for i in range(n_state):
            print(i, end='\t')
            for j, symbol in enumerate(terminals):
                if symbol == Epsilon:
                    continue
                if (i, symbol) in action_table:
                    action, val = action_table[(i, symbol)]
                    if action == Action.SHIFT:
                        action_table_lst[i][j] = f's{val}'
                    elif action == Action.REDUCE:
                        # action_table_lst[i][j] = f'r{Syntax.entry_str(val, skip_lookahead=True)}'
                        action_table_lst[i][j] = f'r '
                    elif action == Action.ACCEPT:
                        action_table_lst[i][j] = 'acc'
                else:
                    action_table_lst[i][j] = ' '
                print(action_table_lst[i][j], end='\t')
            print()



    @classmethod
    def entry_str(cls, entry: LR_Entry, skip_lookahead=False):
        sym = entry.symbol
        left = entry.left
        right = entry.right

        left_str = ' '.join([str(symbol) for symbol in left])
        right_str = ' '.join([str(symbol) for symbol in right])

        lookahead = entry.lookahead
        if skip_lookahead:
            return f'[{sym} -> {left_str}]'
        else:
            return f'[{sym} -> {left_str}·{right_str}, {lookahead}]'
    
    @classmethod
    def show_set(cls, s):
        for item in s:
            print(cls.entry_str(item))
    
if __name__ == '__main__':
    # import everything from expr_grammar.py
    from paren_syntax import *
    syntax = Syntax(syms, rules)
    # syntax.show_first_set()
    # initial_entry = LR_Entry(Goal, (), (List,), Eof)
    # cc0 = syntax.closure({LR_Entry(Goal, (), (List,), Eof)})
    # print('CC0:------------------')
    # Syntax.show_set(cc0)
    # cc1 = syntax.goto(cc0, List)
    # print('CC1:------------------')
    # Syntax.show_set(cc1)
    # cc2 = syntax.goto(cc0, Pair)
    # print('CC2:------------------')
    # Syntax.show_set(cc2)

    # state_lst, _, transitions = syntax.build_collection()
    # for state in state_lst:
    #     print('------------------')
    #     print(len(state))
    #     Syntax.show_set(state)
    # print(len(transitions))
    # print(transitions)

    action_table, goto_table =  syntax.build_table()
    # syntax.visualiz_table(action_table, goto_table)
    syntax.visualiz_table(action_table, goto_table)