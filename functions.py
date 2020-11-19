import pandas as pd
import numpy as np


def load_measurements(filename, fmode):
    """This function loads the data and processes the data based on user requests.

    input:
        filename (str): the name of the data file
        fmode (str): the requested data processing
    output:
        a tuple containing 2 pandas DataFrames: tvec (N x 6 matrix),data (N x 4 matrix)
    """

    # Load the data into a pandas DataFrame
    df = pd.read_csv(filename,header=None)

    df = df.rename(columns={0:'year',1:'month',2:'day',3:'hour',4:'min',5:'sec',6:'zone 1',7:'zone 2',8:'zone 3',9:'zone 4'})
    # Replace all -1 values with NaN
    df = df.replace(to_replace=-1, value=np.nan)

    # Process the data based on the users request
    if fmode == "forward fill":
        # Drop all corrupt rows if there is a NaN value in the first row
        if np.nan in df.iloc[0]:
            df = df.dropna()
        # Replace NaN values with the latest valid measurement
        else:
            df = df.ffill(axis=0)

    elif fmode == "backward fill":
        # Drop all corrupt rows if there is a NaN value in the last row
        if np.nan in df.iloc[-1]:
            df = df.dropna()
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

#print(load_measurements("2008.csv","drop"))



pd.set_option('display.max_rows', 100)


def aggregate_measurements(tvec, data, period):
    # Concatenate tvec and data
    df = pd.concat([tvec,data],axis=1)

    x = df.groupby("hour").agg('zone 1').sum()

    if period == 'hour':
        # Group by year, month, day and hour and aggregate the zone
        agg = df.groupby(['year', 'month', 'day', 'hour']).agg({'zone 1': 'sum', 'zone 2': 'sum','zone 3': 'sum','zone 4': 'sum'})
        data_a = agg.reset_index().iloc[:,-4:]
        tvec_a = tvec.drop_duplicates(subset = ['year', 'month', 'day', 'hour'])
    elif period == 'day':
        agg = df.groupby(['year', 'month', 'day']).agg({'zone 1': 'sum', 'zone 2': 'sum','zone 3': 'sum','zone 4': 'sum'})
        data_a = agg.reset_index().iloc[:,-4:]
        tvec_a = tvec.drop_duplicates(subset = ['year', 'month', 'day'])
    elif period == 'month':
        agg = df.groupby(['year', 'month']).agg({'zone 1': 'sum', 'zone 2': 'sum','zone 3': 'sum','zone 4': 'sum'})
        data_a = agg.reset_index().iloc[:,-4:]
        tvec_a = tvec.drop_duplicates(subset = ['year', 'month'])

    # print(x)
    return (tvec_a, data_a)

tvec, data = load_measurements("2008.csv","drop")
tvec_a, data_a =  aggregate_measurements(tvec,data,'day')
print(tvec_a)
print(data_a)

def print_statistics(tvec, data):

    return
