#   Title:                  GRM_SaveFileParser
#   Author:                 Aaron Topping (Arkaan)
#   Description:            Opens a save file and parses the data.

# IMPORTS
import copy
import re

imported_Data = {}

def ParseAllData():
    with open('C:\\Users\\aaron\\OneDrive\\Programming\\GRM_SaveFileParser\\Test Files\\Guild_Roster_Manager.lua', encoding='utf-8') as data:

        c = 0
        leftPlayers = []
        currentMembers = []
        logReport = []
        settings = []
        alts = []
        backupData = []
        saveTables = [ "GRM_GuildMemberHistory_Save = {" , "GRM_LogReport_Save = {" , "GRM_AddonSettings_Save = {" , "GRM_GuildDataBackup_Save = {" , "GRM_Alts = {" , "GRM_DailyAnnounce = {" ]
        SeparatedTables = [ leftPlayers , currentMembers , logReport , settings , backupData , alts ]
        
        currentArray = []
        currentSaveIndex = 0
        for line in data:
            c += 1
            
            currentArray.append ( line )

            if saveTables[currentSaveIndex] in line:
                SeparatedTables[currentSaveIndex] = copy.deepcopy ( currentArray )
                currentArray = []
                currentSaveIndex += 1

            if currentSaveIndex == 6:
                break

        print(f'Report: Total lines copied - {c}')
        print(f"Left Player: {len(SeparatedTables[0]):<30}" )
        print(f"Current Player: {len(SeparatedTables[1]):<30}" )
        print(f"Log: {len(SeparatedTables[2]):<30}" )
        print(f"Setting: {len(SeparatedTables[3]):<30}" )
        print(f"BackupData: {len(SeparatedTables[4]):<30}" )
        print(f"Log: {len(SeparatedTables[5]):<30}" )
        print()

        ParseGuilds ( SeparatedTables[0] )

def ParseGuilds ( data ):

    GuilData = {}
    
    pattern1 = r'\t'
    tabCount = 0
    creationDate = ''

    c = 0
    for line in data:
        numTabs = len(re.findall ( pattern1 , line ) )

        if ( tabCount == 0 or tabCount == 1 ) and numTabs == 1:
            name = re.search ( r'\[\"(.*)\"\]' , line )
            print(f"Guild Found: {name.group(1)}")
            # Start of Guild
            

        elif tabCount == 2 and numTabs == 1:
            # Closing out the guild

            tabCount = 0
            print(f'End Of Guild: {c}')
            c = 0
            print()
            
        elif ( ( tabCount == 1 or tabCount == 2 ) and numTabs == 2 ):
            # Start of a player
            if '[\"grmCreationDate\"] =' in line:
                creationDate = re.search ( r'= \"(.*)\"' , line )
                print(f'Guild Creation Date: {creationDate.group(1)}')
            elif not '[\"grmName\"] =' in line:
                c += 1  
        elif tabCount == 3 and numTabs == 2:
            # End of a player
            c += 0    

        tabCount = numTabs

def StartProgram():

    print()
    answer = input("Do you want to Start? (Y/N) ")
    if answer == 'y':
        ParseAllData()
    else:
        print("Exiting")

StartProgram()