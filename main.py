# Start program loop
while True:
    # Options the user can pick from
    options = [
        "(1) Load data",
        "(2) Aggregate data",
        "(3) Display statistics",
        "(4) Visualize electricity consumption",
        "(5) Quit"
    ]

    # Get user input
    action = input("What do you wish to do?\n{}\n".format(
        "\n".join(options))).lower()

    if action == "1":

        print("NOT DONE: Load data")

    elif action == "2":
        print("NOT DONE: Aggregate data")
    elif action == "3":
        print("NOT DONE: Print statistics")
    elif action == "4":
        print("NOT DONE: Visualize data")
    elif action == "5":
        print("Thank you for using our program :)")
        # Exit program
        exit()
    else:
        print("Please pick a valid option")
