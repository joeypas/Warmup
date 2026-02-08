import parser as par
# Example of a valid query: 'question == "hello" and volume > 10'
# Example output [[[['question', '==', 'hello']], 'and', [['volume', '>', 10]]], 'detail']

# Refines the rough dictionary into usable date for the firebase
# NEED TO FIX DETAIL
def dictionary_refiner(unrf_dict : dict):
    refined_dict = {}
    # First see if theres a compound so we know we have to send two fields
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
    # Funciton to determine if we need to exit the program
    running = True
    while running:
        user_input_unparsed = input(">> ")
        # First check to see if they asked for the help function
        if user_input_unparsed.lower() == "help":
            # Needs to be correctly typed out, just a place holder
            help_text = """
            Welcome to our program about market prediction bets.
            ADD MORE IN GREATER DETAIL LATER
            Example of a valid query: 'question == "hello" and volume > 10'
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
                # print(user_refined_dict)
                # TO BE IMPLEMENTED ON FRIDAY
                returned_que = get_query(user_refined_dict)

                # Need to add detail check
                for query in returned_que:
                    """
                    If: detail print out the whole thing
                    else:
                    """
                    print(f"id:{query['id']} | Question: {query['question']}")


if __name__ == "__main__":
    main()
