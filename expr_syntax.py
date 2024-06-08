from symbols import Symbol, Symbol_Type, Epsilon

Goal = Symbol('Goal', Symbol_Type.NONTERMINAL)
Expr = Symbol('Expr', Symbol_Type.NONTERMINAL)
Expr_ = Symbol('Expr_', Symbol_Type.NONTERMINAL)

Term = Symbol('Term', Symbol_Type.NONTERMINAL)
Term_ = Symbol('Term_', Symbol_Type.NONTERMINAL)
Factor = Symbol('Factor', Symbol_Type.NONTERMINAL)

Plus = Symbol('+', Symbol_Type.TERMINAL)
Minus = Symbol('-', Symbol_Type.TERMINAL)
Mult = Symbol('*', Symbol_Type.TERMINAL)
Div = Symbol('/', Symbol_Type.TERMINAL)
L_Paren = Symbol('(', Symbol_Type.TERMINAL) 
R_Paren = Symbol(')', Symbol_Type.TERMINAL)

Name = Symbol('name', Symbol_Type.TERMINAL)
Num = Symbol('num', Symbol_Type.TERMINAL)


syms = [Goal, Expr, Expr_, Term, Term_, Factor, Plus, Minus, Mult, Div, L_Paren, R_Paren, Epsilon, Name, Num]

rules = {
    0 : (Goal, (Expr,)),
    1 : (Expr, (Term, Expr_)),
    2 : (Expr_, (Plus, Term, Expr_)),
    3 : (Expr_, (Minus, Term, Expr_)),
    4 : (Expr_, (Epsilon,)),
    5 : (Term, (Factor, Term_)),
    6 : (Term_, (Mult, Factor, Term_)),
    7 : (Term_, (Div, Factor, Term_)),
    8 : (Term_, (Epsilon,)),
    9 : (Factor, (L_Paren, Expr, R_Paren)),
    10 : (Factor, (Num,)),
    11 : (Factor, (Name,))
}