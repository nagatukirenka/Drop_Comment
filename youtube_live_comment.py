import json
import time
import re
import httplib2
from time import sleep
from oauth2client import tools
from oauth2client import client
from oauth2client.file import Storage
from requests_oauthlib import OAuth1Session

#YouTubeLiveURL
LIVEURL='YouTubeLiveの配信URL'
 
#TwitterAPI
CONSUMER_KEY =  ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_SECRET = ''

twitter = OAuth1Session(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_SECRET)
tweet_url = "https://api.twitter.com/1.1/statuses/update.json"
del_url = "https://api.twitter.com/1.1/statuses/user_timeline.json"

def GetURL():
    urlP = LIVEURL[-11:]
 
    credentials_path = "./credentials.json"
    store = Storage(credentials_path)
    credentials = store.get()
 
    if credentials is None or credentials.invalid:
        f = "./client.json"
        scope = "https://www.googleapis.com/auth/youtube.readonly"
        flow = client.flow_from_clientsecrets(f, scope)
        #YouTubeAPI
        flow.user_agent = "YOUR API KEY"
        credentials = tools.run_flow(flow, Storage(credentials_path))
 
    http = credentials.authorize(httplib2.Http())
    url = "https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id="
    url += urlP

    res, data = http.request(url)
    data = json.loads(data.decode())
 
    try:
        chat_id = data["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
    except:
        #生放送読み込み失敗時
        return
 
    url = "https://www.googleapis.com/youtube/v3/liveChat/messages?part=snippet,authorDetails"
    url += "&liveChatId=" + chat_id
 
    Comment(data,url,http)
 
def Comment(data,url,http):
    check = ""
    Flag = False
    #コメント取得
    while True:
        res, data = http.request(url)
        data = json.loads(data.decode())
        if data.get("items"):
            for datum in data["items"]:
                snippet = datum.get("snippet")
                if snippet.get("textMessageDetails"):
                    textMessageDetails = snippet.get("textMessageDetails")
                    if textMessageDetails.get("messageText"):

                        comment = datum["snippet"]["textMessageDetails"]["messageText"]
                        name = datum["authorDetails"]["displayName"]

                        if Flag == True:
                            tweet = name + ':' + comment + ' Twitter連携タグ'
                            params = {"status" : tweet}
                            req = twitter.post(tweet_url, params = params)                                       
                            params ={'count' : 5}
                            res = twitter.get(del_url, params = params)
                            if res.status_code == 200: 
                                TL = json.loads(res.text) 
                                for tweet in TL:
                                    if re.search(r'Twitter連携タグ', tweet['text']):
                                        print(tweet['text'])
                                        del_req = twitter.post('https://api.twitter.com/1.1/statuses/destroy/{}.json'.format(tweet['id']))  
                        if check == name + ":" + comment:
                            Flag = True

        check = name + ":" + comment
        Flag = False
        time.sleep(1)
if __name__ =='__main__':
    GetURL()
