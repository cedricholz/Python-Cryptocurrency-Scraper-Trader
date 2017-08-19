import praw
import json

with open("reddit_secrets.json") as secrets_file:
    reddit_secrets = json.load(secrets_file)
    secrets_file.close()

reddit = praw.Reddit(client_id=reddit_secrets["client_id"], client_secret=reddit_secrets["client_secret"],
                     password=reddit_secrets["password"], user_agent=reddit_secrets["user_agent"],
                     username=reddit_secrets["username"])


print(reddit.user.me())