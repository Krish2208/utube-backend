import requests
import tensorflow
import pandas as pd
import nltk
import numpy as np
import re

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

tokenizer = Tokenizer(num_words=5000)

lemma = WordNetLemmatizer()
corpus = []

model = tensorflow.keras.models.load_model(
    '.\model_1\\', custom_objects=None, compile=True, options=None
)

API_KEY = "AIzaSyCEHPlVs2jxqTIFGNkld8Ve1EXYWzepRM0"
base_url = "https://www.googleapis.com/youtube/v3"


def getChannelID(username):
    try:
        url = "https://youtube-search6.p.rapidapi.com/channel/id/"
        querystring = {"channelName": username}
        headers = {
            "X-RapidAPI-Host": "youtube-search6.p.rapidapi.com",
            "X-RapidAPI-Key": "106d180865msh251d3d0baad0b78p1f5c5djsnd17f019bbc77"
        }
        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        return response.json()['channel_id']
    except:
        return "Error"


def getVideoList(channel_id):
    try:
        all_video_info = []
        url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={channel_id}&part=snippet,id&order=date&maxResults=50"
        response = requests.request("GET", url)
        list_of_Dict = response.json()
        for video_info in list_of_Dict["items"]:
            info = {}
            info['Id'] = video_info['id']['videoId']
            info['Description'] = video_info['snippet']['description']
            info['Title'] = video_info['snippet']['title']
            info['Thumbnail'] = video_info['snippet']['thumbnails']['high']['url']
            all_video_info.append(info)
        return all_video_info, list_of_Dict["items"][0]['snippet']['channelTitle']
    except:
        return "Error", "Error"


def GetComment(video_id):
    url = f'https://www.googleapis.com/youtube/v3/commentThreads?key={API_KEY}&textFormat=plainText&part=snippet&videoId={video_id}&maxResults=100'
    response = requests.request("GET", url)
    x = response.json()
    comments = []
    total = x["pageInfo"]["totalResults"]
    if "nextPageToken" in x.keys():
        pageToken = x["nextPageToken"]
        for i in range(10):
            if int(total)<100 or "nextPageToken" not in x.keys():
                break
            url2 = f'https://www.googleapis.com/youtube/v3/commentThreads?key={API_KEY}&pageToken={pageToken}&textFormat=plainText&part=snippet&videoId={video_id}&maxResults=100'
            response2 = requests.request("GET", url2)
            x2 = response2.json()
            for comment in x2['items']:
                comments.append(comment['snippet']['topLevelComment']['snippet']['textOriginal'])
            pageToken = x2["nextPageToken"]
    for comment in x['items']:
        comments.append(comment['snippet']
                        ['topLevelComment']['snippet']['textOriginal'])
    return comments


def GetStats(id):
    stat = {}
    url = f'https://www.googleapis.com/youtube/v3/videos?part=statistics%2csnippet&id={id}&key={API_KEY}'
    response = requests.request("GET", url)
    x = response.json()
    stat['views'] = x['items'][0]['statistics']['viewCount']
    stat['likes'] = x['items'][0]['statistics']['likeCount']
    stat['comments'] = x['items'][0]['statistics']['commentCount']
    description = x['items'][0]['snippet']['description']
    return stat, description


def GetSentiment(comments):
    corpus2 = []
    data = {'comment': comments}
    df = pd.DataFrame(data)
    for i in range(0, len(df)):
        review2 = re.sub('[^a-zA-Z]', ' ', df['comment'][i])
        review2 = review2.lower()
        review2 = review2.split()
        review2 = [lemma.lemmatize(
            word) for word in review2 if not word in stopwords.words('english')]
        review2 = ' '.join(review2)
        corpus2.append(review2)
    tokenizer.fit_on_texts(corpus2)
    test_sequences = tokenizer.texts_to_sequences(corpus2)
    test_padded = pad_sequences(
        test_sequences, maxlen=50, truncating='post', padding='post')
    keras_predict = model.predict(test_padded)
    k = ["Corrective", "Imperative", "Interogative",
        "Misc.", "Negative", "Positive"]
    ans = []
    for i in keras_predict:
        ans.append(k[np.argmax(i)])
    return ans