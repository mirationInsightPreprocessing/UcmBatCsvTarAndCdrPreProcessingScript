Hostname> python UserBasedUCMFeatureMigration.py
Total arguments passed: 0
Usage:
1.	python UserBasedUCMFeatureMigration.py DNInMultipleDP insightDir=(see below)
2.	python UserBasedUCMFeatureMigration.py csvDir=(see below) UserList=(see below) insightDir=(see below)


Parameters:
DNInmultipleDP -> Identify Directory numbers which present in multiple Device Pools and list in DNInMultipleDevicePool.csv in insightDir

csvDir=<Path to directory where UCM Feature Migration tool output .zip is unziped>

userList=<UserList file (same format as used in UCM migration tool) with path. Use EMAIL ID (not CUCM USER ID) and you can add Location column to overide user/device location.

insightDir=<Path to directory where UCM Migration Insight tool output .zip is unziped>. This is needed for Call Park and Pickup group WxC CSVs needs to be creeated from Migration Insight output

This tool provide 4 main functionality:
1.	User list based filtering of output from "Migrate features from UCM" tool. You can override user/device location also using a Location column.
2.	Identify users which are part of group features but not present in provided User list
3.	Identify Directory numbers which present in multiple Device Pools and list in DNInMultipleDevicePool.csv in insightDir
4.	Create Call park and Call Pickup group WxC CSV files which currently "Migrate features from UCM" tool doesnt generate
