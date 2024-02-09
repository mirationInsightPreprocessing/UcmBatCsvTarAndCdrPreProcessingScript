# csvftar - UCM Tar file and CDR pre processing script

Script to extract migration data from UCM tar export to CSV for
migration upload.

## UCM Export tar File to CSV Using the `csvftar.py` Script

As part of migration from a local UCM to Webex Calling Multi-tenant,
the data needed by the Webex Calling migration processing needs to be
extracted from a current UCM tar file exported using the [Bulk
Administration Tool (BAT) export
](https://www.cisco.com/c/en/us/support/docs/unified-communications/bulk-administration-tool/200596-Bulk-Configure-Changes-with-Import-Expor.html#anc7).

Once this tar file has been generated and is available locally, the
`csvftar.py` script should then be used to generate a CVS file
containing *only* the data needed for migration. This CSV file should
then be uploaded to the Webex Calling Migration Tool in Control Hub.

### Script Requirements

These scripts have been tested under both Windows 10 and Ubuntu using
Python 3.10.


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

### Phone CSV Processing

The following columns (total 43) need to be removed:

* Services Provisioning
* Packet Capture Mode
* Packet Capture Duration
* Phone Load Name
* Authentication Server
* Proxy Server
* MLPP Indication
* MLPP Preemption
* MLPP Domain
* Digest User',
  'Device Presence Group
* Device Security Profile
* Device Subscribe CSS
* Unattended Port
* Require DTMF Reception
* RFC2833 Disabled
* Certificate Operation
* Authentication String
* Operation Completes By
* XML
* CSS Reroute
* Rerouting Calling Search Space
* Default DTMF Capability
* MTP Preferred Originating Codec
* Logout Profile
* Signaling Port
* Gatekeeper Name
* Motorola WSM Connection
* Secure Authentication URL
* Secure Directory URL
* Secure Idle URL
* Secure Information URL
* Secure Messages URL
* Secure Services URL
* Early Offer support for voice and video calls (insert MTP if needed)
* Caller ID Calling Party Transformation CSS
* Caller ID Use Device Pool Calling Party Transformation CSS
* Remote Number Calling party Transformation CSS
* Remote Number Use Device Pool Calling Party Transformation CSS
* Require off-premise location
* Confidential Access Mode
* Confidential Access Level
* MLPP Target 2

### Enduser CSV Column Removal

The following columns (total 56) need to be removed:

* ASSOCIATED PC
* PAGER
* DELETED TIME STAMP
* DIGEST CREDENTIALS
* PRESENCE GROUP
* SUBSCRIBE CSS
* ENABLE USER FOR UNIFIED CM IM AND PRESENCE
* INCLUDE MEETING INFORMATION IN PRESENCE
* ASSIGNED PRESENCE SERVER
* PASSWORD LOCKED BY ADMIN 1
* PASSWORD CANT CHANGE 1
* PASSWORD MUST CHANGE AT NEXT LOGIN 1
* PASSWORD DOES NOT EXPIRE 1
* PASSWORD AUTHENTICATION RULE 1
* PASSWORD 1
* PIN LOCKED BY ADMIN 1
* PIN CANT CHANGE 1
* PIN MUST CHANGE AT NEXT LOGIN 1
* PIN DOES NOT EXPIRE 1
* PIN AUTHENTICATION RULE 1
* PIN 1
* APPLICATION SERVER NAME 1
* CONTENT 1
* ACCESS CONTROL GROUP 1
* ACCESS CONTROL GROUP 2
* ACCESS CONTROL GROUP 3
* ACCESS CONTROL GROUP 4
* ACCESS CONTROL GROUP 5
* ACCESS CONTROL GROUP 6
* ACCESS CONTROL GROUP 7
* ACCESS CONTROL GROUP 8
* ACCESS CONTROL GROUP 9
* ACCESS CONTROL GROUP 10
* ACCESS CONTROL GROUP 11
* ACCESS CONTROL GROUP 12
* ACCESS CONTROL GROUP 13
* ACCESS CONTROL GROUP 14
* ACCESS CONTROL GROUP 15
* ACCESS CONTROL GROUP 16
* ACCESS CONTROL GROUP 17
* ACCESS CONTROL GROUP 18
* ACCESS CONTROL GROUP 19
* ACCESS CONTROL GROUP 20
* ACCESS CONTROL GROUP 21
* ACCESS CONTROL GROUP 22
* ACCESS CONTROL GROUP 23
* ACCESS CONTROL GROUP 24
* ACCESS CONTROL GROUP 25
* ACCESS CONTROL GROUP 26
* ACCESS CONTROL GROUP 27
* ACCESS CONTROL GROUP 28
* ACCESS CONTROL GROUP 29
* ACCESS CONTROL GROUP 30
* MLPP PRECEDENCE AUTHORIZATION LEVEL 1
* MLPP USER IDENTIFICATION NUMBER 1
* MLPP PASSWORD 1

### Filter CSV File Format

Besides the columns' removal, the filter is the concept which can separate UCM data between some boundaries, such as by device pools, by locations, etc..
The filter input is a csv filter with the following header:

csvFileName,filterName,filterValues,filterValuesFile

where

| header              | description                                                   | example                                                        |
| ------------------- | ------------------------------------------------------------- | -------------------------------------------------------------- |
| csvFileName         | specify the csv file in UCM data tarfile                      | phone.csv, enduser.csv                                         |
| filterName          | specify the to-be-filter column in the above csv file         | columns: Device Pool, Description, Location in phone.csv       |
|                     |                                                               | columns: FIRST NAME, MAIL ID, TELEPHONE NUMBER in enduser.csv  |
| filterValues        | specify the filter values for the above filter                | DP-MEDIA-REMOTE-A,DP-SUB-1A_SUB-1B                             |
| filterValuesFile    | specify the txt file which contains the list of filter values | filterValues.txt:                                              |
|                     |                                                               | CX_BA-1,CX_BA-2                                                |
|                     |                                                               | migrationuser1-CSF                                             |
|                     |                                                               | migrationuser2-CSF                                             |
|                     |                                                               | migrationuser3-CSF                                             |

The csvfile of csvFileName should be in UCM data tarfile, otherwise that fdilter row will have no effect.
For each csvfile, multiple filters can be used. Note, when multiple filters are used, the filters' relationship is logic AND.
The filtering uses string CONTAIN to determine whether the condition is met. In other words, if a to-be-filter column contains the filter value, then that row meets the condition.

### Design/Implementation

The codes are written in Python, using Python Standard library to avoid extra installation requirement.
The only required input is the UCM data tarfile.
The output is the tarfile using the same name as original one.
To avoid overwriting the original one, specify the output path.
The filtering step is executed before column removal, in case that a filtering uses the column content to be removed.

### Example Invocations

#### Case 1: No Filtering with Output Path
* Syntax:
  ```python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp ```
* This test simply removed the columns (as described above) in phone.csv and enduser,csv files. Then put the tarfile under ~/Temp folder.
* PASSED.

#### Case 2: No Filtering without Output Path

* run with input tarfile, without filtering, and not specify output path:
* Syntax:
  ``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar ```
* This test is essentially same as the above one, BUT no output path is specified. In this case  the input path will be used,  the original tarfile will be overwritten.
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

the content in filterValues.txt is as below:

```
fakevalue4,fakevalue5,fakevalue6
Finfirstname1006
fakevalue7
```

* Syntax:
  ``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp -f ~/Filter/Set2/filter.csv ```
