import pyparsing as pp

pp.ParserElement.enable_packrat()

# Some AST types

def ast_pred(field, op, value):
    return {"Field_name": field, "Operator": op, "Value": value}

def ast_not(node):
    return {"Not_Predicate": "not", "Right": node}

def ast_bin(op, left, right):
    return {"Compound_Operator": op.lower(), "Left": left, "Right": right}

# BASIC PARSERS

LPAREN, RPAREN = pp.Suppress.using_each("()")

# Keywords
# Added an optional Keyword called "detail"
AND, OR, NOT, IS, NULL, DETAIL = pp.CaselessKeyword("and"), pp.CaselessKeyword("or"), pp.CaselessKeyword("not"), pp.CaselessKeyword("is"), pp.CaselessKeyword("null"), pp.CaselessKeyword("detail")

# Resolutions
YES, NO, CANCEL = pp.CaselessKeyword.using_each(("YES", "NO", "CANCEL"))

# Fields
MARKET_ID, QUESTION, VOLUME, PROBABILITY, RESOLUTION = pp.Keyword.using_each(("market_id", "question", "volume", "probability", "resolution"))

field = (MARKET_ID | QUESTION | VOLUME | PROBABILITY | RESOLUTION)

# Values
number = pp.common.number()

string = pp.dbl_quoted_string().set_parse_action(pp.remove_quotes)

null = NULL.copy().set_parse_action(pp.replace_with(None))


value = (number | string).set_name("value")("value")

# Operators
comparison = pp.one_of("== != >= <= < >", as_keyword=False)

contains = pp.Literal("?=")

# COMPLEX PARSERS

# Predicates

# field <op> value
comparison_pred = pp.Group(field + comparison + value).set_parse_action(
    # create an ast_pred dict
    lambda t: ast_pred(t[0][0], t[0][1], t[0][2])
)

# field '?=' "substring"
contains_pred = pp.Group(field + contains + value).set_parse_action(
    # create an ast_pred dict but set the operator
    lambda t: ast_pred(t[0][0], "?=", t[0][2])
)

# field is [not]
is_null_pred = pp.Group(field + IS + pp.Optional(NOT("negated")) + null).set_parse_action(
    lambda t: ast_pred(
        t[0][0],
        "is not" if len(t[0]) == 4 else "is",
        None
    )
)

predicate = (is_null_pred | contains_pred | comparison_pred)

# Expressions (THIS IS BROKEN)

expr = pp.Forward()

primary = (predicate | pp.Group(LPAREN + expr + RPAREN))

def parse_action_not(t):
    toks = t[0]
    if len(toks) == 2 and str(toks[0]).lower() == "not":
        return ast_not(toks[1])
    return toks[0]

def parse_action_bin(t):
    toks = t[0]
    node = toks[0]
    i = 1
    while i < len(toks):
        op = toks[i]
        rhs = toks[i + 1]
        node = ast_bin(op, node, rhs)
        i += 2
    return node

not_expr = pp.Group(pp.Optional(NOT("not_")) + primary)

expr <<= pp.infix_notation(
    base_expr=primary,
    op_list=[
        (NOT, 1, pp.opAssoc.RIGHT, parse_action_not),
        (AND, 2, pp.opAssoc.LEFT, parse_action_bin),
        (OR, 2, pp.opAssoc.LEFT, parse_action_bin),
    ],
)

grammar = (expr("ast") + pp.Optional(DETAIL("detail")) + pp.StringEnd())

# Changed the arrow for point of error testing so it doesn't have to
# Be a tuple or a unioned str and pp.ParseResults
def parse_query(text: str):
    # A try excpetion in order to catch invalid strings, returns True if valid parse happend and False if not
    try:
        pr = grammar.parse_string(text, parse_all=True)
        # detail field states if user requested detail view
        # ast field is the actual dictionary
        return True, {
            "detail": bool(pr.detail),
            "ast": pr.ast,
        }
    except pp.exceptions.ParseException as e:
        return False, str(e)
