import praw
import json
import requests

with open("reddit_secrets.json") as secrets_file:
    reddit_secrets = json.load(secrets_file)
    secrets_file.close()

reddit = praw.Reddit(client_id=reddit_secrets["client_id"], client_secret=reddit_secrets["client_secret"],
                     password=reddit_secrets["password"], user_agent=reddit_secrets["user_agent"],
                     username=reddit_secrets["username"])

# Check to see OAuth worked
print(str(reddit.user.me()) + '\n')
# .hot(limit=25):

# Print the first "limit" titles on r/cryptocurrency and print their sentiment
for submission in reddit.subreddit('CryptoCurrency').hot(limit=25):
    print(submission.title)

    # for x in submission.comments:
    #     print(x.body)

    r = requests.post("http://text-processing.com/api/sentiment/", data={'text': submission.title})
    processedText = json.loads(r.text)

    pos = processedText['probability']['pos']
    neutral = processedText['probability']['neutral']
    neg = processedText['probability']['neg']

    sentiment_pairs = {"Positive": pos, "Neutral": neutral, "Negative": neg}

    v = list(sentiment_pairs.values())
    k = list(sentiment_pairs.keys())
    print("Mostly " + k[v.index(max(v))])

    print("Positive " + str(pos))
    print("Neutral " + str(neutral))
    print("Negative " + str(neg) + "\n")







