-- This table has a row per run of the software that persists tweets.
CREATE TABLE persistence_run (
    datetime DATE,
	tweet_count INTEGER,
	overlap_count INTEGER,
	min_tweet_datetime DATE,
	max_tweet_datetime DATE,
	min_tweet_id VARCHAR2(22),
	max_tweet_id VARCHAR2(22)
);
