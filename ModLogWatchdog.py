import praw
import csv
import json
import os
import re
import yaml
import textwrap
from discord_webhook import DiscordWebhook, DiscordEmbed

#===Constants===#
CONFIG_FILE = os.path.join(os.path.dirname(__file__),"config.yaml")
CACHE_FILE =  os.path.join(os.path.dirname(__file__), "cache.json")
BAD_WORDS = ['fuck']
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
    postCache = {}
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
    with open(CACHE_FILE, "w") as fout:
        for chunk in json.JSONEncoder().iterencode(postCache):
            fout.write(chunk)

def post_webhook(log, report):
    item_id = log.id
    is_submission = log._submission
    message = ''
    if is_submission:
        message += ('**Submission Title:** {}\n'.format(log.target_title))
    if report:
        message += ('**Report:** {}\n'.format(textwrap.shorten(report[0], width=1000, placeholder="...(Too long to preview full content)...")))
    if log.body:
        message += ('**Content:** {}\n'.format(textwrap.shorten(log.body, width=1000, placeholder="...(Too long to preview full content)...")))
    message += ('**Author:** {}\n'.format(log.author.name))
    message += ('**Permalink:** https://www.reddit.com{}\n'.format(log.permalink))
    webhook = DiscordWebhook(url=config["webhook"], content=message)
    webhook.execute()

if __name__ == "__main__":
    #Intialize 
    loadConfig()
    postCache = loadCache()
    reddit = initReddit()

    #Local vars
    submissions = {}
    logs = []
    #Only check for removelink actions, grab last X since we dont want to spend too much time grabbing post information
    while(True):
        try:
            for log in reddit.subreddit(config["subreddit"]).mod.stream.reports():
                item_id = log.id
                if log.mod_reports:
                    for report in log.mod_reports:
                        if config["report_phrase"] in report[0] and item_id not in postCache:
                            post_webhook(log, report)
                            postCache.append(item_id)
                            saveCache(postCache)
        except:
            if postCache:
                saveCache(postCache)