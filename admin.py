from db import market_collection
import json
import sys

def delete_collection(coll_ref, batch_size):
    """
    Delete all documents in collection.
    This function if from firebase docs. Link to docs:
    https://firebase.google.com/docs/firestore/manage-data/delete-data#python
    """
    if batch_size == 0:
        return

    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

def main ():
    # credit to video resource https://www.youtube.com/watch?v=qsFYq_1BQdk
    # initialize using function
    db = market_collection()
    markets = db.collection("markets")

    # get the json file from command line
    json_file = sys.argv[1]

    with open(json_file, "r") as f:
        data = json.load(f)

    # clear the contents if there are any docs
    delete_collection(markets, 100)

    # add all markets from the json file
    for item in data:
        doc_ref = db.collection("markets").document()
        doc_ref.set(item)

if __name__ == "__main__":
    main()