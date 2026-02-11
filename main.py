import parser as par
from firebase import get_query
from db import market_collection
from tabulate import tabulate

# Example of a valid query: 'question == "hello" and volume > 10'
# Example output [[[['question', '==', 'hello']], 'and', [['volume', '>', 10]]], 'detail']

ORDER = ["id", "question", "volume", "probability", "resolution"]

def order_dicts(responses):
    return [{k: r.get(k) for k in ORDER} for r in responses]

def detail_view(responses):
    return tabulate(responses, headers="keys", maxcolwidths=[None, 40, None, None], tablefmt="grid")


# Refines the rough dictionary into usable date for the firebase
def dictionary_refiner(unrf_dict : dict):
    refined_dict = {}
    # First see if there's a compound so we know we have to send two fields
    if 'Compound_Operator' in unrf_dict:
        refined_dict['Compound_Operator'] = unrf_dict['Compound_Operator']
        left_dict = unrf_dict['Left']
        right_dict = unrf_dict['Right']
        refined_dict['fields'] = [unrf_dict['Left'], right_dict]
    else:
        refined_dict['Compound_Operator'] = None
        refined_dict['fields'] = unrf_dict
    return refined_dict


def main():
    # one db connection for all queries
    db = market_collection()
    # Function to determine if we need to exit the program
    running = True
    while running:
        user_input_unparsed = input(">> ")
        # First check to see if they asked for the help function
        if user_input_unparsed.lower() == "help":
            # Needs to be correctly typed out, just a placeholder
            help_text = """
            Welcome to our program about market prediction betting markets. To query the program you can use
            one or two of the following valid fields (you can join two queries with an 'and' or an 'or'):
                id (string)
                question (string)
                volume (number)
                probability (number)
                resolution (enum | null)

            Ways to query fields:
                > : Greater than (numeric fields only)
                < : Less than (numeric fields only)
                => : Greater than or equal (numeric fields only)
                =< : Less than or equal (numeric fields only)
                =: Equal to 
                ?= Contains (text fields only)
                != Not equal to 

            Example of a valid queries:
                resolution is not null
                resolution is null 
                probability > 0.5
                question ?= “will”
                volume < 1000
                id = “TJsVEaHGVx8v2Z0D2slq”
                id != “TJsVEaHGVx8v2Z0D2slq”
                probability > 0.5 and question ?= “will”
            
            Make sure if your value is a string for a field i.e the “TJsVEaHGVx8v2Z0D2slq” in id = “TJsVEaHGVx8v2Z0D2slq”,
            you must put it between double quotes. 
            
            In order to exit the program simply type 'exit'!
            """
            print(help_text)
        elif user_input_unparsed.lower() == "exit":
            running = False
        else:
            # Parse the query from our parser
            success, user_input_parsed = par.parse_query(user_input_unparsed)


            # First see if the user input is valid
            if not success:
                print(">> Invalid query! Type 'help' to see how to input a valid query")
                print(f">> Error: {user_input_parsed}")
            else:
                # Does the user want a detail view?
                detail_requested = user_input_parsed['detail']

                user_refined_dict = dictionary_refiner(user_input_parsed['ast'])

                # User input validition for text and number fields
                returned_que = order_dicts(get_query(user_refined_dict, db))
                # Need to add detail check
                if detail_requested:
                    print(detail_view(returned_que))
                else:
                    for query in returned_que:
                        """
                        If: detail print out the whole thing
                        else:
                        """
                        print(f">> id:{query['id']} | Question: {query['question']}")


if __name__ == "__main__":
    main()
