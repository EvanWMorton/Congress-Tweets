import json

# Reads a JSON config file and returns a dictionary with its contents.
# 
# In the case of a config file with auth info, the keys are based on what
# the Twitter developer site calls the variables when you receive them, not on what Tweepy
# (and presumably Twitter) calls them in doc on authorization.  So they are:
#     api_key
#     api_secret_key
#     bearer_token
#     access_token
#     access_token_secret
def read_config(filename):
    with open(filename, "r") as jsonfile:
        config_data = json.load(jsonfile)
        #print("config read successful")
    return config_data
