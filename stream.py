import tweepy
import json
from tweepy import Cursor
from tweepy import API
import pandas as pd
import time
############# Twitter Client #############
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = Twitter_Auth().get_auth()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    # gets tweets from user time line
    def get_user_timeline_tweet(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline,id= self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends,id= self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id = self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return  home_timeline_tweets

    def get_followers(self,num_followers,user):
        followers = []
        for follower in Cursor(self.twitter_client.followers_ids, id = user).items(num_followers):
            followers.append(follower)
        return followers
    def get_tweets(self,words, date_since, numtweet):
        tweets = []
        for tweet in Cursor(self.twitter_client.search,q=words,lang="en",since=date_since, tweet_mode='extended').items(numtweet):
            tweets.append(tweet)
        return tweets




############# Twitter Authenticator #############
class Twitter_Auth():
    def __init__(self):
        self.consumer_key = '8HCOe72MfuMrDk0EGVCmAVAhD'
        self.consumer_secret = 'N6VWMv7d5NZqQfAzCnhWtciH8KFxqKrChwwB2eubwZoz2ho4sY'
        self.access_key = '1389216126371090432-rk7hfKOrhy7oFn7Hji827ER0C8MWBq'
        self.access_secret = '8nBXWvhKdxFF22pIVk9ie4OtVupQsXAMX9Q4GaWCXL2XC'

    def get_auth(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_key, self.access_secret)
        return auth

############# Twitter Streamer #############
class TwitterStreamer():
    def __init__(self):
        pass
    def stream_tweets(self, auth,listener, keywords):
        while True:
            myStream = tweepy.Stream(auth=auth, listener=listener)
            try:
                myStream.filter(track=keywords,languages=["en"])
            except:
                time.sleep(200)
                pass
            # myStream.filter(languages=["en"])

############# Twitter Stream Listener #############
class TwitterListener(tweepy.StreamListener):

    def on_data(self, data):
        tweets_analyzer = TweetAnalyzer()
        df = tweets_analyzer.tweets_from_json_to_data_frame(json.loads(data))

        # j_data = json.loads(data)

        print(df.head(5))

    def on_error(self, status_code):
        time.spleep(200)
        pass
        # if status_code == 420:
        #     # returning False in on_data disconnects the stream
        #     time.sleep(200)
        #     pass

class TweetData():
    def __init__(self,df):
        self.df = df
    def add_data(self,tweet):
        self.df.append(tweet)
    def get_data(self):
        return self.df

class TweetAnalyzer():
    """
    Functionality for analyzing content from tweets
    """
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[(tweet.full_text, tweet.id, tweet.author.id,tweet.user.screen_name,tweet.retweet_count,tweet.entities['hashtags'],tweet.user.followers_count) for tweet in tweets],
                          columns=['Tweet','Tweet ID','Author ID','User','Num_retweets','HashTags used','Follower Count'])
        df['followers_IDs'] = [twitter_clinet.get_followers(10, id) for id in df['Auther ID']]
        filename = 'scraped_tweets.csv'
        # we will save our database as a CSV file.
        df.to_csv(filename,mode='a')
        return df
    def tweets_from_json_to_data_frame(self,tweets):
        print(tweets['user'])
        print(tweets['user']['id'])
        df = pd.DataFrame(data=[(tweets['text'], tweets['id'],  tweets['user']['id'], tweets['retweet_count'],tweets['entities']['hashtags']) ],
                          columns=['Tweet', 'Tweet ID',  'Author ID', 'Num_retweets','Hashtags'])
        twitter_clinet = TwitterClient()
        df['followers_IDs'] = [twitter_clinet.get_followers(10, id) for id in df['Author ID']]
        print(df.head(1))
        filename = 'scraped_tweets_stream.csv'
        # we will save our database as a CSV file.
        df.to_csv(filename, mode='a',header=False)
        return df



if __name__ == '__main__':
    # twitter_auth = Twitter_Auth()
    # auth= twitter_auth.get_auth()
    # api = tweepy.API(auth)
    # myStreamListener = TwitterListener()
    # keywords = ['marvel']
    #
    # twitter_client = TwitterClient('pycon')
    # print(twitter_client.get_followers(5))
    # # streamer = TwitterStreamer()
    # # streamer.stream_tweets(api.auth,myStreamListener,keywords)
    df = pd.DataFrame( columns=['Tweet', 'Tweet ID', 'Author ID', 'Num_retweets', 'Hashtags','followers_IDs'])
    filename = 'scraped_tweets_stream.csv'
    # we will save our database as a CSV file.
    # df.to_csv(filename)
    tweetData = TweetData(df)
    twitter_clinet = TwitterClient()
    api = twitter_clinet.get_twitter_client_api()
    # these keywords are taken from below website
    # https://www.mcafee.com/blogs/consumer/family-safety/no-one-likes-many-ways-kids-bully-one-another-online/
    keywords = ['idiot','fuck','cry','ugly','stupid','fat','annoying','kill yourself','Dirl','Gcad','Foad','Fugly','IHML','KMS','KYS','FUB','GCAD','IWTKM','JLMA','bully', 'bullied', 'bullying']
    myStreamListener = TwitterListener()
    streamer = TwitterStreamer()
    streamer.stream_tweets(api.auth, myStreamListener, keywords)

    # tweets_analyzer = TweetAnalyzer()
    # print("Enter Date since The Tweets are required in yyyy-mm--dd")
    # date_since = input()
    # numtweet = 100
    # tweets = twitter_clinet.get_tweets(keywords,date_since,numtweet)
    # # print(dir(tweets[0]))
    #
    # df = tweets_analyzer.tweets_to_data_frame(tweets)

    print(df.head(5))


