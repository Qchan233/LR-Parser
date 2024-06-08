from symbols import Symbol, Symbol_Type, Epsilon

Goal = Symbol('Goal', Symbol_Type.NONTERMINAL)
List = Symbol('List', Symbol_Type.NONTERMINAL)
Pair = Symbol('Pair', Symbol_Type.NONTERMINAL)

L_Paren = Symbol('(', Symbol_Type.TERMINAL)
R_Paren = Symbol(')', Symbol_Type.TERMINAL)

syms = [Goal, List, Pair, L_Paren, R_Paren, Epsilon]

rules = {
    0 : (Goal, (List,)),
    1 : (List, (List, Pair)),
    2 : (List, (Pair,)),
    3 : (Pair, (L_Paren, List, R_Paren)),
    4 : (Pair, (L_Paren, R_Paren))
}