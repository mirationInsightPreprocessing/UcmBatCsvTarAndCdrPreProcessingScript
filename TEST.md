#### Case 1: No Filtering with Output Path
* Syntax:
  ```python3 csvftar.py -i ~/Downloads/ucmdata_export.tar -o ~/Temp ```
* This test simply removed the columns (as described above) in phone.csv and enduser,csv files. Then put the tarfile under ~/Temp folder.
* PASSED.

#### Case 1: No Filtering without Output Path

* run with input tarfile, without filtering, and not specify output path:
* Syntax:
  ``` python3 csvftar.py -i ~/Downloads/ucmdata_export.tar ```
* This test is essentially same as the above one, BUT no output path is specified. In this case  the input path will be used,  the original tarfile will be overwritten.
* PASSED.
