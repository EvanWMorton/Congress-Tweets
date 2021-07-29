-- This table has a row per run of the software that persists tweets.
CREATE TABLE persistence_run (
    datetime TIMESTAMP,
	tweet_count INTEGER,
	overlap_count INTEGER,
	min_tweet_datetime TIMESTAMP,
	max_tweet_datetime TIMESTAMP,
	min_tweet_id VARCHAR(22),
	max_tweet_id VARCHAR(22)
);
