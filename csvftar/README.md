# softer - UCM Tar file pre-processing script

Script to extract migration data from UCM tar export to CSV for
migration upload.

### Running the `csvftar.py` Script

```
usage: python3 csvftar.py [-h] -i INPUT [-f FILTER] [-o OUTPUT]
options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        input tarfile path
  -f FILTER, --filter FILTER
                        filter csv file path. Filter csv header: csvFileName,filterName,filterValues,filterValuesFile
  -o OUTPUT, --output OUTPUT
                        output dir. Optional; If not specified, the dir of input tarfile path will be used
```
The path to the exported UCM data tarfile is the input argument specified using the  `-i` command line argument.

To specify the output filename path for the CSV file, use the `-o` argument.

## Script Functionality

This script extracts the following UCM input CSV files and removes columns of data that are not needed for migration:

* Phone CSV
* Enduser CSV
* Filter CSV

### Filter CSV File Format

- Besides the columns' removal, the filter is the concept that can separate UCM data between some boundaries, such as by device pools, by locations, etc..
The filter input is a CSV filter with the following header:

csvFileName,filterName,filterValues,filterValuesFile

where
- The CSV file of csvFileName should be in the UCM data tarfile, otherwise that filter row will have no effect.
- For each CSV file, multiple filters can be used. Note, that when multiple filters are used, the filters' relationship is logic AND.
- The filtering uses the string CONTAIN to determine whether the condition is met. In other words, if a to-be-filter column contains the filter value, then that row meets the condition.

### Design/Implementation

- The codes are written in Python, using the Python Standard library to avoid extra installation requirements.
- The only required input is the UCM data tarfile.
- The output is the tar file using the same name as the original one.
- To avoid overwriting the original one, specify the output path.
- The filtering step is executed before column removal, in case filtering uses the column content to be removed.

### Example Invocations

#### Case 1: No Filtering with Output Path
* Syntax:
  ```python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp ```
* This test simply removed the columns (as described above) in phone.csv and enduser,csv files. Then put the tarfile under the ~/Temp folder.
* PASSED.

#### Case 2: No Filtering without Output Path

* run with input tarfile, without filtering, and not specify output path:
* Syntax:
  ``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar ```
* This test is essentially the same as the above one, BUT no output path is specified. In this case,  the input path will be used,  the original tarfile will be overwritten.
* PASSED.

#### Case 3: Filtering Using Input CSV File
* run with input tarfile, with the following filter csvfile whose filterValues are only in txt files:

  ```
  csvFileName,filterName,filterValues,filterValuesFile
  phone.csv,Description,,filter1Values.txt
  enduser.csv,"FIRST NAME",,filter2Values.txt
  the content in filter1Values.txt is as below:
  CX_BA-1,CX_BA-2
  migrationuser1-CSF
  migrationuser2-CSF
  migrationuser3-CSF
  the content in filter2Values.txt is as below:
  fakevalue4,fakevalue5,fakevalue6
  Finfirstname1006
  fakevalue7
  ```

* Syntax:
  ``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp -f ~/Filter/Set1/filter.csv ```

#### Case 4: Filtering Using Input CSV File and Filter Values Text File
* run with input tarfile, with the following filter csvfile in which filter values are strings inside both csvfile and fliterValues txt file:

```
csvFileName,filterName,filterValues,filterValuesFile
phone.csv,Device Pool,"DP-MEDIA-REMOTE-A,DP-SUB-1A_SUB-1B, fakevalue, CX_BA-1",
enduser.csv,"FIRST NAME","Enfirstname1005",filterValues.txt
```

the content in filterValues.txt is as follows:

```
fakevalue4,fakevalue5,fakevalue6
Finfirstname1006
fakevalue7
```

* Syntax:
  ``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp -f ~/Filter/Set2/filter.csv ```
