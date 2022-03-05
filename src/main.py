import os
import time
import json

from dotenv import load_dotenv
import tweepy

load_dotenv()

users: list = os.environ["twitter_users"].split(",")
keywords: list = os.environ["twitter_keywords"].split(",")
client: tweepy.Client = tweepy.Client(os.environ["bearer_token"])


class Tweet:
    def __init__(
        self,
        user_id: int,
        username: str,
        tweet_id: int,
    ):
        self.timestamp = int(time.time())
        self.user_id = user_id
        self.id = tweet_id
        self.username = username
        self.tweet_url = self.make_tweet_url()

    def make_tweet_url(self):
        return f"https://twitter.com/{self.username}/status/{self.id}"


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

    def user_lookup(self, users: list[str]) -> list[tweepy.User]:
        return client.get_users(usernames=users)

    def latest_user_tweets(self):
        return client.get_users_tweets(self.user["id"])

    def search_timeline(self, keywords: list[str] = []) -> list[Tweet]:
        tweets: list[Tweet] = []
        latest_tweets = self.latest_user_tweets()[0]
        for tweet in latest_tweets:
            for i in keywords:
                if i in tweet.text.lower():
                    tweets.append(
                        Tweet(self.user["id"], self.user["username"], tweet.id).__dict__
                    )
        return tweets


class Cache:
    def __init__(self, cachename: str, count = 10,ttl: int = 3600):
        self.cachename = cachename
        self.cachedir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "../cache/"
        )
        self.cachefile = os.path.join(self.cachedir, f"{self.cachename}.json")
        self.cachedir_exsists = self.create_cachedir()
        self.ttl = ttl
        self.current_cache = self.load()
        self.cache = []
        self.load()
        self.validate()

    def load(self):
        if not self.cachedir_exsists:
            raise Exception("Cache dir does not exists")
        if not os.path.exists(self.cachefile):
            with open(self.cachefile, "x") as cache:
                cache.close()

        with open(self.cachefile, "r") as cache:
            self.cache = json.load(cache)

    def save(self):
        if not self.cachedir_exsists:
            raise Exception("Cache dir does not exists")

        if not os.path.exists(self.cachefile):
            with open(self.cachefile, "x+") as cache:
                json.dumps(self.cache, cache, indent=4)
        else:
            with open(self.cachefile, "w+") as cache:
                json.dump(self.cache, cache, indent=4)

    def add(self, item: Tweet = None, items: list[Tweet] = None):
        if item is not None and not items is None:
            raise TypeError("Excpected one item or a list of items, not both")
        if item is not None:
            self.cache.append(item)
        elif items is not None:
            self.cache.extend(items)
        else:
            raise TypeError("item or a list of items is required")


    def remove(self, id: int):
        pass

    def validate(self):
        now: int = int(time.time())
        for seq, item in enumerate(self.cache):
            if item["timestamp"] >= (now - self.ttl):
                self.cache.pop(seq)

    def check_duplicate(self):
        cache_id: list[int] = []
        for item in self.cache:
            cache_id.append(item["id"])

        if sorted(list(set(cache_id))) == sorted(cache_id):
            return

        for seq, item in enumerate(cache_id):
            pass

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


def main():
    usersobj: list[User] = []
    usersobj.extend(User.lookup_users(users))
    print(usersobj)
    tweets: list[Tweet] = []
    for user in usersobj:
        t = Twitter(user)
        timeline = t.search_timeline(keywords)
        tweets.extend(timeline)
    cache_tweets = Cache("tweets")
    cache_tweets.save()


if __name__ == "__main__":
    main()
