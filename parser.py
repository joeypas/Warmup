import pyparsing as pp

pp.ParserElement.enable_packrat()

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

grammar = (expr + pp.Optional(DETAIL("detail")) + pp.StringEnd())

# Changed the arrow for point of error testing so it doesn't have to
# Be a tuple or a unioned str and pp.ParseResults
def parse_query(text: str):
    # A try excpetion in order to catch invalid strings, returns True if valid parse happend and False if not
    try:
        return True, grammar.parse_string(text, parse_all=True)
    except pp.exceptions.ParseException as e:
        return False, str(e)
    
# To dictionary function using an Abstract Syntax Tree
# This has to work recursively as the depth of each item in the list
# Can change with each query
def build_dict(element):
    if not isinstance(element, pp.ParseResults):
        # This returns when it gets a number, string or field, ie accepted grammer
        return element
    
    # For Compound Operations (AND /OR) 
    # As pp.ParseResults behave like List's for len we can use that to determine the input
    if len(element) == 3 and element[1] in ("and", "or"):
        return {
            # Recursive call to see what's to the left and righ of the BO
            "Compound_Operator": element[1],
            "Left": build_dict(element[0]),
            "Right":build_dict(element[2])
        }
    
    # For Unary (Not)
    if len == 2 and element == "not":
        return {
            "Not_Predicate": "not",
            "Right": build_dict(element[1])
        }
    
    # For null field

    if len(element) == 3 and isinstance(element[0], str) and element[2] == None:
        return {
            "Field_name": element[0],
            "Operator": element[1],
            "Value": element[2],
    }

    # For is not null field

    if len(element) == 4 and isinstance(element[0], str) and element[3] == None:
        return {
            "Field_name": element[0],
            "Operator": "is not",
            "Value": None,
    }
    
    # For the predicates: [field, operator, value]
    if len(element) == 3 and isinstance(element[0], str):
        return {
            "Field_name": element[0],
            "Operator": element[1],
            "Value": element[2],
        }
    
    
    if len(element) == 1:
        return build_dict(element[0])
    
     # If nothing got parsed put it in an error part of the dict
    return {
        "Error Elements": [build_dict(e) for e in element]
    }
    
