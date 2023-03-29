import pandas as pd
import os

# Load range data from Download and Base Stations stored in the RANGE.CSV files
def mn_range_loader(path, is_ds=True):
    ''''
    Range data load and parse
    
    Params:
    ------
    path:  str  : directory of the RANGE.CSV file
    is_ds: bool : specify is the data comes from Dowload Station (default True) or Base Station (change to False)

    Usage:
    ------
    >>> from dulogpy import mn_range_loader
    >>> mn_range_loader('file path', is_ds=True) 
    ''' 
    if is_ds == True:
        df = pd.read_csv(path, usecols=[0,1,2,3,4,5,6,7,9], 
                         parse_dates={'datetime':['year','month','day','hour','minute','second']})
    # Load data from BS --> is_ds=False
    else:
        df = pd.read_csv(path, usecols=[0,1,2,3,4,5,6,7],
                         parse_dates={'datetime':['year','month','day','hour','minute','second']})

    # Parse datetime
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y %m %d %H %M %S')

    # Set 'Node ID' as string
    df['Node ID'] = df['Node ID'].astype('string')
    
    # Set datetime colum as index
    df.set_index('datetime', drop=True, inplace=True)
    df.sort_index(ascending=True, inplace = True)

    return df

# Load proximity data stored in the MN_DATA.CSV files
def mn_data_loader(path):
    ''''
    Proximity data load and parse

    Params:
    ------
    path: str  : directory of the MN_DATA.CSV file

    Usage:
    ------
    >>> from dulogpy import mn_data_loader
    >>> mn_data_loader('file path')
    '''

    # Load data selecting columns and columns to be parsed as datetime
    cols = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    df = pd.read_csv(path, usecols= cols, parse_dates={'datetime':[0,1,2,3,4,5], 'datetime_received':[9,10,11,12,13,14]})

    # Parse datetime
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y %m %d %H %M %S')
    df['datetime_received'] = pd.to_datetime(df['datetime_received'], format='%Y %m %d %H %M %S')
    
    # Transform 'RX Node' and 'TX Node' as strings (they are not really numbers)
    df['RX Node'] = df['RX Node'].astype('string')
    df['TX Node'] = df['TX Node'].astype('string')
    
    # Drop potential duplicates
    df.drop_duplicates(subset=['RX Node', 'TX Node','datetime'], inplace=True)
    
    # Select columns and arrange them
    df = df[['datetime', 'RX Node', 'TX Node', 'RSSI', 'datetime_received', 'Received RSSI']]
    
    # Set 'datetime' of the logging event as index and sort it
    df.set_index('datetime', drop=True, inplace=True)
    df.sort_index(ascending=True, inplace = True)
    
    return df

# Elimination of proximit data redundancy between dyads
def no_redundancy(df, Node1, Node2, start=None, end=None):
    '''
    Eliminates redundacy of the proximity data of a specified dyad.

    Params:
    ------
    df   : DataFrame previously loaded and parsed with the mn_data_loader function
    Node1: str : First individual from a dyad
    Node2: str : Second individual from a dyad
    start: str : Datetime in the format 'YYYY-MM-DD HH:MM:SS' indicates the start of the observation time window : default value None
    end  : str : Datetime in the format 'YYYY-MM-DD HH:MM:SS' indicates the end of the observation time window   : default value None

    Usage:
    ------
    >>> from dulogpy import no_redundancy
    >>> no_redundancy(df, 'Node1', 'Node2', start=None, end=None)
    '''

    # Split the DataFrame with proximity data per RX Node
    df_node1 = df.loc[(df['RX Node']==Node1)&(df['TX Node']==Node2)][start:end]
    df_node2 = df.loc[(df['RX Node']==Node2)&(df['TX Node']==Node1)][start:end]
    
    # Merge data frames using datetime index
    df_n1_n2 = df_node1.merge(df_node2[['TX Node', 'RSSI']], left_index = True, right_index = True, 
            how='outer', suffixes=(f'_{Node1}', f'_{Node2}'))
    
    # Fill NaNs values
    df_n1_n2.loc[df_n1_n2['RX Node'].isna(), 'RX Node'] = Node2
    df_n1_n2.loc[df_n1_n2[f'TX Node_{Node1}'].isna(), f'TX Node_{Node1}'] = Node1
    df_n1_n2.loc[df_n1_n2[f'TX Node_{Node2}'].isna(), f'TX Node_{Node2}'] = Node2
    
    # Filling missing RSSI values
    df_n1_n2[f'RSSI_{Node1}'] = df_n1_n2[f'RSSI_{Node1}'].where(~df_n1_n2[f'RSSI_{Node1}'].isna(), df_n1_n2[f'RSSI_{Node2}'])
    df_n1_n2[f'RSSI_{Node2}'] = df_n1_n2[f'RSSI_{Node2}'].where(~df_n1_n2[f'RSSI_{Node2}'].isna(), df_n1_n2[f'RSSI_{Node1}'])
    
    # Get maximum RSSI value from the interaction of the nodes
    df_n1_n2['RSSI_max'] = df_n1_n2[[f'RSSI_{Node1}',f'RSSI_{Node2}']].max(axis=1)
    
    # Select and rename columns
    df_noredundancy = df_n1_n2[['RX Node', f'TX Node_{Node1}', 'RSSI_max']]
    df_noredundancy = df_noredundancy.rename(columns={f'TX Node_{Node1}':'TX Node'})
    
    # Add column indicating the pair of interacting nodes.
    df_noredundancy['dyad'] = f'{Node1}-{Node2}'
    
    return df_noredundancy

# Save output DataFrames
def save_csv(df, name='new_file', index=True):
    '''
    Save the files into .csv format ready to use with R

    Params:
    ------
    df   : DataFrame output from loading and parsing functions (mn_range_loader, mn_data_loader, no_redundancy)
    name : str  : name of the new file to be saved into your working directory
    index: bool : specify if the index should be saved as a column : default value True recommended for R users
    '''
    wd = os.getcwd()
    return df.to_csv(wd+'/'+name+'.csv', index=index)