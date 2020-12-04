import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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


def visualize(data, tvec, zones, unit, agg_by=False):

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
    dates = pd.to_datetime(tvec)

    if len(dates) > 25:
        if zones == "all":
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.suptitle('Plot of Power Consumption', fontsize=16)
            ax.plot(dates.to_numpy(),data["zone 1"].to_numpy()+data["zone 2"].to_numpy()+data["zone 3"].to_numpy()+data["zone 4"].to_numpy())

            ax.set_ylabel(unit)
            ax.set_xlabel("Minutes")
            if agg_by:
                ax.set_xlabel(agg_by)

            start, end = ax.get_xlim()
            ax.set_ylim(0)
            ax.xaxis.set_ticks(np.arange(start, end, 30))
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)

        else:
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.suptitle('Plot of Power Consumption', fontsize=16)
            ax.plot(dates.to_numpy(), data["zone {}".format(int(zones))])
            start, end = ax.get_xlim()
            ax.set_ylabel(unit)
            ax.set_ylim(0)
            ax.set_xlabel("Minutes")
            if agg_by:
                ax.set_xlabel(agg_by)
            ax.xaxis.set_ticks(np.arange(start, end, 30))
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)

    else:
        # TODO: The bar plots needs a x-value which is unknown in this instance..
        if zones == "all":
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_ylabel(unit)
            ax.set_xlabel("Minutes")
            if agg_by:
                ax.set_xlabel(agg_by)
            start, end = ax.get_xlim()
            ax.bar(dates.to_numpy(), data["zone 1"].to_numpy()+data["zone 2"].to_numpy()+data["zone 3"].to_numpy()+data["zone 4"].to_numpy(),
                    color=("blue", "black", "green", "red"))
            ax.set_ylim(0)
            ax.set_xticks(dates)
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)

        else:
            plt.bar(dates, data["zone {}".format(int(zones))])

    plt.tight_layout()
    plt.show()

    return None
