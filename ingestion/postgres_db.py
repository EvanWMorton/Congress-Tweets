'''
This class attempts to isolate the Postgres-specific aspects of
database access, as well as certain schema information.
'''

import datetime
import time
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, select, func

import read_config

class postgres_client:
    ''' See module comment '''

    def __init__(self):
        # Get all the config info.
        db_config = read_config.read_config("db_config.private.json")
        username = db_config["username"]
        password = db_config["password"]
        endpoint = db_config["endpoint"]
        port = db_config["port"]
        database = db_config["database"]

        # Make the database connection and modify it.
        connection_string = f"postgresql://{username}:{password}@{endpoint}:{port}/{database}"
        print("connection_string = " + connection_string)
        self.engine = create_engine(
            connection_string,
            echo=False,
            execution_options={
                "isolation_level": "SERIALIZABLE"    # so nothing committed until we say so
            }
        )
        self.conn = self.engine.connect()
        self.metadata = MetaData()

        # Get metadata about all the tables.  Would you believe...both the tables?
        self.persistence_run = Table('persistence_run', self.metadata, autoload=True, autoload_with=self.engine)
        self.raw_tweet = Table('raw_tweet', self.metadata, autoload=True, autoload_with=self.engine)

        self.metadata.create_all(self.engine)
        self.transaction = None    # Can't do anything without a begin

    def get_max_id(self):
        maximum_id = self.conn.execute(
            select([
                   func.max(self.raw_tweet.c.id).
                       label('max_id')
                  ])
            ).scalar()
        return maximum_id;

    def begin (self):
        # BEGIN in the SQL transaction sense.
        self.transaction = self.conn.begin()
    def commit(self):
        ''' Perform a COMMIT. '''
        self.transaction.commit()
        self.transaction = None
    def close(self):
        ''' Close the database connection. '''
        self.conn.close()

    def insert_into_raw_tweet (self, dict):
        ins = self.raw_tweet.insert().values (
            author_name=dict['author_name'],
            author_screen_name=dict['author_screen_name'],
            datetime=dict['datetime'],
            id=dict['id'],
            full_text=dict['full_text']
        )

        #print (str(ins))
        self.conn.execute(ins)

    def insert_into_persistence_run (self, dict):
        ins = self.persistence_run.insert().values (
            datetime=dict['datetime'],
            tweet_count=dict['tweet_count'],
            overlap_count=dict['overlap_count'],
            min_tweet_datetime=dict['min_tweet_datetime'],
            max_tweet_datetime=dict['max_tweet_datetime'],
            min_tweet_id=dict['min_tweet_id'],
            max_tweet_id=dict['max_tweet_id']
        )
        #print (str(ins))
        self.conn.execute(ins)

    @staticmethod
    def get_date_format_string():
        ''' Get a date format which, in the TO_DATE function for this database, gives a
        format that works for INSERT statements. '''
        return 'YYYY-MM-DD-HH24-MI-SS'

if __name__ == "__main__":

    client = postgres_client()

    client.begin()
    dict = {
        'datetime':'28-Oct-1900',
        'tweet_count':37,
        'overlap_count':3,
        'min_tweet_datetime':'25-Oct-1900',
        'max_tweet_datetime':'25-Oct-1900',
        'min_tweet_id':'007',
        'max_tweet_id':'008'
    }

    client.insert_into_persistence_run (dict)
    max_id = client.get_max_id()
    print ("max_id = " + max_id)

    client.commit()
    client.close()    # unnecessary
