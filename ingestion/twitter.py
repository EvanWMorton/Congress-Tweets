from datetime import timezone
import datetime
import tweepy

import read_config

# We use the term "twitter_status" to mean the object that Twitter and tweepy nonsensically call a "status", which represents a tweet.  In contrast, the class "tweet"
# is our stripped-down representation of a tweet.

class Tweet:
    def __init__(self, twitter_status, retweet_author_screen_names):
    #author_name, author_screen_name, create_datetime, id, full_text):
        print("processing twitter_status with id = " + str(twitter_status.id))
        outer_author_screen_name = twitter_status.author.screen_name;
        print ("outer_author_screen_name = " + outer_author_screen_name)
        # If the tweet is from a source we follow only because of what it retweets, take the retweeted tweet.  Otherwise just stay on the tweet we're on.
        if outer_author_screen_name in retweet_author_screen_names:
            real_twitter_status = twitter_status.retweeted_status
        else:
            real_twitter_status = twitter_status
        self.author_name = real_twitter_status.author.name
        self.author_screen_name = real_twitter_status.author.screen_name
        self.create_datetime = datetime.datetime(
            real_twitter_status.created_at.year,
            real_twitter_status.created_at.month,
            real_twitter_status.created_at.day,
            real_twitter_status.created_at.hour,
            real_twitter_status.created_at.minute,
            real_twitter_status.created_at.second)
        # Treat id as an integer, even though we persist it as a string.  This
        # allows us to subtract 1 from it, which we need for an inequality-strictness
        # reason described in persist_tweets.py.
        self.id = real_twitter_status.id
        self.full_text = real_twitter_status.full_text
    def get_author_name(self):
        return self.author_name
    def get_author_screen_name(self):
        return self.author_screen_name
    def get_datetime(self):
        return self.create_datetime
    def get_id(self):
        return self.id
    def get_full_text(self):
        return self.full_text
    def __str__(self):
        return self.author_name + "," + self.author_screen_name + "," + str(self.create_datetime) + "," + str(self.id) + "," + self.full_text

# Had to write this pretty-printer because pretty() fails on a twitter_status.  It may also help with other objects.  It's pretty hacky, especially the
# stuff to avoid infinite recursion.
#
# Return True if there was, or may have been, real content to print.
def pritty(d, indent=0, label=""):
    if indent > 5:
        print("went too deep, cutting off", file=outfile)
        return True
    class_name = type(d).__name__
    if class_name in ('builtin_function_or_method','method'):
        return False
    print('\t' * indent + label, end = '', file=outfile)
    attr_names = dir(d)
    attr_name_count = len(attr_names)
    attr_name_count = min(attr_name_count, 10000)
    any_genuine_attrs = False
    for i in range(attr_name_count):
        attr_name = attr_names[i]
        if (attr_name[0] != '_' and
                attr_name not in ('denominator','imag','numerator','real') and not
                (label.startswith('max') or label.startswith('min') or label.startswith('resolution'))):
            child = getattr(d,attr_name)
            if pritty(child, indent + 1, attr_name + ':'):
                any_genuine_attrs = True
    if not any_genuine_attrs:
        print('\t' * indent + str(str(d)), file=outfile)
    return True
    
# Remove an initial string from a longer string.  If it's not present, exit with an error.
#def strip_init(string, start):
#    if not string.startswith(start):
#        print ("Error in strip_init")
#        print (string)
#        print (start)
#        exit()
#    return string[len(start):9999]

outfile = open("twitter.out","w", encoding='utf-8')

class twitter_account:
    def __init__(self, config_file_name):
        auth_data = read_config.read_config(config_file_name)
        auth = tweepy.OAuthHandler(auth_data["api_key"], auth_data["api_secret_key"])
        auth.set_access_token(auth_data["access_token"], auth_data["access_token_secret"])
        self.api = tweepy.API(auth)
        self.retweet_author_screen_names = auth_data["retweet_author_screen_names"]
    def get_tweets(self, max_tweet_count, id_for_since_id):
        twitter_ststuses = self.api.home_timeline(q="foo", tweet_mode='extended', count=max_tweet_count, since_id=id_for_since_id)
        #print ("number of tweets = " + str(len(twitter_ststuses)))
        tweet_list = []
        for twitter_status in twitter_ststuses:
            pritty(twitter_status)
            tweet = Tweet(twitter_status, self.retweet_author_screen_names)
            tweet_list.append(tweet)
        return tweet_list
#        print ("length of tweet_list is " + str(len(tweet_list)))
#            print(tweet)
#        print (datetime.datetime.today())
#        print (datetime.datetime.now())
#        print (datetime.datetime.now(timezone.utc))
#        print (datetime.datetime.utcnow())

#ta = twitter_account("auth_config_congress.json")
#ta.get_tweets(10, "")
# "1385781058331942916")

