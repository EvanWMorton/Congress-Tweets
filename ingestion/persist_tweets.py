import sys
import datetime
import time

import oracle_db
import twitter


# This fetches recent tweets and persists them, meaning stores them in the database.
def persist_tweets(raw_tweet_table_name, persistence_run_table_name):

    run_start = datetime.datetime.utcnow()
    odb = oracle_db.OracleDb()
    
    # Find the last (highest-id) old tweet, meaning of a tweet we've already persisted.
    query_result = odb.run_query("select max(id) from " + raw_tweet_table_name)
    #print ("length of query_result is " + str(len(query_result)))
    answer = query_result[0][0]
    if answer == None:
        # Special case of empty table.  Use an arbitrary old tweet id.
        last_old_tweet_id = '1386138077077381121'
    else:
        last_old_tweet_id = answer; 
    print ("last_old_tweet_id = " + str(last_old_tweet_id))
    #exit()
    
    #     We want to get all new tweets, that is, all tweets that we don't already have.  The normal way to accomplish this would be
    # to pass last_old_tweet_id.  However, this is not guaranteed to get *all* new tweets, as Twitter limits your lookback.  As an example,
    # suppose you got the first 1000 tweets.  Later, after 2000 more tweets have been added, you ask for all new tweets.  Instead of
    # providing all of them (#1001-3000), it might provide only the last part of that set, e.g. #1573-3000.
    #     There is nothing we can do after the fact about those missing tweets.  To prevent/reduce the problem, we can run this
    # more frequently.  What we can do in this code is to *detect* the problem.  We'd like to do so by asking for every tweet from
    # last_old_tweet_id forward, but the interface is inflexible on the strictness of the inequality.  That is, it uses "greater than"
    # and doesn't support "greater than or equal to".  Therefore we pass an id slightly earlier than the last id,
    # hoping to receive the last old one plus the new ones.  In other words, we try to overlap by one tweet.  We check for the old
    # one, note whether it was present, and delete it if it is.
    #     To get an id slightly earlier than the last old id, we just subtract 1.  This almost certainly is not a legitimate id,
    # but works in Twitter's filters.
    last_old_tweet_id_as_int = int(last_old_tweet_id)
    tweet_list = ta.get_tweets(200, last_old_tweet_id_as_int-1)

    # Determine the highest and lowest ids and times, and look for the overlapped one discussed above.
    highest_id = 0
    lowest_id = sys.maxsize
    lowest_datetime = datetime.datetime.strptime('9999-01-01','%Y-%m-%d')    
    highest_datetime = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')    
    copy_of_tweet_list = []
    overlap_tweet_count = 0
    for tweet in tweet_list:
        id = tweet.get_id()
        dtime = tweet.get_datetime()
        if id == last_old_tweet_id_as_int:
            overlap_tweet_count = overlap_tweet_count + 1
        else:
            copy_of_tweet_list.append(tweet)
            if id > highest_id:
                highest_id = id
            if id < lowest_id:
                lowest_id = id
            if dtime > highest_datetime:
                highest_datetime = dtime
            if dtime < lowest_datetime:
                lowest_datetime = dtime
        #print (id)
    # At this point, overlap_tweet_count will be 1 in the good case and 0 in the bad case (in which we missed data).
    if overlap_tweet_count > 1:
        print("overlap_tweet_count too high: " + str(overlap_tweet_count))
        exit()
    for tweet in copy_of_tweet_list:
        query = "INSERT INTO " + raw_tweet_table_name + " VALUES (:author_name,:author_screen_name,TO_DATE(:date_string,'" + oracle_db.OracleDb.get_date_format_string() + "'),:id,:full_text)"
        # Left-pad the id with zeros, so that in the unlikely event that the length in digits ever changes, the alphabetical MAX we uses
        # in the query for the highest value will match the numerical max.
        padded_id = format(tweet.get_id(),'022d')   # FIXME magic number
        dtime = tweet.get_datetime()
        date_string = dtime.strftime('%y-%m-%d-%H-%M-%S')
        print ("date_string = " + date_string)
        dict = { "author_name": tweet.get_author_name(), \
                 "author_screen_name": tweet.get_author_screen_name(), \
                 "date_string": date_string, \
                 "id": padded_id, \
                 "full_text": tweet.get_full_text() \
               }
        #print ("query is:" + query)
        odb.run_statement_with_variables(query,dict)
    print(str(datetime.datetime.today()) + " length of copy is " + str(len(copy_of_tweet_list)) + ", overlap_tweet_count = " + str(overlap_tweet_count))
    # Having persisted the tweet data, persist a little data about this run.
    query = "INSERT INTO " + persistence_run_table_name + " VALUES (:run_start, \
                                                 :tweet_count,:overlap_count, \
                                                 :min_tweet_create_date,\
                                                 :max_tweet_create_date,\
                                                 :min_tweet_id,:max_tweet_id)"
    dict = {"run_start": run_start, \
            "tweet_count": len(copy_of_tweet_list), \
            "overlap_count": overlap_tweet_count, \
            "min_tweet_create_date": lowest_datetime, \
            "max_tweet_create_date": highest_datetime, \
            "min_tweet_id": lowest_id, \
            "max_tweet_id": highest_id, \
           }
    odb.run_statement_with_variables(query,dict)
    odb.commit()
    odb.close()
    return overlap_tweet_count

if len(sys.argv) < 2 or len(sys.argv) > 4:
    print(len(sys.argv))
    print("Usage: {0} sleep_seconds [raw_tweet_table_name [persistence_run_table_name]]".format(sys.argv[0]))
    exit()
raw_tweet_table_name = 'raw_tweet'
persistence_run_table_name = 'persistence_run'
sleep_seconds = sys.argv[1]
if len(sys.argv)>2:
    raw_tweet_table_name = sys.argv[2]
    if len(sys.argv)>3:
        persistence_run_table_name = sys.argv[3]

print ("args are sleep_seconds = {0}, raw_tweet_table_name = {1}, persistence_run_table_name = {2}".format(sleep_seconds,raw_tweet_table_name,persistence_run_table_name))

ta = twitter.twitter_account("twitter_config.private.json")

while True:
    overlap_tweet_count = persist_tweets(raw_tweet_table_name, persistence_run_table_name)
    if int(sleep_seconds) == 0:
        break
    time.sleep(int(sleep_seconds))
