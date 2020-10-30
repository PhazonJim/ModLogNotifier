import praw
import json
import os
import yaml
import textwrap
from discord_webhook import DiscordWebhook, DiscordEmbed

#===Constants===#
CONFIG_FILE = os.path.join(os.path.dirname(__file__),"config.yaml")
CACHE_FILE =  os.path.join(os.path.dirname(__file__), "cache.json")

#===Globals===#
#Config file
config = None

def loadConfig():
    global config
    #Load configs
    try:
        config = yaml.load(open(CONFIG_FILE).read(), Loader=yaml.FullLoader)
    except:
        print("'config.yaml' could not be located. Please ensure 'config.example' has been renamed")
        exit()

def loadCache():
    postCache = []
    try:
        with open(CACHE_FILE, "r") as fin:
            postCache = json.load(fin)
    except Exception as e:
        print (e)
    return postCache

def initReddit():
    client = config["client"]
    reddit = praw.Reddit(**client)
    return reddit

def saveCache(postCache):
    postCache = postCache[-(config['cache_size']):]
    with open(CACHE_FILE, "w") as fout:
        for chunk in json.JSONEncoder().iterencode(postCache):
            fout.write(chunk)

def post_webhook(log, report, phrase):
    is_submission = isinstance(log, praw.models.Submission)
    recipient = config['report_config'][phrase]['recipient']
    webhook = config['report_config'][phrase]['webhook']
    message = ''
    if recipient:
        message += ('**Recipient:** {}\n'.format(recipient))
    if report:
        message += ('**Report:** {}\n'.format(textwrap.shorten(report[0], width=1000, placeholder="...(Too long to preview full content)...")))
    if is_submission:
        message += ('**Submission Title:** {}\n'.format(log.title))
        if log.selftext:
            message += ('**Content:** {}\n'.format(textwrap.shorten(log.selftext, width=500, placeholder="...(Too long to preview full content)...")))
    else:
        if log.body:
            message += ('**Content:** {}\n'.format(textwrap.shorten(log.body, width=1000, placeholder="...(Too long to preview full content)...")))
    message += ('**Author:** {}\n'.format(log.author.name))
    message += ('**Permalink:** https://www.reddit.com{}\n'.format(log.permalink))
    webhook = DiscordWebhook(url=webhook, content=message)
    webhook.execute()

if __name__ == "__main__":
    #Intialize 
    loadConfig()
    postCache = loadCache()
    reddit = initReddit()

    while(True):
        try:
            for log in reddit.subreddit(config["subreddit"]).mod.stream.reports():
                item_id = log.id
                if log.mod_reports:
                    for report in log.mod_reports:
                        for phrase in config["report_config"]:
                            if phrase.lower() in report[0].lower() and item_id not in postCache:
                                post_webhook(log, report, phrase)
                                postCache.append(item_id)
                                saveCache(postCache)
        except Exception as e:
            print(e)
            if postCache:
                saveCache(postCache)