```
Pkg: dulogpy
Purpose: Handle data retrived by the duolog bio-logging system (e.g. range and proximity data)
Author: Dr. Jesus R. Hernández Montero
Contact: jesus.hdezmontero@gmail.com
Last uptade: 2023.03.30
```

# dulogpy

This is a package with functions for handling files retrived by [dulog](https://dulog.net/). Dulog is a bio-logging system based on wireless sensors developed by [Niklas Duda](https://orcid.org/0000-0001-7846-353X). This bio-loging system delivers interactions among components in terms of proximity between them.

## Dulog components
The dulog bio-logging system has the following components (please refer to the developer's manual to read the details about each component):
* Ground Nodes
    * Base Station (BS)
    * Download Station (DS)
* Mobile Nodes (MN)
* Stationary Nodes (SN)

## Retrived data
The data retrived can be categorized into:

* **Range data**: this data is delivered by GN and indicates the detection of a mobile or stationary node within its detectin range. The tables are saved in the files named `"RANGE.CSV"`. BS as well DS deliver this data but tables have subtle differences.

* **Proximity data**: this data indicates the interaction between MN-MN, MN-SN and SN-SN. Both ground nodes can save this data in the file `"MN_DATA.CSV"`. This data have redundancy.

# `dulogpy` functions
The functions provide in this package are for loading the data (Range and Proximity)into your local environment ready to use for analysis. The functions are the following

### **`mn_range_loader()`**
This function is for load range data delivered by the BS and DS. The functions does the following:

1. Parse datetime columns
2. Transform datatypes
3. Sort records chronologically
4. Sets the date and time as an index

**Function arguments**:
* `path`: is the directory of the file where the "RANGE.CSV" file is stored.
* `is_ds`: indicates if the files comes from a Download Station or not. The default is `True`. If you are loading range data from a Base Station this parameter should be set `False`.

### **`mn_data_loader()`**
This function is for loading the proximity data delivered by ground nodes. The function does the following:

1. Parse datetime columns.
2. Transform datatypes.
3. Handle potential duplicates.
4. Sort records chronologically.
5. Sets the date and time as index.

**Function arguments**:
* `path`: is the directory of the file where the "MN_DATA.CSV" is stored.

### **`no_redundancy()`**
This functions deals with redundancy of the data between dyads. Since Node A meets B and node B meets A, this data is redundant. This function deliver pair-wise interactions of specified nodes. This function uses the output DataFrame delivered by the `mn_data_loader()` function to do the following:

1. Captures interactions between specified nodes (e.g. A-B and B-A).
2. Fill missing values where data is not redundant.
3. Get the maximum RSSI values between nodes (returned in the column `RSSI_max`).
4. Specify the dyad in string format in the colum `dyad`.
5. If specified, returns interactions between a time window.

**Function arguments**
* `df`: DataFrame where the output of the `mn_data_loader()` is stored.
* `Node1`: string of the first node of a given dyad (e.g. `'A'`)
* `Node2`: string of the second node of a given dyad (e.g. `'B'`)
* `start`: datetime string specifying the start of the observation window, it should be specified in the following format `YYYY-MM-DD HH:MM:SS`. Default value is `None`.
* `end`: datetime string specifying the end of the observation window, it should be specified in the following format `YYYY-MM-DD HH:MM:SS`. Default value is `None`.

### **`save_csv()`**
This is a basic function to store, into your working directory, DataFrames as .csv files delivered by `mn_range_loader()`, `mn_data_loader()` and `no_redundancy()`. 

**Function arguments**:
* `df`: DataFrame to be saved as .csv
* `name`: name of the file, do not include '.csv' e.g. 'my_file'
* `index`: specify is the index should be saved as a column or kept as index. The default value is `True` saving the index as colum. Saving the index as column allows to use the output file in R.

# Getting started
The packages can be found on PyPI hence you can install it using `pip`

## Installation
```bash
pip install dulogpy
```

## Usage
Using function to load range and proxmity data.
```python
>>> from pydulog import mn_range_loader, mn_data_loader

# For loading Range data from Donwload Station
>>> mn_range_loader('data_file_path.csv', is_ds=True)

# For loading Range data from Base Station
>>> mn_range_loader('data_file_path.csv', is_ds=False)

# For loading Proximity data from any Ground Node
>>> mn_data_loader('data_file_path.csv')
```

## Contributions
Contributions are welcome.
If you notice a bug, let me know. Thanks.