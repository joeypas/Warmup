import parser as par
from firebase import get_query
from db import market_collection

# Example of a valid query: 'question == "hello" and volume > 10'
# Example output [[[['question', '==', 'hello']], 'and', [['volume', '>', 10]]], 'detail']

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

# Validation of operators
def valid_dict(refined_dict : dict):
    valid = True
    if isinstance(refined_dict['fields'], dict):
        field = refined_dict['fields']['Field_name']
        operator = refined_dict['fields']['Operator']
        if field == 'volume' and operator == '?=':
            valid = False
        elif field == 'probability' and operator == '?=':
            valid = False
        elif field == 'question' and operator not in ['=', '?=']:
            valid = False
        elif field == 'id' and operator != ['=', '?=']:
            valid = False
    # For when there are multiple fields
    else:
        for fields in refined_dict['fields']:
            field = fields['Field_name']
            operator = fields['Operator']
            if field == 'volume' and operator == '?=':
                valid = False
            elif field == 'probability' and operator == '?=':
                valid = False
    return valid


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
            Welcome to our program about market prediction betting markets. 
            Example of a valid query: 'volume > 1000'
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
                # Create a dictionary to send over to the firebase.py program
                user_rough_query_dict = par.build_dict(user_input_parsed)
                user_refined_dict = dictionary_refiner(user_rough_query_dict)
        
                # User input validition for text and number fields
                if valid_dict(user_refined_dict):
                    returned_que = get_query(user_refined_dict, db)
                    # Need to add detail check
                    for query in returned_que:
                        """
                        If: detail print out the whole thing
                        else:
                        """
                        print(f">> id:{query['id']} | Question: {query['question']}")
                else:
                    print(">> Error! You inputted a text operator on a number field.")
                    print(">> Type help for instructions on proper querying.")

            
              


if __name__ == "__main__":
    main()
