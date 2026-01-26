# Prediction Market Query Grammar

## Fields
- market_id (string)
- question (string)
- volume (number)
- probability (number)
- resolution (enum | null)

## Tokens
\<string\> ::= '"'(any character)+'"'

\<number\> ::= integer | float

## Grammar
\<query\> ::= \<expr\> EOF

\<expr\> ::= \<or_expr\>

\<or_expr\> ::= \<and_expr\> | "or" \<or_expr\>

\<and_expr\> ::= \<not_expr\> | "and" \<and_expr\>

\<not_expr\> ::= [ "not" ] \<primary\>

\<primary\> ::= \<predicate\> | "(" \<expr\> ")"

\<predicate\> ::= \<field\> \<comparison_op\> \<value\>
              | \<field\> "?=" \<string\>
              | \<field\> "is" [ "not" ] "null"

\<field\> ::= "market_id" | "question" | "volume" | "probability" | "resolution"

\<value\> ::= \<number\> | \<string\> | \<resolution\> | "null"

\<resolution\> ::= "YES" | "NO" | "CANCEL"

# Examples
- volume > 1000
- probability <= 0.2 and resolution = NO
- question ~ "Snowpiercer" and (resolution = NO or resolution = CANCEL)
- resolution is null
- resolution is not null
- market_id = "TJsVEaHGVx8v2Z0D2slq"
        not (probability < 0.05)
