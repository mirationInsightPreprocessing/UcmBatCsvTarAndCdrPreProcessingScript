# UCM Tar file and CDR pre processing script, decompress file size

## Contacts
* Michael Jiang (mijiang@cisco.com)
* Ajay Gupta (akgupta@cisco.com)
* kishan yadav (kishyada@cisco.com)
* Rod Morehead (rmorehea@cisco.com)
* Charles Mather (cmather@cisco.com)

### Python version and OS consideration
The scripts had been tested under both Windows 10 and Ubuntu.
The version of Python is 3. x.x.

## UCM Tar file preprocessing

### Description

For this preprocessing, UCM data tarfile is  the input. 
The filtering can be applied to any csv file contained in UCM data tarfile, 
but the content (/columns) removal is only for phone.csv and enduser,csv files. 

The steps are
* take cucm tar file (which contains phone.csv and enduser,csv) as input, untar it;
* apply the filtering on any csv file defined in filter  (a format-predefined csv file, see below section);
* remove the unwanted columns in phone.csv and enduser,csv files;
* tar the processed files.

**Note** : it is easy to add removing content(/columns) in csv file other than phone.csv and enduser,csv files: 
* define csv filename and the columns to be removed, then add one if statement in Python script.

### Phone CSV's columns removal

The following columns (total 43) need to be removed:
['Services Provisioning','Packet Capture Mode','Packet Capture Duration','Phone Load Name','Authentication Server','Proxy Server','MLPP Indication','MLPP Preemption','MLPP Domain','Digest User',
'Device Presence Group','Device Security Profile','Device Subscribe CSS','Unattended Port','Require DTMF Reception','RFC2833 Disabled','Certificate Operation','Authentication String','Operation Completes By',
'XML','CSS Reroute','Rerouting Calling Search Space','Default DTMF Capability','MTP Preferred Originating Codec','Logout Profile','Signaling Port','Gatekeeper Name','Motorola WSM Connection',
'Secure Authentication URL','Secure Directory URL','Secure Idle URL','Secure Information URL','Secure Messages URL','Secure Services URL','Early Offer support for voice and video calls (insert MTP if needed)',
'Caller ID Calling Party Transformation CSS','Caller ID Use Device Pool Calling Party Transformation CSS','Remote Number Calling party Transformation CSS','Remote Number Use Device Pool Calling Party Transformation CSS',
'Require off-premise location','Confidential Access Mode','Confidential Access Level','MLPP Target 2']

### Enduser CSV's columns removal

The following columns (total 56) need to be removed:
['ASSOCIATED PC','PAGER','DELETED TIME STAMP','DIGEST CREDENTIALS','PRESENCE GROUP','SUBSCRIBE CSS','ENABLE USER FOR UNIFIED CM IM AND PRESENCE',
'INCLUDE MEETING INFORMATION IN PRESENCE','ASSIGNED PRESENCE SERVER','PASSWORD LOCKED BY ADMIN 1','PASSWORD CANT CHANGE 1','PASSWORD MUST CHANGE AT NEXT LOGIN 1',
'PASSWORD DOES NOT EXPIRE 1','PASSWORD AUTHENTICATION RULE 1','PASSWORD 1','PIN LOCKED BY ADMIN 1','PIN CANT CHANGE 1','PIN MUST CHANGE AT NEXT LOGIN 1','PIN DOES NOT EXPIRE 1',
'PIN AUTHENTICATION RULE 1','PIN 1','APPLICATION SERVER NAME 1','CONTENT 1','ACCESS CONTROL GROUP 1','ACCESS CONTROL GROUP 2','ACCESS CONTROL GROUP 3','ACCESS CONTROL GROUP 4',
'ACCESS CONTROL GROUP 5','ACCESS CONTROL GROUP 6','ACCESS CONTROL GROUP 7','ACCESS CONTROL GROUP 8','ACCESS CONTROL GROUP 9','ACCESS CONTROL GROUP 10','ACCESS CONTROL GROUP 11',
'ACCESS CONTROL GROUP 12','ACCESS CONTROL GROUP 13','ACCESS CONTROL GROUP 14','ACCESS CONTROL GROUP 15','ACCESS CONTROL GROUP 16','ACCESS CONTROL GROUP 17','ACCESS CONTROL GROUP 18',
'ACCESS CONTROL GROUP 19','ACCESS CONTROL GROUP 20','ACCESS CONTROL GROUP 21','ACCESS CONTROL GROUP 22','ACCESS CONTROL GROUP 23','ACCESS CONTROL GROUP 24','ACCESS CONTROL GROUP 25',
'ACCESS CONTROL GROUP 26','ACCESS CONTROL GROUP 27','ACCESS CONTROL GROUP 28','ACCESS CONTROL GROUP 29','ACCESS CONTROL GROUP 30','MLPP PRECEDENCE AUTHORIZATION LEVEL 1',
'MLPP USER IDENTIFICATION NUMBER 1','MLPP PASSWORD 1']

### Filter

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

The codes are in written in Python, using Python Standard library to avoid extra installation requirement.
The only required input is the UCM data tarfile.
The output is the tarfile using the same name as original one.
To avoid overwriting the original one, specify the output path.
The filtering step is executed before column removal, in case that a filtering uses the column content to be removed.

### Syntax to run script:

```
usage: csvftar.py [-h] -i INPUT [-f FILTER] [-o OUTPUT]
options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        input tarfile path
  -f FILTER, --filter FILTER
                        filter csv file path. Filter csv header: csvFileName,filterName,filterValues,filterValuesFile
  -o OUTPUT, --output OUTPUT
                        output dir. Optional; If not specified, the dir of input tarfile path will be used
```

**Tests**

**Normal cases:**

**Case 1** - 
* run with input tarfile, without filtering:
* Syntax:  
```python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp ```
* This test simply removed the columns (as described above) in phone.csv and enduser,csv files. Then put the tarfile under ~/Temp folder.
* PASSED.

**Case 2** - 
* run with input tarfile, without filtering, and not specify output path:
* Syntax:  
``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar ```
* This test is essentially same as the above one, BUT no output path is specified. In this case  the input path will be used,  the original tarfile will be overwritten.
* PASSED.

**Case 3** - 
* run with input tarfile, without filtering, but the output folder does not exist:
* Syntax:  
``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/NewFolder ```
* This test will create the output folder, then put the new tarfile under it.
* PASSED.

**Case 4** - 
* run with input tarfile, with the filter csvfile which does not have any row besides the header:
* Syntax:  
``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp -f ~/Filter/Set1/filter.csv ```
* In this case, the filter csvfile has no effect, hence the result is same as the above cases.
* PASSED.

**Case 5** - 
* run with input tarfile, with the following filter csvfile in which file names not in UCM data tarfile:
csvFileName,filterName,filterValues,filterValuesFile
phone1.csv,Device Pool,"DP-MEDIA-REMOTE-A,CX_BA-1, value3",
enduser2.csv,"FIRST NAME","Enfirstname1005",filter.txt

* Syntax:  
``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp -f ~/Filter/Set1/filter.csv ```

* In this case, the filter does not have any effect, hence  the result is same as the above cases.
PASSED.

**Case 6** - 
* run with input tarfile, with the following filter csvfile whose filterValues are only in txt files:
  ```csvFileName,filterName,filterValues,filterValuesFile
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
* PASSED.

**Case 7** - 
* run with input tarfile, with the following filter csvfile in which filter values are strings inside both csvfile and fliterValues txt file:
``` csvFileName,filterName,filterValues,filterValuesFile
phone.csv,Device Pool,"DP-MEDIA-REMOTE-A,DP-SUB-1A_SUB-1B, fakevalue, CX_BA-1",
enduser.csv,"FIRST NAME","Enfirstname1005",filterValues.txt
the content in filterValues.txt is as below:
fakevalue4,fakevalue5,fakevalue6
Finfirstname1006
fakevalue7
```
* Syntax:  
``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp -f ~/Filter/Set2/filter.csv ```
* PASSED.

**Case 8** - 
* run with input tarfile, with the following filter csvfile in which multiple filters will be used on a file (such as on phone.csv):
```csvFileName,filterName,filterValues,filterValuesFile
phone.csv,Device Pool,"DP-MEDIA-REMOTE-A,DP-SUB-1A_SUB-1B,",
phone.csv,Description,,filter1Values.txt
enduser.csv,"FIRST NAME","Enfirstname1005",filter2Values.txt
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
``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp -f ~/Filter/Set3/filter.csv ```
* PASSED.

**Case 9** - 
* run with input tarfile, with the following filter csvfile in which the filter value is part of whole string in csvfile:
csvFileName,filterName,filterValues,filterValuesFile
phone.csv,Device Pool,"DP",
The test is for filter value CONTAIN test. All rows whose Device Pool contain "DP" (such as "DP-MEDIA-REMOTE-A" or "DP-SUB-1A_SUB-1B") will be included in final tarfile.
* Syntax:  
``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp -f ~/Filter/Set3/filter.csv ```
* PASSED.

## CDR CSV filtering and combining

### Description

This preprocessing does the following tasks:
* collect CDR files CUCM generates since the last collection time;
* apply the filtering which is Device Name in phone.csv.  Only the CDR which contains one of devices in phone.csv will be included for next step;
* remove the unwanted columns;
* combine the CDR files into one, then gzip. 

**CDR CSV columns' removal**

The following columns will be removed in processing:
['origIpAddr','callingPartyNumber','callingPartyUnicodeLoginUserID','origMediaTransportAddress_IP','origMediaTransportAddress_Port','origVideoTransportAddress_IP','origVideoTransportAddress_Port',
 'destIpAddr','originalCalledPartyNumber','finalCalledPartyNumber','finalCalledPartyUnicodeLoginUserID','destMediaTransportAddress_IP','destMediaTransportAddress_Port','destVideoTransportAddress_IP',
 'destVideoTransportAddress_Port','outpulsedCallingPartyNumber','outpulsedCalledPartyNumber','origIpv4v6Addr','destIpv4v6Addr','origVideoTransportAddress_IP_Channel2','origVideoTransportAddress_Port_Channel2',
 'destVideoTransportAddress_IP_Channel2','destVideoTransportAddress_Port_Channel2','outpulsedOriginalCalledPartyNumber','outpulsedLastRedirectingNumber','callingPartyNumber_uri',
 'originalCalledPartyNumber_uri','finalCalledPartyNumber_uri','lastRedirectDn_uri','mobileCallingPartyNumber','finalMobileCalledPartyNumber']

**Filter**

Filtering for CDR is meant to collect the information of the only related devices, which can be correlated by Device Name, hence the phone.csv  from UCM data is used.
For convenience, both UCM data tarfile and phone.csv can be used.
Filtering is optional. IF not specifying a filter or something goes wrong with filter file, the filtering will be ignored.
Design/Implementation
The codes are in written in Python, using Python Standard library to avoid extra installation requirement.
The only required input is the path of UCM CDR folder.  The user running the script must have read permission on the path and CDR files.
The filtering step is executed before column removal, in case that a filtering uses the column content to be removed.

The script has some running options such as output path, maxlines per combined CDR file. Those options only needs input once.
Important note: a small text file (for run configuration) needs to created in CDR folder, hence the user running the script should have write permission on CDR folder.

### Syntax to run script

```
usage: cdrfgzip.py [-h] -p PATH [-o OUTPUT] [-l MAXLINES] [-f FILTER]
options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  sftp/ftp path
  -o OUTPUT, --output OUTPUT
                        output zip file path. If not specified, use PATH
  -l MAXLINES, --maxlines MAXLINES
                        the max records number in one csv file; max is 1000000
  -f FILTER, --filter FILTER
                        the filter file path, either the tarfile containing phone.csv  or phone.csv  itself.
```

**Note**, if the value of maxlines option is 0, then the default 1000000 will be used. If the specified filter file does not exist, then filtering will be ignored.
**Tests**
Normal cases:

**Case 1** - 
* run with CDR path only:
since no output path, the final gzip file(s) will be put into CDR folder; since no filter is specified, the final CDR file(s) will remove those columns (see above section) only.
* Syntax: 
``` python3 cdrfgzip.py -p ~/ftp/upload ```
* PASSED

**Case 2** - 
* run with CDR path, output path and maxlines options:
In this test, maxlines per combined CDR file is 100.  Since we have about 150 records in CDR path, multiple gzip files are generated.
$ ls Temp
combined_filtered_cdr_2023-06-03_07_34_15.946318.csv.gz  combined_filtered_cdr_2023-06-17_07_57_03.960705.csv.gz
* Syntax:
```python3 cdrfgzip.py -p ~/ftp/upload  -o ~/Temp -l 100```
* PASSED

**Case 3** - 
* run with CDR path only after Case 2:
In this test, no other options are specified besides input CDR path,  the run configuration from last run will be use: the new combined CDR gzip will be in same output folder with maxlines 100 per file.
$ ls Temp
combined_filtered_cdr_2023-06-03_07_34_15.946318.csv.gz  combined_filtered_cdr_2023-06-17_07_57_03.960705.csv.gz  combined_filtered_cdr_2023-06-18_09_09_06.180277.csv.gz
* Syntax:
```python3 cdrfgzip.py -p ~/ftp/upload```
* PASSED

**Case 4** - 
* specify a UCM data tarfile as the filter:
the UCM data tarfile can be the original one or the one after processing described. The script will use phone.csv inside tarfile to filter on CDR rows.
* Syntax: 
``` python3 cdrfgzip.py -p ~/ftp/upload -f ~/Filter/Set2/ucmdata_export_61_74.tar -o ~/Temp ```
* PASSED

**Case 5** - 
* specify a phone.csv as the filter:
the filter is phone.csv, the filter will be used.
* Syntax: 
``` python3 cdrfgzip.py -p ~/ftp/upload -o ~/Temp -f ~/Filter/Set2/phone.csv ```
* PASSED

**Case 6** - 
* specify a tarfile containing phone.csv or phone.csv as the filter, but no content in it:
the filter has no effect since no cotents.
* Syntax: 
``` python3 cdrfgzip.py -p ~/ftp/upload -o ~/Temp -f ~/Filter/Set1/phone.csv ```
* PASSED

**Case 7** - 
* specify a filter which does not exist:
since the filter does not exist, the output will be generated without any filtering.
* Syntax: 
```python3 cdrfgzip.py -p ~/ftp/upload -o ~/Temp -f ~/Filter/notexisted```
PASSED

**Case 8** - 
* specify a csv file as filter, but its name is not phone.csv:
the filter file can only be the tarfile containing phone.csv  or phone.csv  itself, so this filter will not have any effect.
* Syntax: 
```python3 cdrfgzip.py -p ~/ftp/upload -o ~/Temp -f ~/Filter/unrelated.csv```
* PASSED

**Case 9** - 
* run script after previous run but there is no new CDR file generated:
this test is to check that the script will not generate any new output, instead it should display some info as below:
2023-06-18 06:07:03,613 [INFO] No new cdr files generated after 2023-06-17 07:57:03.960705
* Syntax:
``` python3 cdrfgzip.py -p ~/ftp/upload -o ~/Temp```
* PASSED

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.