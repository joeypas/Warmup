import pyparsing as pp

pp.ParserElement.enable_packrat()

# BASIC PARSERS

LPAREN, RPAREN = pp.Suppress.using_each("()")

# Keywords
AND, OR, NOT, IS, NULL = pp.CaselessKeyword(" and "), pp.CaselessKeyword(" or "), pp.CaselessKeyword("not"), pp.CaselessKeyword("is"), pp.CaselessKeyword("null")

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
comparison_pred = pp.Group(field + comparison + value)

# field '?=' "substring"
contains_pred = pp.Group(field + contains + value)

# field is [not]
is_null_pred = pp.Group(field + IS + pp.Optional(NOT("negated")) + null)

predicate = (is_null_pred | contains_pred | comparison_pred)

# Expressions (THIS IS BROKEN)

expr = pp.Forward()

primary = (predicate | pp.Group(LPAREN + expr + RPAREN)("group"))

not_expr = pp.Group(pp.Optional(NOT("not_")) + primary)

expr <<= pp.infix_notation(
    base_expr=not_expr,
    op_list=[
        (AND, 2, pp.opAssoc.LEFT),
        (OR, 2, pp.opAssoc.LEFT),
    ],
)

grammar = (expr + pp.StringEnd())

def parse_query(text: str) -> pp.ParseResults:
    return grammar.parse_string(text, parse_all=True)

