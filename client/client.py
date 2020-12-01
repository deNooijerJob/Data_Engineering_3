'''
Import all dependencies
'''
import json
import tweepy
from tweepy.streaming import StreamListener
import requests
import time
import os

import credentials # credentials file for twitter authentication

#Authenticate witht the twitter API
auth = tweepy.OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_SECRET)

#setup the Tweepy api
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=False)

#Hashtag list to listnen to
hashtag_lst = os.environ['HASHTAGS']

#Buffer of tweets to be processed
tweet_buffer = []

#init running varibles
avg_sentiment = 0.0
num_observations = 0


'''
Send a prediction request to the predict api
'''
def predict(tweets):
    payload = json.dumps({"tweets": tweets}) # tweets to be predicted

    # http headers
    headers = {
        "Content-Type": "application/json"
    }

    prediction = requests.post(os.environ['location_api'], data=payload, headers=headers).json() #send request
    updateN(len(prediction['predictions'])) #update number of tweets parsed
    update_avg(prediction['predictions']) # update average sentiment

'''
updates the global number of tweets parsed
'''
def updateN(n):
    global num_observations
    num_observations = num_observations + n

'''
updates the average sentiment and updates the visualisation
'''
def update_avg(predictions):
    for p in predictions:
        global avg_sentiment
        global num_observations
        s = float(p[0])
        avg_sentiment = avg_sentiment + ((s - avg_sentiment) / num_observations)

    payload = json.dumps({"avg": avg_sentiment})

    headers = {
        "Content-Type": "application/json"
    }

    update = requests.post(os.environ['vis_api'], data=payload, headers=headers).json() # update visualisation
    print('avg sentiment = ' + str(avg_sentiment))

'''
processes incoming tweets and batches them in sets of ten before predicting to limit api calls (can be changed)
'''
def process_tweets(tweet):
    if tweet["lang"] == "en":
        tweet_buffer.append(tweet['text'])
        if (len(tweet_buffer) > 10):
            predict_buffer = tweet_buffer[:10]
            for x in predict_buffer:
                tweet_buffer.remove(x)
            predict(predict_buffer) # make the prediction


# Method to format a tweet from tweepy # TODO dont touch this
def reformat_tweet(tweet):
    x = tweet

    processed_doc = {
        "id": x["id"],
        "lang": x["lang"],
        "retweeted_id": x["retweeted_status"]["id"] if "retweeted_status" in x else None,
        "favorite_count": x["favorite_count"] if "favorite_count" in x else 0,
        "retweet_count": x["retweet_count"] if "retweet_count" in x else 0,
        "coordinates_latitude": x["coordinates"]["coordinates"][0] if x["coordinates"] else 0,
        "coordinates_longitude": x["coordinates"]["coordinates"][0] if x["coordinates"] else 0,
        "place": x["place"]["country_code"] if x["place"] else None,
        "user_id": x["user"]["id"],
        "created_at": time.mktime(time.strptime(x["created_at"], "%a %b %d %H:%M:%S +0000 %Y"))
    }

    if x["entities"]["hashtags"]:
        processed_doc["hashtags"] = [{"text": y["text"], "startindex": y["indices"][0]} for y in
                                     x["entities"]["hashtags"]]
    else:
        processed_doc["hashtags"] = []

    if x["entities"]["user_mentions"]:
        processed_doc["usermentions"] = [{"screen_name": y["screen_name"], "startindex": y["indices"][0]} for y in
                                         x["entities"]["user_mentions"]]
    else:
        processed_doc["usermentions"] = []

    if "extended_tweet" in x:
        processed_doc["text"] = x["extended_tweet"]["full_text"]
    elif "full_text" in x:
        processed_doc["text"] = x["full_text"]
    else:
        processed_doc["text"] = x["text"]

    return processed_doc


# Custom listener class
class StdOutListener(StreamListener):  # Don't touch this
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just pushes tweets to pubsub
    """

    def __init__(self):
        super(StdOutListener, self).__init__()
        self._counter = 0

    def on_data(self, data):
        data = json.loads(data)
        #print(data)
        try:
            process_tweets(reformat_tweet(data))
        except KeyError:
            pass
        self._counter += 1
        return True

    def on_status(self, status):
        print(status.text)

    def on_error(self, status):
        if status == 420:
            print("rate limit active")
            return False


# Start listening
tweets_api = StdOutListener()
stream = tweepy.Stream(auth, tweets_api, tweet_mode='extended')
stream.filter(track=hashtag_lst)


