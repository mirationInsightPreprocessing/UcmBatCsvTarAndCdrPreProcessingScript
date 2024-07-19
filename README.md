This repository contains scripts to assist with migration to Webex Calling-related tasks.
The script provided here will process (merge, remove unwanted columns, compress etc.) the Call detail records (CDR) data collected on a server or Unified Communications Manager (UCM). The corresponding compressed files then can be uploaded on Control Hub

### Executables
 
For convenience, pre-built executables for different operating systems are provided in this repository under executable.zip folder. These executables allow you to run the scripts without needing to set up a Python environment.
 
Available Executables
 
#Mac/: Contains the executable for macOS users.
#Windows/: Contains the executable for Windows users.
#Ubuntu/: Contains the executable for Ubuntu users.
 
## Building Your Own Executable
 
If you prefer to build your own executable from the source code, you can find the source code in the wrapperForExecutable.py file. Follow the instructions below to create an executable for your platform:
 
## Prerequisites
 
Ensure you have Python 3.x.x installed on your system.
Any additional dependencies required by the scripts should be installed.
 
Build Instructions
 
Navigate to the Source/ directory where the script files are located.
Use a tool like pyinstaller to create an executable. For example:
# Mac/Ubuntu:  pyinstaller --onefile wrapperForExecutable.py
# Windows: pyinstaller.exe --onefile -F wrapperForExecutable.py

The executable will be created in the dist/ directory within the Source/ directory.

### Currently the following scripts are supported:

- [cdrfgzip](cdrfgzip/README.md)
- [csvftar](csvftar/README.md)

### preprocess Unified Communications Manager (UCM) Export tar File using the [csvftar](csvftar/README.md) script

As part of the migration from a local UCM to Webex Calling Multi-tenant,
the data needed by the Webex Calling migration processing needs to be
extracted from a current UCM tar file exported using the [Bulk
Administration Tool (BAT) export
](https://www.cisco.com/c/en/us/support/docs/unified-communications/bulk-administration-tool/200596-Bulk-Configure-Changes-with-Import-Expor.html#anc7).

Once this tar file has been generated and is available locally, the
`csvftar.py` script should then be used to regenerate the tar file containing *only* the data needed for migration. This new tar file should then be uploaded to the Webex Calling Migration Tool in the Control Hub.

- You can use this script when you need to decrease the tar file size because the size for migration is 350 MB. This is achieved by removing not required columns.
- You can use this script when you need to filter the records based on a specific column, for example, a particular device pool
- Follow [cdrfgzip](cdrfgzip/README.md) for Syntax and example test cases. you can find the sample files in the script directory.

### preprocess Call detail records (CDR'S) File using the [cdrfgzip](cdrfgzip/README.md) script

#### How to Collect CDR's
Please follow [this](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/service/12_5_1/Car/cucm_b_cdr-analysis-reporting-admin-guide-1251/cucm_b_cdr-analysis-reporting-admin-guide-1251_chapter_010.html#CUCM_RF_C60605F7_00) link for details: 

***Important Note*** Once CDR is received and is available locally, it is mandatory to preprocess the script before uploading it to CH for [Migration Insight](https://help.webex.com/en-us/article/svoi86/Migration-Insights) The script will take your CDR which can be a list of text or CSV file and will regenerate the file in .csv.gz format, which is the acceptable format for MigrationInsight. This helps us in file size reduction as the allowed limit on Control Hub is 2Gb

- This script removes columns that are not required for processing on Control Hub.
- This script also supports filtering where it also requires a UCM tar file from the above step. On filtering it will give data only for devices that are present in phone.csv from the UCM tar file. 
- Follow [cdrfgzip](cdrfgzip/README.md) for Syntax and example test cases. you can find the sample files in the script directory.

### Python version and OS consideration
The scripts had been tested under both Windows 10 and Ubuntu.
The version of Python is 3. x.x.

## Contacts
* Michael Jiang (mijiang@cisco.com)
* Ajay Gupta (akgupta@cisco.com)
* kishan yadav (kishyada@cisco.com)
* Rod Morehead (rmorehea@cisco.com)
* Charles Mather (cmather@cisco.com)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)