import datetime
import os
import time
from typing import Union, Tuple
import json

from dotenv import load_dotenv
import tweepy
import slack_sdk as slack

load_dotenv()

users: list = os.environ["twitter_users"].split(",")
keywords: list = os.environ["twitter_keywords"].split(",")
client: tweepy.Client = tweepy.Client(os.environ["bearer_token"])
slack_token: str = os.environ["slack_bot_token"]
slack_channel: str = os.environ["slack_channel"]

class User:
    def __init__(self, username: str, id: int, name: str):
        self.timestamp = int(time.time())
        self.username = username
        self.id = id
        self.name = name

    def lookup_users(users: list[str]) -> list:
        users = client.get_users(usernames=users)[0]
        list_users: list[User] = []
        for user in users:
            list_users.append(User(user.username, user.id, user.name).__dict__)
        return list_users

class Twitter:
    def __init__(self, user: User):
        self.user = user

    def latest_user_tweets(self):
        return client.get_users_tweets(self.user["id"])

    def search_timeline(self, keywords: list[str] = []) -> list[int]:
        tweets: list[int] = []
        latest_tweets = self.latest_user_tweets()[0]
        for tweet in latest_tweets:
            for i in keywords:
                if i in tweet.text.lower():
                    tweets.append(tweet.id)
        return tweets

class Tweet_cache:
    def __init__(self):
        self.cachename = "tweets"
        self.cachedir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "../cache/"
        )
        self.cachefile = os.path.join(self.cachedir, f"{self.cachename}.json")
        self.cachedir_exsists = self.create_cachedir()


    def load_sent_tweets(self) -> list[int]:
        with open(self.cachefile, "r") as tweets_file:
            data = json.load(tweets_file)
            return data

    def save_tweets(self,tweets: list[int]):
        if len(tweets) > 100:
            tweets = tweets[:50]
        with open(self.cachefile, "w+") as tweets_file:
            json.dump(tweets, tweets_file)

    def create_cachedir(self):
        if os.path.exists(self.cachedir):
            return True
        else:
            try:
                os.mkdir(self.cachedir)
            except Exception as e:
                return False
            else:
                return True

class Slack:
    def __init__(self):
        self.client = slack.WebClient(token=slack_token)

    def send_message(self, message: Union[str, list[str]]):
        print(dir(self.client))
        response = self.client.chat_postMessage(channel=slack_channel, text=f"@channel {message}")
        print(response)

def main():
    usersobj: list[User] = []
    usersobj.extend(User.lookup_users(users))
    slackbot = Slack()
    tweet_cache = Tweet_cache()
    sendt_tweets = tweet_cache.load_sent_tweets()
    for user in usersobj:
        tweets: list[int] = []
        send_tweets: list[int] = []
        tweet_link: list[str] = []
        t = Twitter(user)
        timeline = t.search_timeline(keywords)
        tweets.extend(timeline)
        for i in tweets:
            if i not in sendt_tweets:
                send_tweets.append(i)
        for i in send_tweets:
            tweet_link.append(f"https://twitter.com/{user['username']}/status/{i}")
        print(f"{datetime.datetime.now()}: send to slack {tweet_link}")
        sendt_tweets.extend(send_tweets)
        for msg in tweet_link:
            slackbot.send_message(msg)

    tweet_cache.save_tweets(sendt_tweets)


if __name__ == "__main__":
    main()