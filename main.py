import functions as f
import os
import pathlib

# Get current working directory
cwd = os.getcwd()

print("""
                    ___,-----.___
                ,--'             `--.
               /                     \\
              /                       \\
             |                         |
            |                           |
            |        |~~~~~~~~~|        |
            |        \         /        |
             |        \       /        |
              \        \     /        /
               \        |   |        /
                \       |   |       /
                 \      |   |      /
                  \     |   |     /
                   \____|___| ___/
                   )___,-----'___(
                   )___,-----'___(
                   )___,-----'___(
                   )___,-----'___(
                   \_____________/
                        \___/

========================================================
|                                                      |
|   Welcome to our Electrictity Consumption Project    |
|                                                      |
|  --------------------------------------------------  |
|                                                      |
|                      Made by:                        |
| Johan Böcher Hanehøj, August Tollerup, Andreas Fiehn |
|                                                      |
========================================================
""")

tvec = None
data = None
data_loaded = False
tvec_a = None
data_a = None
data_aggregated = False
aggregated_by = None

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
    action = input("\nWhat do you wish to do?\n{}\n".format(
        "\n".join(options))).lower()

    if action == "1":

        while True:
            # Ask user for filename. Has to be in same directory as script
            filename = input("\nPlease enter the name of your data file (case sensitive).\nThe file must be in the same directory as the script.\nIf you wish to go back to the main menu enter \"back\"\n")

            # Go back to main menu
            if filename.lower() == "back":
                print("\nLoad data aborted. Data has not been loaded \n")
                break

            # Full file path
            file = cwd + "/" + filename

            # Check if it is a csv file
            if pathlib.Path(filename).suffix == ".csv":
                # Check if file exists
                if os.path.isfile(file):
                    # Enter loop to get fmode from user
                    while True:
                        # Options to pick from
                        fmode_options = [
                            "(1) Forward fill",
                            "(2) Backward fill",
                            "(3) Drop",
                            "(4) Back to main menu"
                        ]

                        # Ask for user input
                        fmode = input("\nHow would you like to handle corrupted data?\n{}\n".format(
                            "\n".join(fmode_options))).lower()

                        # Check input
                        if fmode in ["1", "2", "3"]:
                            # Define options
                            dict = {"1": "forward fill", "2": "backward fill", "3": "drop"}

                            tvec, data = f.load_measurements(filename, dict[fmode])
                            data_loaded = True

                            # Reset aggregated data when new data is loaded
                            data_aggregated = False
                            data_a = None
                            tvec_a = None

                            print("\nData was loaded succesfully!\n")
                            break
                        elif fmode == "4":
                            print("\nLoad data aborted. Data has not been loaded \n")
                            break
                        else:
                            print("\nPlease enter a valid way to handle corrupted data\n")
                            continue
                        # Data is saved. Break out of the loop
                        break
                else:
                    print("\nFile does not exist!\n")
                    continue
            else:
                print("\nPlease provide a .csv file\n")
                continue
            break
    elif action == "2":

        if not data_loaded:
            print("\nPlease load data first!\n")
        else:
            while True:
                agg_options = [
                "(1) Consumption per minute (no aggregation)",
                "(2) Consumption per hour",
                "(3) Consumption per day",
                "(4) Consumption per month",
                "(5) Hour-of-day consumption (hourly average)",
                "(6) Back to main menu"
                ]

                period = input("\nWhat period would you like to aggregate for \n{}\n".format("\n".join(agg_options)))

                # Aggregate by minute
                if period == "1":
                    # If aggregation "minute" is chosen data is not aggregated
                    tvec_a = tvec
                    data_a = data
                    aggregated_by  = "minute"
                    data_aggregated = True
                    print("\nAggregated by minute (No aggregation has been applied)\n")
                    break
                elif period in ["2", "3", "4", "4"]:
                    # Define options
                    dict = {"2": "hour", "3": "day", "4": "month", "5": "hour of the day"}

                    tvec_a, data_a = f.aggregate_measurements(tvec, data, dict[period])
                    aggregated_by = dict[period]
                    data_aggregated = True
                    print("\nData aggregated succesfully!\n")
                    break
                elif period == "6":
                    print("\nData has not been aggregated\n")
                    break
                else:
                    print("Please enter a valid aggregate option")
                    continue

    elif action == "3":
        if not data_loaded:
            print("\nPlease load data first!\n")
        else:
            if data_aggregated:
                print("\nConsumption per {} in watt-hour\n".format(aggregated_by))
                f.print_statistics(tvec_a, data_a)
            else:
                print("\nConsumption per minute in watt-hour\n")
                f.print_statistics(tvec, data)

    
    elif action == "4":
        if data_loaded:
            choice = input("Specify if you want the combined zones or particular ('all' or '1,2,3,4')\n")
            if choice.lower() == "all" or int(choice) in [1,2,3,4]:
                if data_aggregated:
                    f.visualize(data_a, choice, aggregated_by)
                else:
                    f.visualize(data, choice)
            else:
                print("\n Please specify a correct choice. \nWrite 'all' or the numerical zone: 1,2,3 or 4\n")
        else:
            print("\nPlease load data first!\n")

        
    elif action == "5":
        print("\nThank you for using our program :)")
        # Exit program
        exit()
    else:
        print("Please pick a valid option")
