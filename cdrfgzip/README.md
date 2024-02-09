## CDR CSV filtering and combining
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
  -c compress, --compress COMPRESS
                        specify the compressed format (gzip) used for original cdr file. Default is plain csv.
```

**Note**, If the value of the maxlines option is 0, then the default 1000000 will be used. If the specified filter file does not exist, then filtering will be ignored.

### Description

This preprocessing does the following tasks:

1. Collect CDR files CUCM generates since the last collection time.
2. Apply the filtering which is Device Name in phone.csv.  Only the
   CDR which contains one of the devices in phone.csv will be included for the next step.
3. Remove the unwanted columns.
4. Combine the CDR files into one, then gzip.

### CDR CSV Column Removal

The following columns will be removed in processing:

* origIpAddr
* origMediaTransportAddress_IP
* origMediaTransportAddress_Port
* origVideoTransportAddress_IP
* origVideoTransportAddress_Port
* destIpAddr
* destMediaTransportAddress_IP
* destMediaTransportAddress_Port
* destVideoTransportAddress_IP
* destVideoTransportAddress_Port
* outpulsedCallingPartyNumber
* outpulsedCalledPartyNumber
* origIpv4v6Addr
* destIpv4v6Addr
* origVideoTransportAddress_IP_Channel2
* origVideoTransportAddress_Port_Channel2
* destVideoTransportAddress_IP_Channel2
* destVideoTransportAddress_Port_Channel2
* outpulsedOriginalCalledPartyNumber
* outpulsedLastRedirectingNumber
* callingPartyNumber_uri
* originalCalledPartyNumber_uri
* finalCalledPartyNumber_uri
* lastRedirectDn_uri
* mobileCallingPartyNumber
* finalMobileCalledPartyNumber

**Filter**

Filtering for CDR is meant to collect the information of the only related devices, which can be correlated by Device Name, hence the phone.csv  from UCM data is used.
For convenience, both UCM data tarfile and phone.csv can be used.
Filtering is optional. If not specifying a filter or something goes wrong with filter file, the filtering will be ignored.
Design/Implementation
The codes are written in Python, using Python Standard library to avoid extra installation requirement.
The only required input is the path of UCM CDR folder.  The user running the script must have read permission on the path and CDR files.
The filtering step is executed before column removal, in case that a filtering uses the column content to be removed.

The script has some running options such as output path, maxlines per combined CDR file. Those options only needs input once.
Important note: a small text file (for run configuration) needs to created in CDR folder, hence the user running the script should have write permission on CDR folder.


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
  In this test, no other options are specified besides the input CDR path,  the run configuration from the last run will be used: the new combined CDR gzip will be in the same output folder with max lines 100 per file.
  $ ls Temp
  combined_filtered_cdr_2023-06-03_07_34_15.946318.csv.gz  combined_filtered_cdr_2023-06-17_07_57_03.960705.csv.gz  combined_filtered_cdr_2023-06-18_09_09_06.180277.csv.gz
* Syntax:
  ```python3 cdrfgzip.py -p ~/ftp/upload```
* PASSED

**Case 4** -
* specify a UCM data tarfile as the filter:
  the UCM data tarfile can be the original one or the one after the processing described. The script will use phone.csv inside tarfile to filter on CDR rows.
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
  the filter has no effect since no contents.
* Syntax:
  ``` python3 cdrfgzip.py -p ~/ftp/upload -o ~/Temp -f ~/Filter/Set1/phone.csv ```
* PASSED

**Case 7** -
* specify a filter that does not exist:
  since the filter does not exist, the output will be generated without any filtering.
* Syntax:
  ```python3 cdrfgzip.py -p ~/ftp/upload -o ~/Temp -f ~/Filter/notexisted```
  PASSED

**Case 8** -
specify a CSV file as a filter, but its name is not phone.csv:
  the filter file can only be the tar file containing phone.csv  or phone.csv  itself, so this filter will not have any effect.
* Syntax:
  ```python3 cdrfgzip.py -p ~/ftp/upload -o ~/Temp -f ~/Filter/unrelated.csv```
* PASSED

**Case 9** -
run a script after a previous run but there is no new CDR file generated:
  this test is to check that the script will not generate any new output, instead it should display some info as below:
  2023-06-18 06:07:03,613 [INFO] No new cdr files generated after 2023-06-17 07:57:03.960705
* Syntax:
  ``` python3 cdrfgzip.py -p ~/ftp/upload -o ~/Temp```
* PASSED

#### DISCLAIMER:
<b>Please note:</b> If you need to upload a processed tar file or cdr file onto our CISCO tool, please ensure that the size of the compressed file is within the specified limit. If the file size exceeds the limit, you may need to delete some data and reprocess the file to make it smaller and meet the tool's requirements.
