

import requests
import json
#pip install websocket-client
from websocket import create_connection

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

opList = config.get('variables', 'opList')
opList = opList.splitlines()

#variables
try:
    with open('data/commands.txt') as json_file:
        data = json.load(json_file)
        commands = data
        print("Commands loaded!")

except:
    commands = {}
    print("Could not find commands")

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
                                    "sha256Hash":"e755f412252005c7d7865084170b9ec13547e9951a1296f7dfe92d377e760b30"
                                    }
                        },          
           
            
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)

def getUptime():
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

#Subscribe to chat
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

#Save to commands file
def saveCommands():
    try:
        with open('data/commands.txt', 'w') as outfile:
            json.dump(commands, outfile)
    except:
        print("Could not save commands")

while True:
    result = ws.recv()
    result = json.loads(result)

    try:
        message = result["payload"]["data"]["streamMessageReceived"][0]["content"]
        username = result["payload"]["data"]["streamMessageReceived"][0]["sender"]["displayname"]
        print(username + ": " + message)
    except:
        message = ""
        username = ""



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

        #Send all commands
        if "!help" in message.lower():
            sendMessage("Commands are: " + "!pepes, !uptime, " + str(list(commands)).replace("[", "").replace("]", "").replace("'", "") )


        #custom user commands
        for cmd, response in commands.items():
            if cmd.lower() in message.lower():
                sendMessage("@" + username + " " + response)


        #get stream uptime
        if "!uptime" in message.lower():
            getUptime()

        #link to ebur.tv pepe directory
        if "!pepes" in message.lower():
            sendMessage("https://ebur.tv/pepes.html")

        
    except Exception as e: print(e)

ws.close()


















