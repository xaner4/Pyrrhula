import datetime
import os
import time
import json

import tweepy
import slack_sdk as slack
import yaml


configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "config.yml")
with open(configfile, "r") as f:
    config = yaml.safe_load(f)

users: list = config["twitter"]["users"]
keywords: list = config["twitter"]["keywords"]
client: tweepy.Client = tweepy.Client(config["twitter"]["bearer_token"])
slack_token: str = config["slack"]["token"]
slack_channel: str = config["slack"]["channel"]

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
            tweet_list = tweet.text.lower().split(" ")
            for i in keywords:
                if i.lower() in tweet_list:
                    tweets.append(tweet.id)
                    break
        return tweets

class Tweet_cache:
    def __init__(self):
        self.cachename = "tweets"
        self.cachedir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "../cache/"
        )
        self.cachefile = os.path.join(self.cachedir, f"{self.cachename}.json")
        self.cachedir_exsists = self.create_cachedir()
        self.cachefile_exists = self.create_cachefile()


    def load_sent_tweets(self) -> list[int]:
        with open(self.cachefile, "r") as tweets_file:
            data = json.load(tweets_file)
            return data

    def save_tweets(self,tweets: list[int]):
        print(f"Tweets Cached: {len(tweets)}")
        if len(tweets) > 100:
            tweets = tweets[60:]
        with open(self.cachefile, "w+") as tweets_file:
            json.dump(tweets, tweets_file)

    def create_cachedir(self):
        if os.path.exists(self.cachedir):
            return True
        else:
            try:
                os.mkdir(self.cachedir)
            except Exception:
                return False
            else:
                return True
    
    def create_cachefile(self):
        if os.path.exists(self.cachefile):
            return True
        else:
            with open(self.cachefile, "x+") as f:
                try: 
                    f.write("[]")
                except Exception:
                    return False
                finally:
                    return True

class Slack:
    def __init__(self):
        self.client = slack.WebClient(token=slack_token)

    def send_message(self, message: str):
        self.client.chat_postMessage(channel=slack_channel, text=message)

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
        for id in send_tweets:
            tweet_link.append(f"https://twitter.com/{user['username']}/status/{id}")

        print(f"{datetime.datetime.now()}: send to slack {tweet_link}")
        sendt_tweets.extend(send_tweets)
        for msg in tweet_link:
            slackbot.send_message(msg)

    tweet_cache.save_tweets(sendt_tweets)


if __name__ == "__main__":
    main()