-- This table contains raw data about tweets.  Each row is in effect a tiny subset of the twitter data structure called "status".
CREATE TABLE raw_tweet (
    -- The author of the original tweet.  The 15 is the max per Twitter.
    author_name VARCHAR(4000),
	author_screen_name VARCHAR(15),
	datetime TIMESTAMP,
	-- If ID were stored as an integer, it would have to be LONG.  That type does not support many operations,
	-- including at least one we need: MAX.
	id VARCHAR(22),
	full_text VARCHAR(4000)
);

-- insert into raw_tweet values ('Joe Smith','jsmith',TO_DATE('2001-01-01','YYYY-MM-DD'),'356','This is a message.');
