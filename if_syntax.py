from symbols import Symbol, Symbol_Type, Epsilon

Goal = Symbol('Goal', Symbol_Type.NONTERMINAL)
Stmt = Symbol('Stmt', Symbol_Type.NONTERMINAL)

Ifthen = Symbol('ifthen', Symbol_Type.TERMINAL)
Else = Symbol('else', Symbol_Type.TERMINAL)
Assign = Symbol('assign', Symbol_Type.TERMINAL)