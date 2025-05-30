import pandas as pd
import csv
import os
import sys

#Create User, Device and Virtual Lines Filtered List
# Loop through all of the emails and devices in userstomigrate_sample and filter out rows from following CSVs:
# VirtualLineBulk, ConfiguredLineBulk, deviceLineKeyConfiguration, callForward_Internal, callForward_External
# and create new set of CSV files under a sub-directory - FilteredCSVs

def createUserDeviceVirtuallineFilteredList(directory_path, userstomigrate_sample, VirtualLineBulk, ConfiguredLineBulk, deviceLineKeyConfiguration, userFeaturesInternal, userFeaturesExternal):

    print("Starting to create user list based user / device specific CSV files" + '\n\n')
    deviceLineKeyList = []
    shareLineUserNotInUserList = []
    
    #ConfiguredLineBulk.replace(np.nan, '', regex=True)
    
    for indexUL, rowUL in userstomigrate_sample.iterrows():
        try:
            print("Start filtering ConfiguredLineBulk for user/device in UserList", rowUL['EMAIL ID'], rowUL['DEVICE MAC'])
            for indexCL, rowCL in ConfiguredLineBulk.iterrows():
                headers = list(ConfiguredLineBulk.columns)

                # Creating filtered ConfiguredLineBulk
                userNum = 1
                appended = False
                for header in headers:
                    try: 
                        try: 
                            if (pd.isnull(rowCL['Location ' + str(userNum)]) != False):
                                rowCL['Location ' +  str(userNum)] = rowUL['Location']
                        except:
                            pass
                        if 'Username' in header:
                            try:
                                if ((pd.isnull(rowCL['Username ' + str(userNum)]) == False) and (rowCL['Username ' + str(userNum)] == rowUL['EMAIL ID'])):
                                    if appended == False:
                                        rowCL.fillna('', inplace=True)
                                        deviceLineKeyList.append(rowCL)
                                        appended = True
                                if ((pd.isnull(rowCL['Username ' + str(userNum)]) == False) and (rowCL['Username ' + str(userNum)] != rowUL['EMAIL ID'])):
                                    if rowCL['Username ' + str(userNum)] not in shareLineUserNotInUserList:
                                        shareLineUserNotInUserList.append(rowCL['Username ' + str(userNum)])
                                userNum = userNum + 1
                            except:
                                userNum = userNum + 1
                        if 'Device MAC' in header:
                            if ((pd.isnull(rowCL['Device MAC']) == False) and (rowCL['Device MAC'] == rowUL['DEVICE MAC'])):
                                if appended == False:
                                    rowCL.fillna('', inplace=True)
                                    deviceLineKeyList.append(rowCL)
                                    appended = True
                    except:
                        print("Issue in creating  with filtered ConfiguredLineBulk for header ", header)
        except: 
            print("Error in processing for createUserDeviceVirtuallineFilteredList for: ", rowUL['EMAIL ID'], rowUL['DEVICE MAC'])
    
    # Warn if there shared Line users which are not in UserList
    if shareLineUserNotInUserList:
        print('\n\n' + "WARNING: You have in shared Line users but not in userList ")  
        
    # Creating filtered VirtualLineBulk
    # Use deviceLineKeyList which contains filtered list of devices based on user list
    vl = pd.DataFrame(deviceLineKeyList)
    headers = vl.columns.tolist()
    vlList = []
    
    for row in deviceLineKeyList:
        userNum = 1
        print("Start filtering Virtual Line  CSV for device in ConfiguredLineBulk: " + row['Device MAC'])
        for header in headers:
            try: 
                if 'Type' in header:     
                    if (row['Type ' + str(userNum)] and (row['Type ' + str(userNum)] == "VIRTUAL_PROFILE")):
                        virtualExtNum = {}
                        virtualExtNum['Extension'] = ""
                        virtualExtNum['Phone Number'] = ""
                        virtualExtNum['Location'] = ""
                        try:
                            if row['Extension ' + str(userNum)]: 
                                virtualExtNum['Extension'] = int(row['Extension ' + str(userNum)])
                                row['Extension ' + str(userNum)] = int(row['Extension ' + str(userNum)])
                        except:
                            pass
                        try:
                            if row['Phone Number ' + str(userNum)]:
                                virtualExtNum['Phone Number'] = int(row['Phone Number ' + str(userNum)])
                                row['Phone Number ' + str(userNum)] = int(row['Phone Number ' + str(userNum)])
                        except:
                            pass
                        try:
                            if row['Location ' + str(userNum)]:
                                virtualExtNum['Location'] = row['Location ' + str(userNum)]
                        except:
                            pass
                                
                        # Store in a temprarory list
                        if virtualExtNum:
                            vlList.append(virtualExtNum)
                    
                    # Make sure all phone numbers are integer in deviceLineKeyList
                    if (row['Type ' + str(userNum)] and ((row['Type ' + str(userNum)] == "USER") or (row['Type ' + str(userNum)] == "PLACE"))):
                        try:
                            if row['Extension ' + str(userNum)]: 
                                row['Extension ' + str(userNum)] = int(row['Extension ' + str(userNum)])
                        except:
                            pass
                        try:
                            if row['Phone Number ' + str(userNum)]:
                                row['Phone Number ' + str(userNum)] = int(row['Phone Number ' + str(userNum)])
                        except:
                            pass 
                    
                    userNum = userNum + 1
                    
            except:
                print("Issue in creating  with filtered VirtualLineBulk for header ", header)  
                userNum = userNum + 1
                
    # Remove duplicate rows from VirtualLineBulk file and filter for Virtual line from 
    vlOrig = VirtualLineBulk.drop_duplicates()

    # Change Extension to int
    vlFilteredList = []
    for row in vlOrig.iterrows():
        try:
            index = 0
            while index < len(vlList):
                if (str(row[1]['Phone Number']) and str(vlList[index]['Phone Number'])) and(str(row[1]['Phone Number']) == str(vlList[index]['Phone Number'])):
                    row[1]['Location'] = vlList[index]['Location']
                    vlFilteredList.append(row[1])
                    break
                if (str(row[1]['Extension']) and str(vlList[index]['Extension'])) and (str(row[1]['Extension']) == str(vlList[index]['Extension'])):
                    row[1]['Location'] = vlList[index]['Location']
                    vlFilteredList.append(row[1])
                    break
                index = index + 1
        except:
            print("Error in creating Virtual Line Filered list for ", row[1]['Display Name'])
    virtualLineBulkFiltered = pd.DataFrame(vlFilteredList)
    
    # Filter deviceLineKeyConfiguration for Device MAC in ConfiguredLineBulk
    print('\n\n' + "Start filtering device Line Key Configuration CSV")
    deviceList = []
    for row in deviceLineKeyList:
        deviceList.append(row['Device MAC'])
        
    deviceLineKeyConfigurationFiltered = deviceLineKeyConfiguration[deviceLineKeyConfiguration['Device MAC'].isin(deviceList)]
    # Create filtered device LineKey Configuration CSV
    deviceLineKeyConfigurationFiltered.to_csv(directory_path + '/deviceLineKeyConfiguration.csv', index=False)
    
    # Create filtered Virtual Line CSV
    fileVL = directory_path + '/VirtualLineBulk.csv'
    with open(fileVL, 'w') as file2:
        writer = csv.writer(file2)
        writer.writerow(vlOrig.columns.tolist())
        writer.writerows(vlFilteredList)    

    # Create filtred Configured Line CSV
    fileCL = directory_path + '/ConfiguredLineBulk.csv'
    with open(fileCL, 'w') as file3:
        writer = csv.writer(file3)
        writer.writerow(headers)
        writer.writerows(deviceLineKeyList)

    # Filter userFeaturesInternal for user in userstomigrate_sample
    print("Start filtering User Features Filtered CSV")
    userList = []
    for indexUL, rowUL in userstomigrate_sample.iterrows():
        if pd.isnull(rowUL['EMAIL ID']) == False:
            userList.append(rowUL['EMAIL ID'])

    userFeaturesInternalFiltered = userFeaturesInternal[userFeaturesInternal['User Email'].isin(userList)]
    # Create filtered device LineKey Configuration CSV
    userFeaturesInternalFiltered.to_csv(directory_path + '/UserFeatures_Internal.csv.csv', index=False) 

    # Filter userFeaturesExternal for user in userstomigrate_sample       
    userFeaturesExternalFiltered = userFeaturesExternal[userFeaturesExternal['User Email'].isin(userList)]
    # Create filtered device LineKey Configuration CSV
    userFeaturesExternalFiltered.to_csv(directory_path + '/UserFeatures_External.csv.csv', index=False)    

def createLocationFeatureFilteredList(directory_path, userstomigrate, HuntGroupBulk, CallQueueBulk, AutoAttendantBulk, CallParkGroup, CallPickupGroup, SharedLineGroup):
    
    print('\n\n' + "Starting to create user list based Location feature based CSV files")
    ### Hunt Group ###
    huntGroupList = []
    agentNotInUserList = []
    headers = list(HuntGroupBulk.columns)
    for indexCL, rowHG in HuntGroupBulk.iterrows():
        try:
            print("Start filtering HuntGroupBulk for user/device in Hunt Group" + rowHG['Name'])
            for iindexUL, rowUL in userstomigrate.iterrows():
                # Creating filtered ConfiguredLineBulk
                userNum = 1
                appended = False
                for header in headers:
                    try: 
                        if 'Agent' in header:
                            try:
                                if ((pd.isnull(rowHG['Agent' + str(userNum) + ' ID']) == False) and (rowHG['Agent' + str(userNum) + ' ID'] == rowUL['EMAIL ID'])):
                                    if appended == False:
                                        rowHG.fillna('', inplace=True)
                                        huntGroupList.append(rowHG)
                                        appended = True
                                if ((pd.isnull(rowHG['Agent' + str(userNum) + ' ID']) == False) and (rowHG['Agent' + str(userNum) + ' ID'] != rowUL['EMAIL ID'])):
                                    if rowHG['Agent' + str(userNum) + ' ID'] not in agentNotInUserList:
                                        agentNotInUserList.append(rowHG['Agent' + str(userNum) + ' ID'])
                                userNum = userNum + 1
                            except:
                                userNum = userNum + 1
                    except:
                        print("Issue in creating  with filtered HuntGroupBulk for header ", header)
        except: 
            print("Error in processing for createLocationFeatureFilteredList for Hunt Group: ", rowHG['Name'])  
    # Warn if there agents which are not in UserList
    if agentNotInUserList:
        print("WARNING: You have in agents in Hunt Groups but not in userList", agentNotInUserList) 

    # Create filtred HuntGroupBulkCSV
    fileHG = directory_path + '/HuntGroupBulk.csv'
    with open(fileHG, 'w') as file1:
        writer = csv.writer(file1)
        writer.writerow(headers)
        writer.writerows(huntGroupList)

    ### Call Queue ###
    callQueueList = []
    agentNotInUserList = []
    headers = list(CallQueueBulk.columns)
    for indexCL, rowCQ in CallQueueBulk.iterrows():
        try:
            print("Start filtering CallQueueBulk for user/device in Hunt Group" + rowCQ['Name'])
            for iindexUL, rowUL in userstomigrate.iterrows():
                # Creating filtered ConfiguredLineBulk
                userNum = 1
                appended = False
                for header in headers:
                    try: 
                        if 'Agent' in header:
                            try:
                                if ((pd.isnull(rowCQ['Agent' + str(userNum) + ' ID']) == False) and (rowCQ['Agent' + str(userNum) + ' ID'] == rowUL['EMAIL ID'])):
                                    if appended == False:
                                        rowCQ.fillna('', inplace=True)
                                        callQueueList.append(rowCQ)
                                        appended = True
                                if ((pd.isnull(rowCQ['Agent' + str(userNum) + ' ID']) == False) and (rowCQ['Agent' + str(userNum) + ' ID'] != rowUL['EMAIL ID'])):
                                    if rowCQ['Agent' + str(userNum) + ' ID'] not in agentNotInUserList:
                                        agentNotInUserList.append(rowCQ['Agent' + str(userNum) + ' ID'])
                                userNum = userNum + 1
                            except:
                                userNum = userNum + 1
                    except:
                        print("Issue in creating  with filtered CallQueueBulk for header ", header)
        except: 
            print("Error in processing for createLocationFeatureFilteredList for Call Queue: ", rowCQ['Name'])  
    # Warn if there agents which are not in UserList
    if agentNotInUserList:
        print("WARNING: You have in agents in Call Queues but not in userList", agentNotInUserList) 

    # Create filtred HuntGroupBulkCSV
    fileCQ = directory_path + '/CallQueueBulk.csv'
    with open(fileCQ, 'w') as file2:
        writer = csv.writer(file2)
        writer.writerow(headers)
        writer.writerows(callQueueList)

    ### Call Park Group ###
    callParkList = []
    callParkName = ""
    callPark = {}
    appendCallPark = False
    for rowCP in CallParkGroup.iterrows():
        if (rowCP[1]['Feature Type'] == "CALL PARK GROUP"):
            if rowCP[1]['Config Name'] != callParkName:
                callParkName = rowCP[1]['Config Name']
                callPark = {}
                callPark['Call Park Name'] = rowCP[1]['Config Name']
                callPark['Location Name'] = ""
                callPark['Recall To'] = ""
                callPark['Hunt Group Name'] = ""
                callPark['Member Action'] = "ADD"
                userNum = 1
                if callParkName:
                    appendCallPark = True
                    
            if pd.isnull(rowCP[1]['Email ID']) == False:
                callPark['Agent' + str(userNum) + ' ID'] = rowCP[1]['Email ID']
            elif pd.isnull(rowCP[1]['User']) == False:
                callPark['Agent' + str(userNum) + ' ID'] = rowCP[1]['User']
            elif pd.isnull(rowCP[1]['Device']) == False:
                callPark['Agent' + str(userNum) + ' ID'] = rowCP[1]['Device']
            else:
                callPark['Agent' + str(userNum) + ' ID'] = rowCP[1]['Line']
            userNum = userNum + 1
            
        if (rowCP[1]['Feature Type'] == "CALL PARK GROUP") and callParkName and appendCallPark:
            callParkList.append(callPark)
    
    callParkBulk = pd.DataFrame(callParkList)
    callParkBulk.fillna('', inplace=True)
    callParkBulk = callParkBulk.drop_duplicates()
    callParkFilteredList = []
    userNotInUserList = []
    headers = list(callParkBulk.columns)
    for indexCL, rowCPk in callParkBulk.iterrows():
        try:
            print("Start filtering callParkBulk for user/device in Hunt Group " + rowCPk['Call Park Name'])
            for iindexUL, rowUL in userstomigrate.iterrows():
                # Creating filtered ConfiguredLineBulk
                userNum = 1
                appended = False
                for header in headers:
                    try: 
                        if 'Agent' in header:
                            try:
                                if ((pd.isnull(rowCPk['Agent' + str(userNum) + ' ID']) == False) and (rowCPk['Agent' + str(userNum) + ' ID'] == rowUL['EMAIL ID'])):
                                    if appended == False:
                                        rowCPk.fillna('', inplace=True)
                                        callParkFilteredList.append(rowCPk)
                                        appended = True
                                if ((pd.isnull(rowCPk['Agent' + str(userNum) + ' ID']) == False) and (rowCPk['Agent' + str(userNum) + ' ID'] != rowUL['EMAIL ID'])):
                                    if rowCPk['Agent' + str(userNum) + ' ID'] not in agentNotInUserList:
                                        agentNotInUserList.append(rowCPk['Agent' + str(userNum) + ' ID'])
                                userNum = userNum + 1
                            except:
                                userNum = userNum + 1
                    except:
                        print("Issue in creating  with filtered callParkBulk for header ", header)
        except: 
            print("Error in processing for createLocationFeatureFilteredList for Call Park Group: ", rowCPk['Call Park Name'])  
    # Warn if there agents which are not in UserList
    if agentNotInUserList:
        print("WARNING: You have in agents in Call parks but not in userList", agentNotInUserList) 

    # Create filtred CallParkGroup
    fileCPG = directory_path + '/CallParkGroup.csv'
    with open(fileCPG, 'w') as file3:
        writer = csv.writer(file3)
        writer.writerow(headers)
        writer.writerows(callParkFilteredList)

    ### Call Pickup Group ###
    callPickupList = []
    callPickupName = ""
    callPickup = {}
    appendCallPickup = False
    for rowCP in CallPickupGroup.iterrows():
        if (rowCP[1]['Feature Type'] == "CALL PICKUP GROUP"):
            if rowCP[1]['Config Name'] != callPickupName:
                callPickupName = rowCP[1]['Config Name']
                callPickup = {}
                callPickup['Name'] = rowCP[1]['Config Name']
                callPickup['Location'] = ""
                callPickup['Notification Type'] = ""
                callPickup['Notification Delay Timer In Seconds'] = ""
                callPickup['Agent Action'] = "ADD"
                userNum = 1
                if callPickupName:
                     appendCallPickup = True
                    
            if pd.isnull(rowCP[1]['Email ID']) == False:
                callPickup['Agent' + str(userNum) + ' ID'] = rowCP[1]['Email ID']
            elif pd.isnull(rowCP[1]['User']) == False:
                callPickup['Agent' + str(userNum) + ' ID'] = rowCP[1]['User']
            elif pd.isnull(rowCP[1]['Device']) == False:
                callPickup['Agent' + str(userNum) + ' ID'] = rowCP[1]['Device']
            else:
                callPickup['Agent' + str(userNum) + ' ID'] = rowCP[1]['Line']
            userNum = userNum + 1
            
        if (rowCP[1]['Feature Type'] == "CALL PICKUP GROUP") and callPickupName and appendCallPickup:
            callPickupList.append(callPickup)
    
    callPickupBulk = pd.DataFrame(callPickupList)
    callPickupBulk.fillna('', inplace=True)
    callPickupBulk = callPickupBulk.drop_duplicates()
    callPickupFilteredList = []
    userNotInUserList = []
    headers = list(callPickupBulk.columns)
    for indexCL, rowCPk in callPickupBulk.iterrows():
        try:
            print("Start filtering callParkBulk for user/device in Hunt Group " + rowCPk['Name'])
            for iindexUL, rowUL in userstomigrate.iterrows():
                # Creating filtered ConfiguredLineBulk
                userNum = 1
                appended = False
                for header in headers:
                    try: 
                        if 'Agent' in header:
                            try:
                                if ((pd.isnull(rowCPk['Agent' + str(userNum) + ' ID']) == False) and (rowCPk['Agent' + str(userNum) + ' ID'] == rowUL['EMAIL ID'])):
                                    if appended == False:
                                        rowCPk.fillna('', inplace=True)
                                        callPickupFilteredList.append(rowCPk)
                                        appended = True
                                if ((pd.isnull(rowCPk['Agent' + str(userNum) + ' ID']) == False) and (rowCPk['Agent' + str(userNum) + ' ID'] != rowUL['EMAIL ID'])):
                                    if rowCPk['Agent' + str(userNum) + ' ID'] not in agentNotInUserList:
                                        agentNotInUserList.append(rowCPk['Agent' + str(userNum) + ' ID'])
                                userNum = userNum + 1
                            except:
                                userNum = userNum + 1
                    except:
                        print("Issue in creating  with filtered callParkBulk for header ", header)
        except: 
            print("Error in processing for createLocationFeatureFilteredList for Call Pickup Group: ", rowCPk['Name'])  
    # Warn if there agents which are not in UserList
    if agentNotInUserList:
        print("WARNING: You have in agents in Call Pickup but not in userList", agentNotInUserList) 

    # Create filtred Call Pickup Group CSV
    fileCPU = directory_path + '/CallPickupGroup.csv'
    with open(fileCPU, 'w') as file4:
        writer = csv.writer(file4)
        writer.writerow(headers)
        writer.writerows(callPickupFilteredList)

def IdenfiyDNInMultipleDP(directory_path, DevicePool):

    ### Identify if DN exist in multiple device pool
    print("Inside IdenfiyDNInMultipleDP")
    devicePool = {}
    dnInDP = []
    headers = ["Directory Number", "Device Pool", "Device Pool"]
        
    for rowDP in DevicePool.iterrows():
        devicePool[rowDP[1][0].split(',')[0]] = rowDP[1][0].split(',')[1:]
    for key in devicePool.keys():
        
        for num in devicePool[key]:
            for numList in devicePool.keys():
                if (num in devicePool[numList]) and (numList != key):
                    dnInDP.append([num, key, numList])

    fileDNInMultipleDP = directory_path + '/DNInMultipleDevicePool.csv'
    with open(fileDNInMultipleDP, 'w') as file5:
        writer = csv.writer(file5)
        writer.writerow(headers)
        writer.writerows(dnInDP)
    print("Directory numbers which present in multiple Device Pools are listed in DNInMultipleDevicePool.csv ")

def main():

    csvDir = "" 
    userList = ""
    insightDir = ""
    
    # total arguments
    n = len(sys.argv)
    print("Total arguments passed:", n - 1)

    if n == 1:
        print("Usage: " + '\n' + "1) python UserBasedUCMFeatureMigration.py DNInMultipleDP insightDir=(see below)" + '\n')
        print("2) python UserBasedUCMFeatureMigration.py csvDir=(see below) UserList=(see below) insightDir=(see below)" + '\n')
        print("Parameters:")
        print("DNInmultipleDP -> Identify Directory numbers which present in multiple Device Pools and list in DNInMultipleDevicePool.csv in insightDir" + '\n')
        print("csvDir=<Path to directory where UCM Feature Migration tool output .zip is unziped>"+ '\n')
        print("userList=<UserList file (same format as used in UCM migration tool) with path. Use EMAIL ID (not CUCM USER ID) and you can add Location column to overide user/device location." + '\n')
        print("insightDir=<Path to directory where UCM Migration Insight tool output .zip is unziped>. This is needed for Call Park and Pickup group WxC CSVs needs to be creeated from Migration Insight output" + '\n')
        print('\n' + "This tool provide 4 main functionality: " + '\n')
        print('1) User list based filtering of output from "Migrate features from UCM" tool. You can override user/device location also using a Location column.')
        print('2) Identify users which are part of group features but not present in provided User list')
        print('3) Identify Directory numbers which present in multiple Device Pools and list in DNInMultipleDevicePool.csv in insightDir')
        print('4) Create Call park and Call Pickup group WxC CSV files which currently "Migrate features from UCM" tool doesnt generate' + '\n')
        exit()

    # Arguments passed
    print("\nName of Python script:", sys.argv[0])
    print("Argument passed are:")

    if len(sys.argv) == 3 and sys.argv[1] == "DNInMultipleDP":
        print("DNInMultipleDP")
        print(sys.argv[2] + '\n')
        insightDir = ""
        param = sys.argv[2].split("=")
        if param[0] == "insightDir":
            insightDir = param[1]
        DevicePool = pd.read_csv(insightDir + '/DevicePoolNumbers.txt', sep='\r', header=None)
        IdenfiyDNInMultipleDP(insightDir, DevicePool)
        exit()

    for i in range(1, n):
        param = sys.argv[i].split("=")
        print(param[0] + " = " + param[1])
        if param[0] == "csvDir":
            csvDir = param[1]
        if param[0] == "userList":
            userList = param[1]
        if param[0] == "insightDir":
            insightDir = param[1]
    print('\n')
    
    print("Start Processing .... ") 
    ''' Read User List CSV '''
    
    userstomigrate = pd.read_csv(userList)

    ''' Read WxC CSV files output from UCM Feature Migration tool '''
    callForward_Internal = pd.read_csv(csvDir + '/UserFeatures_Internal.csv', low_memory=False)
    callForward_External = pd.read_csv(csvDir + '/UserFeatures_External.csv', low_memory=False)
    configuredLineBulk = pd.read_csv(csvDir + '/ConfiguredLineBulk.csv', low_memory=False)
    HuntGroupBulk = pd.read_csv(csvDir + '/HuntGroupBulk.csv', low_memory=False)
    CallQueueBulk = pd.read_csv(csvDir + '/CallQueueBulk.csv', low_memory=False)
    AutoAttendantBulk = pd.read_csv(csvDir + '/AutoAttendantBulk.csv', low_memory=False)
    
    ''' Read  CSV files output from UCM Migration Insight tool '''
    CallParkGroup = pd.read_csv(insightDir + '/HuntGroup_CallQueue_CallPark_CallPickUpGroups.csv', low_memory=False)
    CallPickupGroup = pd.read_csv(insightDir + '/HuntGroup_CallQueue_CallPark_CallPickUpGroups.csv', low_memory=False)
    SharedLineGroup = pd.read_csv(insightDir + '/shared_line_Group_migration_report.csv', low_memory=False)

    # Read deviceLineKeyConfiguration and convert into Dataframe
    deviceLineKey = []
    with open(csvDir + '/DeviceLineKeyConfigurationBulk.csv', 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            deviceLineKey.append(row)
    deviceLineKeyConfiguration = pd.DataFrame(deviceLineKey)
    deviceLineKeyConfiguration.columns = header

    # Read deviceLineKeyConfiguration and convert into Dataframe
    virtualLine = []
    with open(csvDir + '/VirtualLineBulk.csv', 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            virtualLine.append(row)
    virtualLineBulk = pd.DataFrame(virtualLine)
    virtualLineBulk.columns = header

    # Define the path for the new directory
    directory_path = csvDir + "/Filtered"

    # Create the directory
    # Check if the directory already exists
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)
    else:
        pass

    ''' Generate filtered WxC CSVs based on User List '''
    createUserDeviceVirtuallineFilteredList(directory_path, userstomigrate, virtualLineBulk, configuredLineBulk, deviceLineKeyConfiguration, callForward_Internal, callForward_External)
    createLocationFeatureFilteredList(directory_path, userstomigrate, HuntGroupBulk, CallQueueBulk, AutoAttendantBulk, CallParkGroup, CallPickupGroup, SharedLineGroup)

# Using the special variable  
# __name__ 
if __name__=="__main__": 
    main() 
    