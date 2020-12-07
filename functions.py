import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
pd.options.mode.chained_assignment = None  # chained assingment warning removed


def load_measurements(filename, fmode):
    """This function loads the data and processes the data based on user requests.
    Args:
        filename (str): the name of the data file
        fmode (str): the requested data processing
    Return:
        (tuple): a tuple containing 2 panda DataFrames: tvec (N x 6 matrix), data (N x 4 matrix)
    """

    # Load the data into a pandas DataFrame
    df = pd.read_csv(filename,header=None)

    df = df.rename(columns={0:'year',1:'month',2:'day',3:'hour',4:'minute',5:'second',6:'zone 1',7:'zone 2',8:'zone 3',9:'zone 4'})
    # Replace all -1 values with NaN
    df = df.replace(to_replace=-1, value=np.nan)

    # Process the data based on the users request
    if fmode == "forward fill":
        # Drop all corrupt rows if there is a NaN value in the first row
        if df.iloc[0].isnull().values.any():
            df = df.dropna()
            print("Warning! There is an invalid measurement in the first row of the file. " +
                  "All corrupt measurements have been dropped.")
        # Replace NaN values with the latest valid measurement
        else:
            df = df.ffill(axis=0)
            print("Random")

    elif fmode == "backward fill":
        # Drop all corrupt rows if there is a NaN value in the last row
        if df.iloc[-1].isnull().values.any():
            df = df.dropna()
            print("Warning! There is an invalid measurement in the last row of the file. " +
                  "All corrupt measurements have been dropped.")
        # Replace NaN values with the next valid measurement
        else:
            df = df.bfill(axis=0)

    elif fmode == "drop":
        # Drop all rows with corrupted measurements
        df = df.dropna()

    # Split the DataFrame into a N x 6 time-matrix and a N x 4 data-matrix
    tvec = df.iloc[:,:-4]
    data = df.iloc[:,-4:]

    #df1 = df[df.isna().any(axis=1)]
    #print(df1)

    return (tvec, data)

def aggregate_measurements(tvec, data, period):
    """
    This aggregates the data

    Args:
        tvec (pandas DataFrame object): N x 6 matrix. Each row is a time vector
        data (pandas DataFrame object): N x 4 matrix. Each row is a set of measurements
        period (Str): How to aggregate the data. By "hour", "day", "month" og "hour of the day"
    Return:
        tuple: Two panda DataFrame objects - tvec (N x 6 matrix) and data (N x 4 matrix) aggregated according to period
    """
    # Concatenate tvec and data
    df = pd.concat([tvec,data],axis=1)

    # Group by year, month, day and hour and aggregate the zones
    if period == 'hour':
        agg = df.groupby(['year', 'month', 'day', 'hour']).agg({'zone 1': 'sum', 'zone 2': 'sum','zone 3': 'sum','zone 4': 'sum'})
        data_a = agg.reset_index().iloc[:,-4:]
        tvec_a = tvec.drop_duplicates(subset = ['year', 'month', 'day', 'hour'])

        # Replace columns with 0 to make sure time starts at the beginning of the hour
        tvec_a.loc[:,["minute", "second"]] = 0

    elif period == 'day':
        agg = df.groupby(['year', 'month', 'day']).agg({'zone 1': 'sum', 'zone 2': 'sum','zone 3': 'sum','zone 4': 'sum'})
        data_a = agg.reset_index().iloc[:,-4:]
        tvec_a = tvec.drop_duplicates(subset = ['year', 'month', 'day'])

        # Replace columns with 0 to make sure time starts at the beginning of the day
        tvec_a.loc[:,["hour", "minute", "second"]] = 0

    elif period == 'month':
        agg = df.groupby(['year', 'month']).agg({'zone 1': 'sum', 'zone 2': 'sum','zone 3': 'sum','zone 4': 'sum'})
        data_a = agg.reset_index().iloc[:,-4:]
        tvec_a = tvec.drop_duplicates(subset = ['year', 'month'])

        # Replace columns with 0 to make sure time starts at the beginning of the month
        tvec_a.loc[:,["hour", "minute", "second"]] = 0

    elif period == "hour of the day":
        data_a = df.groupby('hour').agg({'zone 1': 'mean', 'zone 2': 'mean', 'zone 3': 'mean', 'zone 4': 'mean'})
        tvec_a = tvec.drop_duplicates(subset = ['hour'])

        # Replace columns with 0 to make sure time starts at the beginning of the hour
        tvec_a.loc[:,["minute", "second"]] = 0

    return (tvec_a, data_a)

def print_statistics(tvec, data):
    """
    Print statistics to screen

    Args:
        tvec (pandas DataFrame object): N x 6 matrix. Each row is a time vector
        data (pandas DataFrame object): N x 4 matrix. Each row is a set of measurements
    """
    data["All"] = data.sum(axis=1)
    table = data.describe().iloc[3:].T
    table = table.rename(columns={"index":"Zone", "minute":"Minimum", "25%":" 1. quart.",
                          "50%":" 2. quart.", "75%":" 3. quart.", "max":"Maximum"},
                         index={'zone 1':'1','zone 2':'2','zone 3':'3','zone 4':'4'})
    print(table)


def visualize(data, tvec, zones, unit, agg_by="minute"):

    """
        plot the consumption in each zone or the combined consumption (all zones).
        Display a plot with appropriate axes (time on the x-axis and consumption on the y-axis), labels,
        and a title.
        Use a bar chart if the aggregated data contains less than 25 measurements.

        Args:
            data (pandas DataFrame object): N x 4 matrix. Each row is a set of measurements
            zones (str): Desired zones to plots
            unit (str): Unit to display on plot y axis
            agg_by (str): The aggregation period for the data. Default False
    """

    # If aggregated by "hour of the day" dates contains from 0 to 23 hours
    if agg_by == "hour of the day":
        # dates = np.arange(0,24,1)
        dates = pd.Series(np.arange(0,24,1))
        is_datetime = False
    else:
        dates = pd.to_datetime(tvec)
        is_datetime = True

    date_locators = {"minute": md.MinuteLocator, "hour": md.HourLocator, "day": md.DayLocator, "month": md.MonthLocator}
    date_format = {"minute": '%Y-%m-%d %H:%M', "hour": '%Y-%m-%d %H:%M', "day": '%Y-%m-%d', "month": '%Y-%m', "hour of the day": '%H'}

    if len(dates) > 25:
        if zones == "all":
            fig_width = 10
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.suptitle('Plot of Power Consumption', fontsize=16)
            ax.plot(dates.to_numpy(),data["zone 1"].to_numpy()+data["zone 2"].to_numpy()+data["zone 3"].to_numpy()+data["zone 4"].to_numpy())

            ax.set_title("Combined Zones")
            ax.set_ylabel(unit)
            ax.set_xlabel("Minutes")
            if agg_by:
                ax.set_xlabel(agg_by)

            ax.set_ylim(0)

            # Format date according to the aggregation
            x_format = md.DateFormatter(date_format[agg_by])
            ax.xaxis.set_major_formatter(x_format)

            # Determine a proper tick frequency
            tick_frequency = len(dates) // 20
            # Get tick locator according to aggregation
            xtick_locator = date_locators[agg_by](interval=tick_frequency)
            # Set the locator
            ax.xaxis.set_major_locator(xtick_locator)

            for tick in ax.get_xticklabels():
                # Rotate ticks
                tick.set_rotation(60)
                # Align ticks
                tick.set_horizontalalignment('right')

        else:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, figsize=(10, 5))

            ax1.set_title("Zone 1")
            ax2.set_title("Zone 2")
            ax3.set_title("Zone 3")
            ax4.set_title("Zone 4")

            ax1.plot(dates.to_numpy(), data["zone 1"].to_numpy(), color=("blue"))
            ax2.plot(dates.to_numpy(), data["zone 2"].to_numpy(), color=("red"))
            ax3.plot(dates.to_numpy(), data["zone 3"].to_numpy(), color=("magenta"))
            ax4.plot(dates.to_numpy(), data["zone 4"].to_numpy(), color=("green"))

            # Get formatter according to aggregation
            x_format = md.DateFormatter(date_format[agg_by])

            # Determine a proper tick frequency
            tick_frequency = len(dates) // 10
            # Get tick locator according to aggregation
            xtick_locator = date_locators[agg_by](interval=tick_frequency)


            for ax in [ax1, ax2, ax3, ax4]:
                # Set labels
                ax.set_ylabel(unit)
                ax.set_xlabel(agg_by)

                ax.set_ylim(0)
                # Set formatter
                ax.xaxis.set_major_formatter(x_format)
                # Set the locator
                ax.xaxis.set_major_locator(xtick_locator)

                # Rotate and align ticks
                for tick in ax.get_xticklabels():
                    tick.set_rotation(45)
                    tick.set_horizontalalignment('right')

                ax.tick_params(labelsize=6)

    else:
        # There are less than 25 datapoints and we substitute the Graph plot with a Bar plot
        if zones == "all":
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.suptitle('Bar Plot of Power Consumption', fontsize=16)
            ax.set_ylabel(unit)
            ax.set_xlabel("Minutes")
            if agg_by:
                ax.set_xlabel(agg_by)

            ax.set_title("Combined Zones")

            ax.bar(dates.to_numpy(), data["zone 1"].to_numpy()+data["zone 2"].to_numpy()+data["zone 3"].to_numpy()+data["zone 4"].to_numpy())
            ax.set_xticks(dates)

            # Only format ticks if is datetime
            if is_datetime:
                # Format date according to the aggregation
                x_format = md.DateFormatter(date_format[agg_by])
                ax.xaxis.set_major_formatter(x_format)

                for tick in ax.get_xticklabels():
                    tick.set_rotation(45)
                    tick.set_horizontalalignment('right')

            ax.set_ylim(0)

        else:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, figsize=(10, 5))
            fig.suptitle('Bar Plot of Power Consumption', fontsize=16)

            ax1.set_title("Zone 1")
            ax2.set_title("Zone 2")
            ax3.set_title("Zone 3")
            ax4.set_title("Zone 4")

            ax1.bar(dates.to_numpy(), data["zone 1"].to_numpy(), color=("blue"))
            ax2.bar(dates.to_numpy(), data["zone 2"].to_numpy(), color=("red"))
            ax3.bar(dates.to_numpy(), data["zone 3"].to_numpy(), color=("magenta"))
            ax4.bar(dates.to_numpy(), data["zone 4"].to_numpy(), color=("green"))


            for ax in [ax1, ax2, ax3, ax4]:
                # Set labels
                ax.set_ylabel(unit)
                ax.set_xlabel(agg_by)

                # y limit
                ax.set_ylim(0)

                # Set tick
                ax.set_xticks(dates)

                # Only format ticks if is datetime
                if is_datetime:
                    # Format date according to the aggregation
                    x_format = md.DateFormatter(date_format[agg_by])
                    ax.xaxis.set_major_formatter(x_format)
                    # Rotate and align tick labels
                    for tick in ax.get_xticklabels():
                        tick.set_rotation(45)
                        tick.set_horizontalalignment('right')

                # Set tick label size
                ax.tick_params(labelsize=6)

    plt.tight_layout()
    plt.show()

    return None
