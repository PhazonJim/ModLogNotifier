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
    wikiPage = reddit.subreddit(config["wiki_subreddit"]).wiki[config["wiki_page"]].content_md
    return yaml.load_all(wikiPage, Loader=yaml.FullLoader)

def saveCache(postCache):
    with open(CACHE_FILE, "w") as fout:
        for chunk in json.JSONEncoder().iterencode(postCache):
            fout.write(chunk)

def check_log(log, action_reasons):
    for action_reason in action_reasons:
        if action_reason in log.details:
            return True

def post_webhook(log):
    item_id = log.target_fullname.split("_")[1]
    is_submission = log.action == 'removelink'
    message = ''
    message += ('**Removal Reason:** {}\n'.format(log.details))
    if is_submission:
        message += ('**Submission Title:** {}\n'.format(log.target_title))
    if log.target_body:
        message += ('**Content:** {}\n'.format(textwrap.shorten(log.target_body, width=1000, placeholder="...(Too long to preview full content)...")))
    message += ('**Author:** {}\n'.format(log.target_author))
    message += ('**Pushshift Link**: https://api.pushshift.io/reddit/{}/search?subreddits={}&ids={}\n'.format("submission" if is_submission else "comment", config["subreddit"], item_id) )
    message += ('**Permalink:** https://www.reddit.com{}\n'.format(log.target_permalink))
    print (message)
    #webhook = DiscordWebhook(url=config["webhook"], content=message)
    #webhook.execute()

if __name__ == "__main__":
    #Intialize 
    loadConfig()
    postCache = loadCache()
    reddit = initReddit()
    moderator = reddit.subreddit(config["subreddit"]).mod
    automod_config = getAutoModConfig(reddit)
    action_reasons = []
    for rule in automod_config:
        if rule and "modmail" in rule:
            if "action_reason" in rule:
                action_reasons.append(rule["action_reason"])
    #Local vars
    submissions = {}
    logs = []
    #Only check for removelink actions, grab last X since we dont want to spend too much time grabbing post information
    for log in moderator.log(action="removecomment",mod='AutoModerator',limit=config["mod_log_depth"]):
        item_id = log.target_fullname.split("_")[1]
        if item_id not in postCache:
            if check_log(log, action_reasons):
                logs.append(log)
    for log in moderator.log(action="removepost",mod='AutoModerator',limit=config["mod_log_depth"]):
        item_id = log.target_fullname.split("_")[1]
        if item_id not in postCache:
            if check_log(log, action_reasons):
                logs.append(log)
    for log in logs:
        post_webhook(log)
        item_id = log.target_fullname.split("_")[1]
        if item_id not in postCache:
            postCache.append(item_id)
    #Write out
    if postCache:
        saveCache(postCache)