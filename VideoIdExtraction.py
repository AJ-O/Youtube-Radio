import os
import json
import config
import pandas as pd

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def authoriziation():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials = credentials, developerKey = config.API_KEY)

    return youtube #return resource

def usersChannelPlaylists(youtube, pageToken): #Get users' channel playlist

    if pageToken is None:

        request = youtube.playlists().list(part = "snippet", maxResults = 50, mine = True)
        response = request.execute()

    else:

        request = youtube.playlists().list(part = "snippet", maxResults = 50, mine = True, pageToken = pageToken)
        response = request.execute()

    return response

        
def otherChannelsPlaylists(youtube, channelId, pageToken): 

    if pageToken is None:

        request = youtube.playlists().list(part = "snippet", channelId = channelId, maxResults = 50)
        response = request.execute()

    else:

        request = youtube.playlists().list(part = "snippet", channelId = channelId, maxResults = 50, pageToken = pageToken)
        response = request.execute()
        
    return response

def savePlaylistId(response):

    data = response
    playlistdictionary = {}
    playlistid = []
    playlisttitle = []

    for item in data['items']:

        playlistid.append(item['id'])
        playlisttitle.append(item['snippet']['title'])

    playlistdictionary['PID'] = playlistid
    playlistdictionary['PIT'] = playlisttitle

    df = pd.DataFrame(playlistdictionary)
    ids = df['PID'].tolist()

    return ids
        
def getVideoId(ids, youtube):
    
    videodf = pd.DataFrame()
    
    for id in ids: #run for every playlist id

        #base program to extract video id
        response = youtube.playlistItems().list(part = "snippet", playlistId = id, maxResults = 50)
        response = response.execute()
        df = saveDataFrame(response)
        videodf = videodf.append(df)

        while True:#execute when video in the playlist exceed 50
            
            try:

                if response['nextPageToken']:
                    
                    response = executeVideoId(youtube, pageToken = response['nextPageToken'])
                    df = saveDataFrame(response)
                    videodf = videodf.append(df)

            except:

                break
        #maindf = maindf.append(df, ignore_index = True)
        #lastindex = maindf['VID'].count()
        #maindf.loc[lastindex] = ['playlist' + str(i), 'playlist' + str(i)]

    return videodf

def executeVideoId(youtube, pageToken = None):

    if pageToken is None:
        
        response = youtube.playlistItems().list(part = "snippet", playlistId = id, maxResults = 50)
        response = response.execute()

    else:

        response = youtube.playlistItems().list(part = "snippet", playlistId = id, maxResults = 50, pageToken = pageToken)
        response = response.execute()

    return response

def saveDataFrame(data):

    videoidlist = []
    videotitle = []
    videodict = {}
    
    for item in data['items']:

        videoidlist.append(item['snippet']['resourceId']['videoId'])
        videotitle.append(item['snippet']['title'])

    videodict['VID'] = videoidlist
    videodict['VT'] = videotitle

    df = pd.DataFrame(videodict)#convert dictionary to dataframe
    return df

def main():
    
    youtube = authoriziation() #get authorization from the user for access to their account
    pafyDF = pd.DataFrame() #this dataframe will contain video id and description of all the playlists combined 

    self_or_not = int(input("1)Your channels' playlist\n2)Other channels' playlists\n"))

    if self_or_not == 1:

        #run the base program once for users own channel

        response = usersChannelsPlaylists(youtube, None)#get playlists of users channel
        ids = savePlaylistId(response)#save the playlist ids extracted from response in a dataframe
        df = getVideoId(youtube, ids)#extract video ids contained in the playlist, returns a dataframe
        pafyDF = pafyDF.append(df, ignore_index = True)#append that dataframe to the main dataframe, ignore index will continue the values and will not start the dataframe with 0

        try:
            #after that check if more results exist, 
            #then pass nextPageToken as an argument
            if response['nextPageToken']:
                
                nextPageToken = response['nextPageToken']
                response = usersChannelsPlaylists(youtube, nextPageToken)
                ids = savePlaylistId(response)
                df = getVideoId(youtube, ids)
                pafyDF = pafyDF.append(df, ignore_index = True)

        except:
            
            print(pafyDF)

    #run the base program once for other channel, selected by user

    else:
        
        channelId = input("Enter channel id: ")#channel id of the required channels' playlist
        response = otherChannelsPlaylists(youtube, channelId, None)#get playlists of entered channel
        ids = savePlaylistId(response)#save the playlist ids extracted from response in a dataframe
        df = getVideoId(ids, youtube)#extract video ids contained in the playlist, returns a dataframe
        pafyDF = pafyDF.append(df, ignore_index = True)#append that dataframe to the main dataframe, ignore index will continue the values and will not start the dataframe with 0

        try: 
            #after that check if more results exist, 
            #then pass nextPageToken as an argument

            if response['nextPageToken']:
                
                nextPageToken = response['nextPageToken']
                response = otherChannelsPlaylists(youtube, channelId, nextPageToken)
                ids = savePlaylistId(response)
                df = getVideoId(ids, youtube)
                pafyDF = pafyDF.append(df, ignore_index = True)

        except:
            
            print(pafyDF)

        return pafyDF

def test():

    print('test')
#main()