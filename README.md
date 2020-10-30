# ModLogWatchdog
A reddit bot that watches for certain phrases in the report reason field for submisisons and comments in the reddit mod log and reports it to a discord webhook

# Environment setup instructions
1. Install Python 3
2. Install PIP (https://pip.pypa.io/en/stable/installing/)
3. pip install -r requirements.txt

# Configurations
1. Rename config.example to config.yaml
2. Ensure user info, subreddit name, number of items to check in moderator log, etc are set up in config.yaml
3. in the report_config section of the config file, each key represents a phrase you are looking for in the report reason field in reported items in the mod log.
3. Make sure that that you have a user mention (can be False for no mention or a discord user/role ID) and discord webhook set up for each search phrase

# Usage
1. Get Discord notifications for specific modlog items 
    - run RemovalBot.py

# Features
1. Send discord notifications with optional user pings when specific items popup in your modlog. Based on Automoderators "report_reason" feature. 
2. It seems to work. 
3. Allows for user and role pings

# TODO
1. More error handling
2. Additional customizations