import functions as f
import os
import pathlib

# Get current working directory
cwd = os.getcwd()


tvec = None
data = None
data_loaded = False
tvec_a = None
data_a = None
data_aggregated = False

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
            filename = input("\nPlease enter the name of your data file. The file must be in the same directory as the script (case sensitive)\n")

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
            agg_options = [
            "(1) Consumption per minute (no aggregation)",
            "(2) Consumption per hour",
            "(3) Consumption per day",
            "(4) Consumption per month",
            "(5) Hour-of-day consumption (hourly average)"
            ]

            period = input("\nWhat period would you like to aggregate for \n{}\n".format("\n".join(agg_options)))

            if period == "1":
                print("NOT DONE: Consumption per minute (no aggregation)")
            elif period == "2":
                tvec_a, data_a = f.aggregate_measurements(tvec, data, "hour")
                data_aggregated = True
            elif period == "3":
                tvec_a, data_a = f.aggregate_measurements(tvec, data, "day")
                data_aggregated = True
            elif period == "4":
                tvec_a, data_a = f.aggregate_measurements(tvec, data, "month")
                data_aggregated = True
            elif period == "5":
                tvec_a, data_a = f.aggregate_measurements(tvec, data, "hour of the day")
                data_aggregated = True
            else:
                print("Please enter a valid aggregate option")

    elif action == "3":
        if not data_loaded:
            print("\nPlease load data first!\n")
        else:
            if data_aggregated:
                f.print_statistics(tvec_a, data_a)
            else:
                f.print_statistics(tvec, data)
    elif action == "4":
        print("NOT DONE: Visualize data")
    elif action == "5":
        print("\nThank you for using our program :)")
        # Exit program
        exit()
    else:
        print("Please pick a valid option")
