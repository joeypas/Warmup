# This file interacts with main to query firebase google cloud storage
import firebase_admin
from firebase_admin import credentials, firestore


# going to need a reference to the db in some way like this
cred = credentials.Certificate("many-markets-db-firebase-adminsdk-fbsvc-24a5086e09.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
markets_ref = db.collection("markets")

QUERY_OPERATORS = {
    '<':'<', # numeric fields only
    '<=':'<=', # numeric fields only
    '=': '==',
    '!=':'!=',
    '>':'>',  # numeric fields only
    '>=':'>=', # numeric fields only
    '?=': 'in' # Contains (text fields)
}

# I think a query can look something like this
# execution of query:
# docs = (
#     db.collection("markets")
#     .where(filter=FieldFilter(field[Field_Name], QUERY_OPERATORS[field[Operator]], field[Value]))
#     .stream()
# )


def get_single_query_ids(field: dict) -> set:
    """
    Returns a set of market ids for those that satisfy the query with
    the operator, the value, and the field.

    the field dict must have the following structure:
    {
       “Field_name”: str
       “Operator”: str
       “Value”: str
    }
    """
    # TODO Tristin, finish function that get the ids of markets that satisfy the query
    ids = set()

    return ids


def get_markets_by_ids(ids:set) -> list[dict]:
    """
    Returns a list of dictionaries, each representing a market from the set of market ids.
    """
    markets = []
    for id in ids:
        # link to getting a doc using get() https://firebase.google.com/docs/firestore/query-data/get-data
        doc = db.collection("markets").where("id", "==", id).get()[0]
        markets.append(doc.to_dict())
    return markets

def get_query(query_dict: dict) -> list:
    """
    Returns a list of dictionaries where each dictionary represents a market that satisfies the query dictionary fields

    The query_dict parameter must follow this format:
    {
        "Compound_Operator": "and" | "or" | None,
        "fields": [
            {
                "Field_name": str,
                "Operator": str,   # one of: >, <, =>, =<, =, !=, ?=
                "Value": the string or float field to be compared against
            },
            ...
        ]
    }
    Returns:
        A list of market dictionaries, where each market has:
        {
            "id": str,
            "question": str,
            "volume": float,
            "probability": float,
            "resolution": str | None
        }
    """

    fields = query_dict["fields"]
    compound_op = query_dict["Compound_Operator"]

    if compound_op == "and":
        # intersection
        id1 = set(get_single_query_ids(fields[0]))
        id2 = set(get_single_query_ids(fields[1]))
        ids = set.intersection(id1, id2)
    elif compound_op == "or":
        # union
        id1 = set(get_single_query_ids(fields[0]))
        id2 = set(get_single_query_ids(fields[1]))
        ids = set.union(id1, id2)
    else:
        # the set of ids
        ids = set(get_single_query_ids(fields))

    # get full market data from set of ids
    final_markets = get_markets_by_ids(ids)
    return final_markets
