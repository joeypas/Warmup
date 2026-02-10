# This file interacts with main to query firebase google cloud storage
from google.cloud.firestore import Client
from google.cloud.firestore_v1 import FieldFilter

def get_single_query_ids(field: dict, db: Client) -> set:
    """
    returns a set of market id for the ones that satisfy the query with
    the operator, the value, and the field.
    """
    ids = set()

    field_name = field["Field_name"]
    operator = field["Operator"]
    value = field["Value"]

    # firestore  operators
    firestore_ops = {"<", "<=", "=", "!=", ">", ">="}

    # get markets_ref
    markets_ref = db.collection("markets")
    if operator in firestore_ops:
        # convert '=' to Firestore '=='
        fs_op = "==" if operator == "=" else operator

        docs = markets_ref.where(filter=FieldFilter(field_name, fs_op, value)).stream()
        for doc in docs:
            data = doc.to_dict()
            ids.add(data["id"])

    else:
        # fallback for operators firestore can't handle
        docs = markets_ref.stream()
        for doc in docs:
            data = doc.to_dict()
            field_value = data.get(field_name)

            if operator == "?=" and isinstance(field_value, str):
                if value.lower() in field_value.lower():
                    ids.add(data["id"])

            elif value == "empty":
                if operator == "=" and field_value is None:
                    ids.add(data["id"])
                elif operator == "!=" and field_value is not None:
                    ids.add(data["id"])

    return ids



def get_markets_by_ids(ids:set, db: Client) -> list[dict]:
    """
    Returns a list of dictionaries, each representing a market from the set of market ids.
    """
    markets = []
    for id in ids:
        # link to getting a doc using get() https://firebase.google.com/docs/firestore/query-data/get-data
        # also using filter=FieldFilter is updated way to query https://firebase.google.com/docs/firestore/query-data/queries
        doc = db.collection("markets").where(filter=FieldFilter("id", "==", id)).get()[0]
        markets.append(doc.to_dict())
    return markets

def get_query(query_dict: dict, db: Client) -> list[dict]:
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
        id1 = set(get_single_query_ids(fields[0], db))
        id2 = set(get_single_query_ids(fields[1], db))
        ids = set.intersection(id1, id2)
    elif compound_op == "or":
        # union
        id1 = set(get_single_query_ids(fields[0], db))
        id2 = set(get_single_query_ids(fields[1], db))
        ids = set.union(id1, id2)
    else:
        # the set of ids
        ids = set(get_single_query_ids(fields, db))

    # get full market data from set of ids
    final_markets = get_markets_by_ids(ids, db)
    return final_markets
