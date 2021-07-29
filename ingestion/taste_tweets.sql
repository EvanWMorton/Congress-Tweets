-- Look at the most recent stuff in raw_tweet, limiting columns to prevent wrap.
select
-- author_name,
author_screen_name,
to_char(datetime,'DD HH24:MI:SS') "day, time",
--id,
substring(full_text,1,35)
from raw_tweet
order by datetime desc
limit 10;

