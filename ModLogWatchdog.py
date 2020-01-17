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

def initReddit():
    client = config["client"]
    reddit = praw.Reddit(**client)
    return reddit

def loadCache():
    postCache = {}
    try:
        with open(CACHE_FILE, "r") as fin:
            postCache = json.load(fin)
    except Exception as e:
        print (e)
    return postCache

def getAutoModConfig(reddit):
    #Grab the removal reasons from the wiki
    wikiPage = reddit.subreddit(config["wiki_subreddit"]).wiki[config["removal_reasons_wiki"]].content_md
    return yaml.load(wikiPage, Loader=yaml.FullLoader)

def saveCache(postCache):
    with open(CACHE_FILE, "w") as fout:
        for chunk in json.JSONEncoder().iterencode(postCache):
            fout.write(chunk)

def post_webhook(log):
    message = ''
    message += ('Removal Reason: ' + log.details + '\n')
    message += ('Comment Body: ' + textwrap.shorten(log.target_body, width=1000, placeholder="...(Too long to preview full content)...") + '\n')
    message += ('Author: ' + log.target_author + '\n')
    message += ('Permalink: ' + 'www.reddit.com' + log.target_permalink + '\n')
    webhook = DiscordWebhook(url=config["webhook"], content=message)
    webhook.execute()

if __name__ == "__main__":
    #Intialize 
    loadConfig()
    postCache = loadCache()
    reddit = initReddit()
    moderator = reddit.subreddit(config["subreddit"]).mod

    #removalReasons = getAutoModConfig(reddit)
    #Local vars
    submissions = {}
    #Only check for removelink actions, grab last X since we dont want to spend too much time grabbing post information
    for log in moderator.log(action="removecomment",limit=config["mod_log_depth"]):
        comment_id = log.target_fullname.split("_")[1]

        post_webhook(log)
        #if comment_id not in postCache:
        #comment_object = reddit.comment(id=comment_id)
        #print (comment_object.)
    #Write out
    if postCache:
        saveCache(postCache)