This repository contains scripts to assist with migration to Webex Calling-related tasks.
The script provided here will process (merge, remove unwanted columns, compress etc.) the CDR data collected on a server. The processed CDR file (in .zip format) can be uploaded on to Webex Control Hub.

Currently the following scripts are supported:

- [cdrfgzip](cdrfgzip/README.md)
- [csvftar](csvftar/README.md)
- [diJRule](diJRule/README.md)

### How to collect CDR's
Please follow [this](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/service/12_5_1/Car/cucm_b_cdr-analysis-reporting-admin-guide-1251/cucm_b_cdr-analysis-reporting-admin-guide-1251_chapter_010.html#CUCM_RF_C60605F7_00) link for details: 

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