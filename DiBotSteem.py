import requests
import json
#pip install websocket-client
from websocket import create_connection

import random
from threading import Thread
import time

import tweepy

import pyttsx3
engine = pyttsx3.init()

#steem stuff
from beem import Steem
from steemengine.wallet import Wallet


try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

#Load variables 
config = ConfigParser()
config.read('config.ini')

#Set variables
botAccountAuthKey = config.get('variables', 'botAccountAuthKey')
streamerBlockchainUsername = config.get('variables', 'streamerBlockchainUsername')
streamerDLiveDisplayName = config.get('variables', 'streamerDLiveDisplayName')

persistedQuery = config.get('variables', 'persistedQuery')

enablePoints = config.get('extras', 'enablePoints')

if enablePoints == "true":
    enablePoints = True
else:
    enablePoints = False

if enablePoints == True:
    pointsSystemName = config.get('extras', 'pointsSystemName')

    enableGambling = config.get('extras', 'enableGambling')

    #Points distributed every minute
    pointsPerMinute = int(config.get('extras', 'pointsPerMinute'))


    #Give viewers points for donating LINO
    pointsForLemon = int(config.get('extras', 'pointsForLemon'))
    pointsForIceCream = int(config.get('extras', 'pointsForIceCream'))
    pointsForDiamond = int(config.get('extras', 'pointsForDiamond'))
    pointsForNinjaghini = int(config.get('extras', 'pointsForNinjaghini'))
    pointsForNinjet = int(config.get('extras', 'pointsForNinjet'))

    if enableGambling == "true":
        enableGambling = True
    else:
        enableGambling = False
else:
    enableGambling = False

print("Points System Enabled: " + str(enablePoints))
print("Gambling System Enabled: " + str(enableGambling))



#steem stuff
enableBased = config.get('based', 'enableBased')

if enableBased == "true":
    activeKey = config.get('based', 'activeKey')
    steemUsername = config.get('based', 'steemUsername')

    stm = Steem(keys=[activeKey])
    wallet = Wallet(steemUsername, steem_instance=stm)

    autoLinoToBased = config.get('based', 'autoLinoToBased')
    if autoLinoToBased == "true":
        autoLinoToBased = True
    else:
        autoLinoToBased = False

    enableBased = True
else:
    enableBased = False

print("Based system Enabled: " + str(enableBased))

try:
    with open('steemAccounts.txt') as json_file:
        data = json.load(json_file)
        steemAccounts = data
        print("steem accounts loaded!")

except:
    steemAccounts = {}
    print("Could not find existing steem accounts file")

    
    



opList = config.get('variables', 'opList')
opList = opList.splitlines()

tweetOnStreamStart = config.get("twitter", "tweetOnStreamStart")

if tweetOnStreamStart == True:
    print("Tweet on stream start enabled!")

    consumerKey = config.get("twitter", "consumerKey")
    consumerSecret = config.get("twitter", "consumerSecret")
    accessToken = config.get("twitter", "accessToken")
    accessTokenSecet = config.get("twitter", "accessTokenSecet")

    
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecet)
    api = tweepy.API(auth)

    api.update_status(status = "Streaming now on DLive! https://DLive.tv/"+streamerDLiveDisplayName)
    print("Tweet posted!")
else:
    print("Tweet on stream start disabled, not posting tweet")



ttsForDonations = config.get("tts", "ttsForDonations")
tts = config.get("tts", "tts")
ttsVoice = config.get("tts", "ttsVoice")

if ttsForDonations == "true":
    ttsForDonations = True
if tts == "true":
    tts = True

print("TTS for donations Enabled: " + str(ttsForDonations))
print("TTS for chat Enabled: " + str(tts))
print("TTS Voice: " + str(ttsVoice))


if ttsVoice == "female":
    try:
        engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
    except:
        print("Could not set TTS voice to female")



#Variables
lottery = False
entered = []

giveaway = False
giveawayEntered = []

engagementList = []
timer = 0

timedMessage = []
timedTimer = 0



#variables
try:
    with open('commands.txt') as json_file:
        data = json.load(json_file)
        commands = data
        print("Commands loaded!")

except:
    commands = {}
    print("Could not find existing commands")


try:
    with open('points.txt') as json_file:
        data = json.load(json_file)
        points = data
        print("Points loaded!")

except:
    points = {}
    print("Could not find existing points")
    
    points = {"disportum": 100,}


try:
    with open('giveaway.txt') as json_file:
        data = json.load(json_file)
        giveawayInfo = data

        if giveawayInfo["giveaway"] == 1:
            giveaway = True
        else:
            giveaway = False
            
        giveawayEntered = giveawayInfo["giveawayEntered"]
        ticketPrice = giveawayInfo["ticketPrice"]
        
        print("Giveaway loaded!")

except:
    giveawayEntered = []
    giveaway = False
    ticketPrice = 0
    print("Could not find existing giveaway")








def sendMessage(message):
    url = 'https://graphigo.prd.dlive.tv'
    
    headers = {
            'accept': '*/*',
            'authorization': botAccountAuthKey,
            'content-type': 'application/json',
            'fingerprint': '',
            'gacid': 'undefined',
            'Origin': 'https://dlive.tv',
            'Referer': 'https://dlive.tv/'+streamerDLiveDisplayName,
            'User-Agent':
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }

    data = {
            'operationName': 'SendStreamChatMessage',
            'variables': { "input":
                        {
                        'streamer': streamerBlockchainUsername,
                        'message': message,
                        'roomRole': 'Moderator',
                        'subscribing': True
                        }
                        },
            'extensions':{
                    "persistedQuery":{
                                    "version":1,
                                    "sha256Hash":persistedQuery
                                    }
                        },          
            
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)

    responseData = json.loads(response.text)

    #print(responseData)

    


def createConnection():
    print("")
    print("Creating connection")
    print("")
    global ws
    
    ws = create_connection("wss://graphigostream.prd.dlive.tv", suppress_origin=True)

    ws.send(json.dumps({
        'type': 'connection_init',
        'payload': {},
    }))
    ws.send(json.dumps({
                'id': '1',
                'type': 'start',
                'payload': {
                    'variables': {
                        'streamer': streamerBlockchainUsername
                    },
                    'extensions': {},
                    'operationName': 'StreamMessageSubscription',
                    'query':
                        'subscription StreamMessageSubscription($streamer: String!) {\n  streamMessageReceived(streamer: $streamer) {\n    type\n    ... on ChatGift {\n      id\n      gift\n      amount\n      recentCount\n      expireDuration\n      ...VStreamChatSenderInfoFrag\n    }\n    ... on ChatHost {\n      id\n      viewer\n      ...VStreamChatSenderInfoFrag\n    }\n    ... on ChatSubscription {\n      id\n      month\n      ...VStreamChatSenderInfoFrag\n    }\n    ... on ChatChangeMode {\n      mode\n    }\n    ... on ChatText {\n      id\n      content\n      ...VStreamChatSenderInfoFrag\n    }\n    ... on ChatFollow {\n      id\n      ...VStreamChatSenderInfoFrag\n    }\n    ... on ChatDelete {\n      ids\n    }\n    ... on ChatBan {\n      id\n      ...VStreamChatSenderInfoFrag\n    }\n    ... on ChatModerator {\n      id\n      ...VStreamChatSenderInfoFrag\n      add\n    }\n    ... on ChatEmoteAdd {\n      id\n      ...VStreamChatSenderInfoFrag\n      emote\n    }\n  }\n}\n\nfragment VStreamChatSenderInfoFrag on SenderInfo {\n  subscribing\n  role\n  roomRole\n  sender {\n    id\n    username\n    displayname\n    avatar\n    partnerStatus\n  }\n}\n'
                }
    }))



def saveCommands():
    try:
        with open('commands.txt', 'w') as outfile:
            json.dump(commands, outfile)
    except:
        print("Could not save commands")

def saveSteemAccounts():
    try:
        with open('steemAccounts.txt', 'w') as outfile:
            json.dump(steemAccounts, outfile)
    except:
        print("Could not save steem accounts")

def savePoints():
    try:
        with open('points.txt', 'w') as outfile:
            json.dump(points, outfile)
    except:
        print("Could not save points")


def saveGiveaway():

    if giveaway == True:
        giveawayInfo = {"giveaway": 1, "ticketPrice": ticketPrice, "giveawayEntered": giveawayEntered}
    else:
        giveawayInfo = {"giveaway": 0, "ticketPrice": 0, "giveawayEntered": giveawayEntered}
    
    try:
        with open('giveaway.txt', 'w') as outfile:
            json.dump(giveawayInfo, outfile)
    except Exception as e:
        print(e)



        

def getUptime():
    try:
        response = requests.get("https://live.prd.dlive.tv/hls/live/"+streamerBlockchainUsername+".m3u8")
        response2 = requests.get(response.text.splitlines()[-1])

        time = response2.text.splitlines()[6]
        time = time.replace('.ts', "")
        time = int(time)*2/60
        #If minutes are more than 60, change format to hours    
        if time > 60:
            time = time/60
            time = round(time, 1)
            time = (str(time) + " hours")

        #Add text to minute amount
        else:
            time = round(time, 1)
            time = (str(time) + " minutes")
            

        sendMessage("Stream has been online for " + time)
    except:
        sendMessage("Stream is offline!")

def distributePoints():

    global timer

    global engagementList
    global points
    
    #distribute points for talking in chat

    while True:
        if enablePoints:
            if timer <= 60:
                timer += 1
                time.sleep(1)
                #print(timer)

            if timer > 60:
                
                try:
                    for user in engagementList:
                        
                        #if user is existing
                        try:
                            points[user] += pointsPerMinute
                        #if user is new
                        except:
                            points[user] = pointsPerMinute
                        

                    timer = 0
                    engagementList = []

                    savePoints()


                    print("")
                    print("Distributed points")
                    print("")
                except:
                    timer = 0
                    
                    print("")
                    print("No one is chatting to distribute points to!")
                    print("")
        else:
            pass
        


t1 = Thread(target=distributePoints, args=())
t1.start()



def sendTimedMessage():
    #if there's a timed message, send it every whatever minutes

    global timedTimer

    global timedMessage

    while True:
        try:
            #print(timedTimer)
            if timedTimer <= timedMessage[1]*60:
                timedTimer += 1
                time.sleep(1)

                #print(timedTimer)

            elif timedTimer > timedMessage[1]*60:
                timedTimer = 0

                message = timedMessage[0]
                #print(message)
                sendMessage(message)
                

                


                
                
        except Exception as e:
            #print(e)
            pass

t2 = Thread(target=sendTimedMessage, args=())
t2.start()



createConnection()

while True:
    try:
    
        result = ws.recv()
        result = json.loads(result)

        #get donos
        try:
            message = result["payload"]["data"]["streamMessageReceived"][0]["gift"]

            username = result["payload"]["data"]["streamMessageReceived"][0]["sender"]["displayname"]
            print(username + " send a " + message)

            #steem stuff
            try:
                if enableBased == True:
                    if autoLinoToBased == True:
                        try:

                            #sub = result["payload"]["data"]["streamMessageReceived"][0]["ChatExtendSub"]
                            
                            if message == "LEMON":
                                wallet.transfer(steemAccounts[username.lower()],0.1,"BASED", memo="Thanks for the Lemon!")
                                
                                print("")
                                print(username + " just got 0.1 BASED!")
                                print("")
                            elif message == "ICE_CREAM":
                                wallet.transfer(steemAccounts[username.lower()],1,"BASED", memo="Thanks for the Ice Cream!")
                                
                                print("")
                                print(username + " just got 1 BASED!")
                                print("")
                            elif message == "DIAMOND":
                                wallet.transfer(steemAccounts[username.lower()],10,"BASED", memo="Thanks for the Diamond!")
                                
                                print("")
                                print(username + " just got 10 BASED!")
                                print("")
                            elif message == "NINJAGHINI":
                                wallet.transfer(steemAccounts[username.lower()],100,"BASED", memo="Thanks for the Ninjaghini!")
                                
                                print("")
                                print(username + " just got 100 BASED!")
                                print("")
                            elif message == "NINJET":
                                wallet.transfer(steemAccounts[username.lower()],1000,"BASED", memo="Thanks for the Ninjet!")
                                
                                print("")
                                print(username + " just got 1000 BASED!")
                                print("")

                            
                        
                        except Exception as e:
                            print(e)
                            print(username + " needs to link their steem! (!link steemUsername)")
                    else:
                        pass
            except:
                pass





                

            if message == "LEMON":
                try:
                    points[username.lower()] += pointsForLemon
                except:
                    points[username.lower()] = pointsForLemon
                print(username + " received " + str(pointsForLemon) + " for donating a " + message)
            elif message == "ICE_CREAM":
                try:
                    points[username.lower()] += pointsForIceCream
                except:
                    points[username.lower()] = pointsForIceCream
                print(username + " received " + str(pointsForIceCream) + " for donating a " + message)
            elif message == "DIAMOND":
                try:
                    points[username.lower()] += pointsForDiamond
                except:
                    points[username.lower()] = pointsForDiamond
                print(username + " received " + str(pointsForDiamond) + " for donating a " + message)
            elif message == "NINJAGHINI":
                try:
                    points[username.lower()] += pointsForNinjaghini
                except:
                    points[username.lower()] = pointsForNinjaghini
                print(username + " received " + str(pointsForNinjaghini) + " for donating a " + message)
            elif message == "NINJET":
                try:
                    points[username.lower()] += pointsForNinjet
                except:
                    points[username.lower()] = pointsForNinjet
                print(username + " received " + str(pointsForNinjet) + " for donating a " + message)


            savePoints()



            if ttsForDonations == True:
                if message != "":
                    engine.say(username + " sent a " + message)
                    engine.runAndWait()
        except Exception as e:
            #print(e)
            message = ""
            username = ""

        #get messages
        try:
            message = result["payload"]["data"]["streamMessageReceived"][0]["content"]
            username = result["payload"]["data"]["streamMessageReceived"][0]["sender"]["displayname"]
            print(username + ": " + message)

            if tts == True:
                #Exclude empty messages, commands, and emotes in TTS
                if message != "" and "!" not in message and ":emote" not in message.lower():
                    engine.say(username + " says " + message)
                    engine.runAndWait()

        except:
            message = ""
            username = ""


        


        #add user to engagement list if has not chatted in the last minute cycle
        if username.lower() not in engagementList:
            if username.lower() != "":
                engagementList.append(username.lower())


        #timed messages
        try:
            if "!timedmsg" in message.lower() or "!timedmessage" in message.lower():
                if username.lower() in opList:
                    timedMessageArgs = message.split(None, 2)
                    #print(timedMessageArgs)

                    timedMessage = [timedMessageArgs[2], int(timedMessageArgs[1])]

                    sendMessage("@"+username+" Timed message set!")


        except Exception as e:
            print(e)
            sendMessage("@"+username+" !timedMessage [EVERY _ MINUTE/S] [TIMED MESSAGE HERE]")






        #Add cmds // commands
        try:
            if "!cmd" in message.lower() or "!command" in message.lower():
                if username.lower() in opList:
                    cmdArgs = message.split(None, 3)


                    cmdArgs[1] = cmdArgs[1].lower()
                    #make sure command is lowercased
                    cmdArgs[2] = cmdArgs[2].lower()

                    if cmdArgs[1] == "add":
                        
                        if "!" in cmdArgs[2]:
                            commands[cmdArgs[2]] = cmdArgs[3]
                            sendMessage("@" + username + " Added command" + cmdArgs[2])
                        else:
                            commands["!"+cmdArgs[2]] = cmdArgs[3]
                            sendMessage("@" + username + " Added command !" + cmdArgs[2])

                        saveCommands()

                    elif cmdArgs[1] == "delete" or cmdArgs[1] == "del":
                        try:
                            #Try to delete the cmd without a ! added
                            del commands[cmdArgs[2]]
                            sendMessage("@" + username + " Deleted command " + cmdArgs[2])
                        except KeyError:
                            #Try to delete the cmd with a ! added
                            try:
                                del commands["!"+cmdArgs[2]]
                                sendMessage("@" + username + " Deleted command !" + cmdArgs[2])
                            except:
                                sendMessage("@" + username + " Could not find a command by that name to delete")

                        saveCommands()
                else:
                    sendMessage("@"+username + " You are not an OP!")



            #custom user commands
            for cmd, response in commands.items():
                if cmd.lower() in message.lower():
                    sendMessage("@" + username + " " + response)


            if "!uptime" in message.lower():
                getUptime()
            #link to ebur.tv pepe directory
            if "!pepes" in message.lower():
                sendMessage("https://ebur.tv/pepes.html")



            #Send all commands
            if "!help" in message.lower():
                sendMessage("Commands are: " + "!pepes, !uptime, " + str(list(commands)).replace("[", "").replace("]", "").replace("'", "") )


            #steem stuff
            if enableBased == True:
                if "!link" in message.lower():
                    linkArgs = message.lower().split()

                    steemAccounts[username.lower()] = linkArgs[1].lower()
                    saveSteemAccounts()

                    sendMessage(username + " has been linked to " + linkArgs[1])

                #based airdrop
                if "!airdrop" in message.lower():
                    airdropArgs = message.lower().split( )

                    if len(airdropArgs) == 1:
                        sendMessage('@'+username+" Airdrop usage: (!airdrop) start | cancel | draw | join")

                    if len(airdropArgs) >= 2:
                        if airdropArgs[1].lower() == 'start':
                            if username.lower() in opList:
                                if len(airdropArgs) == 3:

                                    airdropEntered = []
                                    airdrop = True
                                    airdropTotal = airdropArgs[2]

                                    sendMessage('Airdrop now started for ' + airdropTotal + ' BASED! - Use (!airdrop join) to enter the airdrop!')
                                    

                        elif airdropArgs[1].lower() == "cancel":
                            if username.lower() in opList:
                                airdrop = False
                                airdropEntered = []

                                sendMessage('The airdrop has been cancelled!')

                        elif airdropArgs[1].lower() == 'draw':
                            if airdrop == True:
                                if username.lower() in opList:
                                    if len(airdropEntered) > 0:
                                        
                                        
                                        #Try to give everyone part of the airdrop
                                        airdropToGive = float(int(airdropTotal)/(len(airdropEntered)))
                                        #try:
                                        for user in airdropEntered:
                                            wallet.transfer(steemAccounts[user],airdropToGive,"BASED", memo="Airdropppppp")
                                        #except Exception as e:
                                            #print(e)
                                            #sendMessage("Could not distribute the airdrop. Do you have enough BASED to give?")

                                        airdropEntered = []

                                        sendMessage("Everyone has just been given " + str(airdropToGive) + " BASED!")

                                        airdrop = False

                                    else:
                                        sendMessage("There was no one to give anything to in the airdrop!")

                                else:
                                    sendMessage('@'+username+" You do not have permission!")

                            else:
                                sendMessage('@' + username + ' There is currently no airdrop running!!!!!!!!')

                        elif airdropArgs[1].lower() == 'join':
                            
                            if airdrop == True:
                                if username.lower() in airdropEntered:

                                    sendMessage('@' + username + " You have already entered the airdrop!!!!!!!!")
                                else:

                                    try:
                                        print(steemAccounts[username.lower()] + " joined the airdrop")
                                        
                                        airdropEntered.append(username.lower())

                                        sendMessage('@' + username + " Welcome to the airdrop! There are currently " + str(len(airdropEntered)) + " people in the airdrop.")
                                    except:
                                        sendMessage('@' + username + " You're not linked to your steem! (!link steemUsername)")
                            else:
                                sendMessage('@' + username + ' There is currently no airdrop running!!!!!!!!')

                #BASED lottery
                if "!basedlottery" in message.lower():
                
                    basedLotteryArgs = message.lower().split( )

                    if len(basedLotteryArgs) == 1:
                        sendMessage('@'+username+" Based Lottery usage: (!basedLottery) start | cancel | draw | join")

                    if len(basedLotteryArgs) >= 2:
                        if basedLotteryArgs[1].lower() == 'start':
                            if username.lower() in opList:
                                if len(basedLotteryArgs) == 3:

                                    basedEntered = []
                                    basedLottery = True
                                    basedLotteryPrize = basedLotteryArgs[2]

                                    sendMessage('Based Lottery now started for ' + basedLotteryPrize + ' BASED! - Use (!basedLottery join) to enter the Based Lottery!')
                                    

                        elif basedLotteryArgs[1].lower() == "cancel":
                            if username.lower() in opList:
                                basedLottery = False
                                basedEntered = []

                                sendMessage('The Based Lottery has been cancelled!')

                        elif basedLotteryArgs[1].lower() == 'draw':
                            if basedLottery == True:
                                if username.lower() in opList:
                                    if len(basedEntered) > 1:
                                        
                                        basedLotteryWinner = random.choice(basedEntered)

                                        try:

                                            wallet.transfer(steemAccounts[username.lower()],basedLotteryPrize,"BASED", memo="Congrates on winning the Based Lottery!")
                                        except:
                                            sendMessage("Could not give the winner the BASED! Do you have enough BASED to give?")

                                        basedEntered = []

                                        sendMessage('Congrates to @' + basedLotteryWinner + ' for winning the lottery! @' + basedLotteryWinner + ' now has ' + str(basedLotteryPrize) + ' BASED!')

                                        basedLottery = False

                                    else:
                                        
                                        basedEntered = []
                                        
                                        sendMessage('The Based Lottery has been cancelled because there were not enough participants. :(')

                                        basedLottery = False

                                else:
                                    sendMessage('@'+username+" You do not have permission!")

                            else:
                                sendMessage('@' + username + ' There is currently no Based Lottery running!!!!!!!!')

                        elif basedLotteryArgs[1].lower() == 'join':
                            
                            if basedLottery == True:
                                if username.lower() in basedEntered:

                                    sendMessage('@' + username + " You have already entered the Based Lottery!!!!!!!!")
                                else:

                                    try:
                                        print(steemAccounts[username.lower()] + " joined the based lottery")
                                        
                                        basedEntered.append(username.lower())

                                        sendMessage('@' + username + " Welcome to the pool! There are currently " + str(len(basedEntered)) + " people in the pool.")
                                    except:
                                        sendMessage('@' + username + " You're not linked to your steem! (!link steemUsername)")
                            else:
                                sendMessage('@' + username + ' There is currently no Based Lottery running!!!!!!!!')


            #point system commands
            if enablePoints:
                if "!give" in message.lower() and "!giveaway" not in message.lower():
                    try:
                        command = message.lower().split()
                        receiver = command[1]
                        amount = command[2]
                    except:
                        #sendMessage("Invalid syntax - !give [RECEIVER] [AMOUNT]")
                        pass

                    try:
                        if points[username.lower()] >= int(amount):
                            

                            #Check if user has points already
                            try:
                                
                                points[receiver] = points[receiver] + int(amount)
                                points[username.lower()] -= int(amount)

                                sendMessage('@'+username+" has given "+receiver+ " " + amount+" " + pointsSystemName + "! @" + receiver + " now has " + str(points[receiver]) + " " + pointsSystemName + "!")

                                savePoints()
                            except:
                                points[receiver] = int(amount)
                                
                                sendMessage('@'+receiver+" now has " + str(points[receiver]) + " " + pointsSystemName + "!")

                                savePoints()


                            
                        else:
                            sendMessage("@"+username+" You do not have enough to give!")


                    except:
                        pass

                
                if "!gift" in message.lower():
                    if username.lower() in opList:
                        try:
                            command = message.lower().split()
                            receiver = command[1]
                            amount = command[2]
                        except:
                            sendMessage("Invalid syntax - !gift [RECEIVER] [AMOUNT]")

                        #Check if user has points already
                        try:
                            points[receiver] = points[receiver] + int(amount)

                            sendMessage('@'+receiver+" was given "+amount+" " + pointsSystemName + "! @" + receiver + " now has " + str(points[receiver]) + " " + pointsSystemName + "!")

                            savePoints()
                        except:
                            points[receiver] = int(amount)
                            
                            sendMessage('@'+receiver+" now has " + str(points[receiver]) + " " + pointsSystemName + "!")

                            savePoints()
                            

                    else:
                        sendMessage('@'+username+" You are not an OP!")




                        
                
                if ("!"+pointsSystemName) in message.lower():
                    try:
                        sendMessage("@" + username + " You have " + str(points[username.lower()]) + " " + pointsSystemName)
                    except:
                        sendMessage("@" + username + " You have no " + pointsSystemName)

                #get top
                if "!top" in message.lower():
                    realList = dict(points)

                    sendMessage("@" + (max(realList, key=realList.get)) + " has " + str(max(realList.values())) + " " + pointsSystemName)




            #MINI GAME STUFF

            ####################################### Gamble Commands #######################################
            if "!gamble" in message.lower():
                gambleArgs = message.lower().split()

                try:

                    if int(gambleArgs[1]) > 0:
                        if points[username.lower()] >= int(gambleArgs[1]):
                    
                            chances = random.randint(0, 1)

                            if chances == 0:
                                gamble = "won"
                            else:
                                gamble = "lost"

                            if gamble == "won":
                                points[username.lower()] += int(gambleArgs[1])

                                sendMessage("@"+username+" You won! You have " + str(points[username.lower()]) + " " + pointsSystemName + "!")
                            else:
                                points[username.lower()] -= int(gambleArgs[1])

                                if points[username.lower()] < 0:
                                    points[username.lower()] = 0

                                sendMessage("@"+username+" You lost! You have " + str(points[username.lower()]) + " " + pointsSystemName + "!")



                            savePoints()

                        else:
                            sendMessage("@"+username+" You don't have enough " + pointsSystemName + " to gamble that much!")
                    else:
                        sendMessage("@"+username+" You must gamble a positive amount!")

                        
                except:
                    sendMessage("@"+username+ " Invalid format! !gamble [AMOUNT]")


            if "!allin" in message.lower():
                if points[username.lower()] > 0:
                    oldPoints = int(points[username.lower()])

                    chances = random.randint(0, 1)

                    if chances == 0:
                        gamble = "won"
                    else:
                        gamble = "lost"
                        
                    if gamble == "won":
                        points[username.lower()] += points[username.lower()]

                        sendMessage("@"+username+" You won "+ str(oldPoints) + " " + pointsSystemName + "! You have " + str(points[username.lower()]) + " " + pointsSystemName + "!")
                    else:
                        points[username.lower()] -= points[username.lower()]

                        if points[username.lower()] < 0:
                            points[username.lower()] = 0

                        sendMessage("@"+username+" You lost "+ str(oldPoints) + " " + pointsSystemName + "! You have " + str(points[username.lower()]) + " " + pointsSystemName + "!")


                    savePoints()


                else:
                    sendMessage("@"+username+" You have no "  + pointsSystemName + "!")



                    

                    
            ####################################### Lottery Commands #######################################
            if "!lottery" in message.lower() and "!basedlottery" not in message.lower():
                
                lotteryArgs = message.lower().split( )

                if len(lotteryArgs) == 1:
                    sendMessage('@'+username+" Lottery usage: (!lottery) start | cancel | draw | join ")

                if len(lotteryArgs) >= 2:
                    if lotteryArgs[1].lower() == 'start':
                        if username.lower() in opList:
                            if len(lotteryArgs) == 3:
                                
                                lottery = True
                                lotteryPrize = lotteryArgs[2]

                                sendMessage('Lottery now started for ' + lotteryPrize + '! - Use (!lottery join) to enter the lottery!')
                                

                    elif lotteryArgs[1].lower() == "cancel":
                        if username.lower() in opList:
                            lottery = False
                            entered = []

                            sendMessage('The Lottery has been cancelled!')

                    elif lotteryArgs[1].lower() == 'draw':
                        if lottery == True:
                            if username.lower() in opList:
                                if len(entered) > 1:
                                    
                                    lotteryWinner = random.choice(entered)
                                    points[lotteryWinner] += int(lotteryPrize)
                                    entered = []

                                    sendMessage('Congrates to @' + lotteryWinner + ' for winning the lottery! @' + lotteryWinner + ' now has ' + str(points[lotteryWinner]) + ' ' + pointsSystemName + '!')

                                    savePoints()

                                    lottery = False

                                else:
                                    
                                    entered = []
                                    
                                    sendMessage('The lottery has been cancelled because there were not enough participants. :(')

                                    lottery = False

                            else:
                                sendMessage('@'+username+" You do not have permission!")

                        else:
                            sendMessage('@' + username + ' There is currently no lottery running!!!!!!!!')

                    elif lotteryArgs[1].lower() == 'join':
                        
                        if lottery == True:
                            if username.lower() in entered:

                                sendMessage('@' + username + " You have already entered the lottery!!!!!!!!")
                            else:
                                entered.append(username.lower())

                                sendMessage('@' + username + " Welcome to the pool! There are currently " + str(len(entered)) + " people in the pool.")
                        else:
                            sendMessage('@' + username + ' There is currently no lottery running!!!!!!!!')



            ####################################### Giveaway Commands #######################################
            if "!giveaway" in message.lower():
                
                giveawayArgs = message.lower().split( )

                if len(giveawayArgs) == 1:
                    sendMessage('@'+username+" Giveaway usage: (!giveaway) start | cancel | draw | join (!buy)")

                if len(giveawayArgs) >= 2:
                    if giveawayArgs[1].lower() == 'start':
                        if username.lower() in opList:
                            if len(giveawayArgs) == 3:
                                if giveaway == False:
                                
                                    giveaway = True
                                    ticketPrice = int(giveawayArgs[2])

                                    sendMessage('Giveaway now started! Tickets are ' + str(ticketPrice) + ' each. (!buy)')
                                else:
                                    sendMessage("There is already a giveaway!")
                                

                    elif giveawayArgs[1].lower() == "cancel":
                        if username.lower() in opList:
                            if giveaway == True:
                                giveaway = False
                                giveawayEntered = []

                                sendMessage('The giveaway has been cancelled!')
                            else:
                                sendMessage("There is no giveaway to cancel!")

                    elif giveawayArgs[1].lower() == 'draw':
                        if giveaway == True:
                            if username.lower() in opList:
                                if len(giveawayEntered) > 1:
                                    
                                    giveawayWinner = random.choice(giveawayEntered)

                                    giveawayEntered = []

                                    sendMessage('Congrates to @' + giveawayWinner + ' for winning the giveaway!')
                                    print("")
                                    print(giveawayWinner + ' won the giveaway!')
                                    print('')

                                    giveaway = False

                                    saveGiveaway()

                                else:
                                    
                                    giveawayEntered = []
                                    
                                    sendMessage('The giveaway has been cancelled because there were not enough participants. :(')

                                    giveaway = False

                            else:
                                sendMessage('@'+username+" You do not have permission!")

                        else:
                            sendMessage('@' + username + ' There is currently no giveaway running!!!!!!!!')

                    elif giveawayArgs[1].lower() == 'join':
                        
                        if giveaway == True:
                            if points[username.lower()] >= ticketPrice:
                                giveawayEntered.append(username.lower())
                                points[username.lower()] -= ticketPrice

                                saveGiveaway()
                                savePoints()

                                sendMessage('@' + username + " Thank you for buying a ticket! There are currently " + str(len(giveawayEntered)) + " tickets.")
                            else:
                                sendMessage('@' + username + " You don't have enough to buy a ticket!")
                            
                            
                        else:
                            sendMessage('@' + username + ' There is currently no giveaway running!!!!!!!!')

            if "!buy" in message.lower() and "(!buy)" not in message.lower():
                if giveaway == True:
                    try:
                        if points[username.lower()] >= ticketPrice:
                            giveawayEntered.append(username.lower())
                            points[username.lower()] -= ticketPrice

                            saveGiveaway()
                            savePoints()

                            sendMessage('@' + username + " Thank you for buying a ticket! There are currently " + str(len(giveawayEntered)) + " tickets.")
                        else:
                            sendMessage('@' + username + " You don't have enough to buy a ticket!")
                    except:
                        sendMessage('@' + username + " You don't have enough to buy a ticket!")
                    
                    
                else:
                    sendMessage('@' + username + ' There is currently no giveaway running!!!!!!!!')

                    #print(giveawayEntered)
            
            
        except Exception as e: print(e)

    except:
        createConnection()

ws.close()


















