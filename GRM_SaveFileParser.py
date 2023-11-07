#   Title:                  GRM_SaveFileParser
#   Author:                 Aaron Topping (Arkaan)
#   Description:            Opens a save file and parses the data.

# IMPORTS
import copy
import re
import json


# Variables
jsonFileDirectory = 'C:\\Users\\aaron\\OneDrive\\Programming\\GRM_SaveFileParser\\Output\\grm.json'
finaFormerPlayerData = {}
finalPlayerData = {}

def ParseAllData():
    global finaFormerPlayerData
    global finalPlayerData

    with open('C:\\Users\\aaron\\OneDrive\\Programming\\GRM_SaveFileParser\\Test Files\\Guild_Roster_Manager.lua', encoding='utf-8') as data:

        leftPlayers = []
        currentMembers = []
        logReport = []
        settings = []
        alts = []
        backupData = []
        saveTables = [ "GRM_GuildMemberHistory_Save = {" , "GRM_CalendarAddQue_Save = {" , "GRM_LogReport_Save = {" , "GRM_AddonSettings_Save = {" , "GRM_PlayerListOfAlts_Save = {" , "GRM_GuildDataBackup_Save = {" , "GRM_Misc = {" , "GRM_Alts = {" , "GRM_DailyAnnounce = {" ]
        SeparatedTables = [ leftPlayers , currentMembers , None , logReport , settings , None , backupData , None , alts ]
        
        currentArray = []
        currentSaveIndex = 0
        for line in data:
           
            currentArray.append ( line )

            if saveTables[currentSaveIndex] in line:

                if currentSaveIndex != 2 and currentSaveIndex != 5 and currentSaveIndex != 7:
                    SeparatedTables[currentSaveIndex] = copy.deepcopy ( currentArray )
                currentArray = []
                currentSaveIndex += 1

            if currentSaveIndex == 6:
                break

        finaFormerPlayerData = ParseGuilds ( SeparatedTables[0] )
        finalPlayerData = ParseGuilds ( SeparatedTables[1] )
        print()

        for gName , data in finalPlayerData.items():
            print(f'{gName} has {len(data) - 1} members.')
        print()
        ExportToJson( finalPlayerData )

def ParseGuilds ( data ):
    GuildData = {}
    
    namePattern = r'\[\"(.*)\"\]'
    pattern1 = r'\t'
    tabCount = 0
    creationDate = ''
    player = []

    for line in data:
        numTabs = len(re.findall ( pattern1 , line ) )

        if ( tabCount == 0 or tabCount == 1 ) and numTabs == 1:
            name = re.search ( namePattern , line ).group(1)

            if name != "":
                GuildData[name] = {}
            # Start of Guild
            

        elif tabCount == 2 and numTabs == 1:
            # Closing out the guild
            tabCount = 0
            name = ""
            
        elif ( ( tabCount == 1 or tabCount == 2 ) and numTabs == 2 ):
            # Possible Start of a player

            if '[\"grmCreationDate\"] =' in line:
                creationDate = re.search ( r'= \"(.*)\"' , line ).group(1)
            elif not '[\"grmName\"] =' in line:
                playerName = re.search ( namePattern , line ).group(1)

                if playerName != "grmNumRanks" and playerName != "ranks" and playerName != 'grmClubID':
                    # New player found!
                    GuildData[name][playerName] = []
                # else:
                #     print("FOUND:")
                        

        elif tabCount == 3 and numTabs == 2:
            # End of a player
            GuildData[name][playerName] = player
            GuildData[name]['grmCreationDate'] = creationDate
            playerName = ""
            player = []

        elif numTabs >= 3:
            player.append(line)

        tabCount = numTabs

    for guildName , data in GuildData.items():     
        for name , playerData in data.items():
            if name != 'grmCreationDate':
                GuildData[guildName][name] = ImportPlayerData ( playerData , name )

    return GuildData


def ImportPlayerData ( playerData , playerName ):
        player = {}
        pattern = r'= \"?(.*?)\"?,'
        pattern2 = r'^\s*\"?(.*?)\"?, -- \[\d\]'
        i = 0

        while i < len(playerData):

            if '[\"GUID\"]' in playerData[i]:
                player['GUID'] = re.search ( pattern , playerData[i] ).group(1)

            if '[\"note\"]' in playerData[i]:
                player['note'] = re.search ( pattern , playerData[i] ).group(1)

            if '[\"customNote\"]' in playerData[i]:
                player['customNote'] = []
                player['customNote'].append ( ConvertToBool( re.search ( pattern2 , playerData[i + 1] ).group(1) ) )
                player['customNote'].append ( int( re.search ( pattern2 , playerData[i + 2] ).group(1) ) )
                cNote = re.search ( pattern2 , playerData[i + 3] ).group(1)
                if cNote == '""':
                    cNote = ''
                player['customNote'].append ( cNote )
                player['customNote'].append ( int ( re.search ( pattern2 , playerData[i + 4] ).group(1) ) )
                player['customNote'].append ( ConvertToBool( re.search ( pattern2 , playerData[i + 5] ).group(1) ) )
                editor = re.search ( pattern2 , playerData[i + 6] ).group(1)
                if editor == '""':
                    editor = ''
                player['customNote'].append ( editor )
                i += 7

            if '[\"zone\"]' in playerData[i]:
                player['zone'] = re.search ( pattern , playerData[i] ).group(1)

            if '[\"class\"]' in playerData[i]:
                player['class'] = re.search ( pattern , playerData[i] ).group(1)

            if '[\"mainStatusChangeTime\"]' in playerData[i]:
                player['mainStatusChangeTime'] = int ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"bannedInfo\"]' in playerData[i]:
                player['bannedInfo'] = []
                player['bannedInfo'].append ( ConvertToBool( re.search ( pattern2 , playerData[i + 1] ).group(1) ) )
                player['bannedInfo'].append ( int ( re.search ( pattern2 , playerData[i + 2] ).group(1) ) )
                player['bannedInfo'].append ( ConvertToBool( re.search ( pattern2 , playerData[i + 3] ).group(1) ) )
                whoBanned = re.search ( pattern2 , playerData[i + 4] ).group(1)
                if whoBanned == '""':
                    whoBanned = ''
                player['bannedInfo'].append ( whoBanned )

                i += 5

            if '[\"status\"]' in playerData[i]:
                player['status'] = int ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"level\"]' in playerData[i]:
                player['level'] = int ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"joinDateUnknown\"]' in playerData[i]:
                player['joinDateUnknown'] = re.search ( pattern , playerData[i] ).group(1)

            if '[\"rankName\"]' in playerData[i]:
                player['rankName'] = re.search ( pattern , playerData[i] ).group(1)

            if '[\"altsAtTimeOfLeaving\"]' in playerData[i]:
                player['altsAtTimeOfLeaving'] = []

                c = 1
                if not '},' in playerData[i+c]:     # No need to process the logic if there are no alts.
                    done = False
                    
                    while not done:
                        alt = []
                        alt.append ( re.search ( pattern2 , playerData[i + c + 1] ).group(1) )
                        alt.append ( re.search ( pattern2 , playerData[i + c + 2] ).group(1) )
                        guid = re.search ( pattern2 , playerData[i + c + 3] ).group(1)
                        if guid == '""':
                            guid = ''
                        alt.append ( guid )
                        alt.append ( int( re.search ( pattern2 , playerData[i + c + 4] ).group(1) ) )

                        player['altsAtTimeOfLeaving'].append ( alt )    # Add the alt to the main setting
                        c+=6

                        if '},' in playerData[i+c]:
                            done = True
                i += c
                        
            if '[\"recommendToKick\"]' in playerData[i]:
                player['recommendToKick'] = ConvertToBool( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"birthdayUnknown\"]' in playerData[i]:
                player['birthdayUnknown'] = ConvertToBool( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"name\"]' in playerData[i]:
                player['name'] = re.search ( pattern , playerData[i] ).group(1)

            if '[\"safeList\"]' in playerData[i]:
                player['safeList'] = {}
                player['safeList']['kick'] = []
                player['safeList']['demote'] = []
                player['safeList']['promote'] = []

                player['safeList']['kick'].append ( ConvertToBool( re.search ( pattern2 , playerData[i + 2] ).group(1) ) )
                player['safeList']['kick'].append ( ConvertToBool( re.search ( pattern2 , playerData[i + 3] ).group(1) ) )
                player['safeList']['kick'].append ( int( re.search ( pattern2 , playerData[i + 4] ).group(1) ) )
                player['safeList']['kick'].append ( int( re.search ( pattern2 , playerData[i + 5] ).group(1) ) )
                player['safeList']['demote'].append ( ConvertToBool( re.search ( pattern2 , playerData[i + 8] ).group(1) ) )
                player['safeList']['demote'].append ( ConvertToBool( re.search ( pattern2 , playerData[i + 9] ).group(1) ) )
                player['safeList']['demote'].append ( int( re.search ( pattern2 , playerData[i + 10] ).group(1) ) )
                player['safeList']['demote'].append ( int( re.search ( pattern2 , playerData[i + 11] ).group(1) ) )
                player['safeList']['promote'].append ( ConvertToBool( re.search ( pattern2 , playerData[i + 14] ).group(1) ) )
                player['safeList']['promote'].append ( ConvertToBool( re.search ( pattern2 , playerData[i + 15] ).group(1) ) )
                player['safeList']['promote'].append ( int( re.search ( pattern2 , playerData[i + 16] ).group(1) ) )
                player['safeList']['promote'].append ( int( re.search ( pattern2 , playerData[i + 17] ).group(1) ) )

                i += 19

            if '[\"lastOnline\"]' in playerData[i]:
                player['lastOnline'] = float ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"recommendToDemote\"]' in playerData[i]:
                player['recommendToDemote'] = ConvertToBool ( re.search ( pattern , playerData[i] ).group(1) )
            
            if '[\"recommendToPromote\"]' in playerData[i]:
                player['recommendToPromote'] = ConvertToBool ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"altGroup\"]' in playerData[i]:
                player['altGroup'] = re.search ( pattern , playerData[i] ).group(1)

            if '[\"race\"]' in playerData[i]:
                player['race'] = re.search ( pattern , playerData[i] ).group(1)

            if '[\"altGroupModified\"]' in playerData[i]:
                player['altGroupModified'] = int ( re.search ( pattern , playerData[i] ).group(1) )
            
            if '[\"promoteDateUnknown\"]' in playerData[i]:
                player['promoteDateUnknown'] = ConvertToBool ( re.search ( pattern , playerData[i] ).group(1) )
            
            if '[\"reasonBanned\"]' in playerData[i]:
                player['reasonBanned'] = re.search ( pattern , playerData[i] ).group(1)

            if '[\"rankHist\"]' in playerData[i]:
                player['rankHist'] = []

                c = 1
                if not '},' in playerData[i+c]:     # No need to process the logic if there are no alts.
                    done = False
                    
                    while not done:
                        date = []
                        date.append ( re.search ( pattern2 , playerData[i + c + 1] ).group(1) )
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 2] ).group(1) ) )
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 3] ).group(1) ) )
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 4] ).group(1) ) )
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 5] ).group(1) ) )
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 6] ).group(1) ) )
                        date.append ( ConvertToBool ( re.search ( pattern2 , playerData[i + c + 7] ).group(1) ) )
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 8] ).group(1) ) )
            
                        player['rankHist'].append ( date )    # Add the alt to the main setting
                        c+=10

                        if '},' in playerData[i+c]:
                            done = True
                i += c  

            if '[\"joinDateHist\"]' in playerData[i]:
                player['joinDateHist'] = []

                c = 1
                if not '},' in playerData[i+c]:     # No need to process the logic if there are no alts.
                    done = False
                    
                    while not done:
                        date = []
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 1] ).group(1) ) )
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 2] ).group(1) ) )
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 3] ).group(1) ) )
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 4] ).group(1) ) )
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 5] ).group(1) ) )
                        date.append ( ConvertToBool ( re.search ( pattern2 , playerData[i + c + 6] ).group(1) ) )
                        date.append ( int ( re.search ( pattern2 , playerData[i + c + 7] ).group(1) ) )
            
                        player['joinDateHist'].append ( date )    # Add the alt to the main setting
                        c+=9

                        if '},' in playerData[i+c]:
                            done = True
                i += c

            if '[\"sex\"]' in playerData[i]:
                player['sex'] = int ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"isUnknown\"]' in playerData[i]:
                player['isUnknown'] = ConvertToBool ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"isMobile\"]' in playerData[i]:
                player['isMobile'] = ConvertToBool ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"timeEnteredZone\"]' in playerData[i]:
                player['timeEnteredZone'] = int ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"isOnline\"]' in playerData[i]:
                player['isOnline'] = ConvertToBool ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"isMain\"]' in playerData[i]:
                player['isMain'] = ConvertToBool ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"events\"]' in playerData[i]:
                player['events'] = [ [ [ 0 , 0 , 0 ] , False , "" ] , [ [ 0 , 0 , 0 ] , False , "" , 0 ] ]

                # Anniversary
                player['events'][0][0][0] = int ( re.search ( pattern2 , playerData[i + 3] ).group(1) )
                player['events'][0][0][1] = int ( re.search ( pattern2 , playerData[i + 4] ).group(1) )
                player['events'][0][0][2] = int ( re.search ( pattern2 , playerData[i + 5] ).group(1) )
                player['events'][0][1] = ConvertToBool ( re.search ( pattern2 , playerData[i + 7] ).group(1) )
                player['events'][0][2] = re.search ( pattern2 , playerData[i + 8] ).group(1)

                # Bday
                player['events'][1][0][0] = int ( re.search ( pattern2 , playerData[i + 12] ).group(1) )
                player['events'][1][0][1] = int ( re.search ( pattern2 , playerData[i + 13] ).group(1) )
                player['events'][1][0][2] = int ( re.search ( pattern2 , playerData[i + 14] ).group(1) )
                player['events'][1][1] = ConvertToBool ( re.search ( pattern2 , playerData[i + 16] ).group(1) )
                player['events'][1][2] = re.search ( pattern2 , playerData[i + 17] ).group(1)
                player['events'][1][3] = int ( re.search ( pattern2 , playerData[i + 18] ).group(1) )

                i += 20

            if '[\"officerNote\"]' in playerData[i]:
                player['officerNote'] = re.search ( pattern , playerData[i] ).group(1)
            
            if '[\"guildRep\"]' in playerData[i]:
                player['guildRep'] = int ( re.search ( pattern , playerData[i] ).group(1) )
            
            if '[\"mainAtTimeOfLeaving\"]' in playerData[i]:
                player['mainAtTimeOfLeaving'] = []

                if not '},' in playerData[i+1]:     # No need to process the logic if there are no alts.
                    player['mainAtTimeOfLeaving'].append ( re.search ( pattern2 , playerData[i+1] ).group(1) )
                    player['mainAtTimeOfLeaving'].append ( re.search ( pattern2 , playerData[i+2] ).group(1) )
                    i += 3
                    
            if '[\"achievementPoints\"]' in playerData[i]:
                player['achievementPoints'] = int ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"faction\"]' in playerData[i]:
                player['faction'] = int ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"MythicScore\"]' in playerData[i]:
                player['MythicScore'] = int ( re.search ( pattern , playerData[i] ).group(1) )

            if '[\"HC\"]' in playerData[i]:
                player["HC"] = {}
                player["HC"]["isDead"] = ConvertToBool ( re.search ( pattern , playerData[i + 1] ).group(1) )
                player["HC"]["timeOfDeath"] = [ 0 , 0 , 0 , 0 , 0 , False ]

                player["HC"]["timeOfDeath"][0] = int ( re.search ( pattern2 , playerData[i + 3] ).group(1) )
                player["HC"]["timeOfDeath"][1] = int ( re.search ( pattern2 , playerData[i + 4] ).group(1) )
                player["HC"]["timeOfDeath"][2] = int ( re.search ( pattern2 , playerData[i + 5] ).group(1) )
                player["HC"]["timeOfDeath"][3] = int ( re.search ( pattern2 , playerData[i + 6] ).group(1) )
                player["HC"]["timeOfDeath"][4] = int ( re.search ( pattern2 , playerData[i + 7] ).group(1) )
                player["HC"]["timeOfDeath"][5] = int ( re.search ( pattern2 , playerData[i + 8] ).group(1) )
                i += 10

            i += 1

        return player

def ConvertToBool ( text ):
    if text == 'true':
        return True
    else:
        return False
    
def ExportToJson ( data ):
    with open(jsonFileDirectory, "w") as json_file:
        json.dump ( data , json_file , indent = 4) 

def StartProgram():

    print()
    answer = input("Do you want to Start? (Y/N) ")
    if answer == 'y':
        ParseAllData()
    else:
        print("Exiting")

StartProgram()