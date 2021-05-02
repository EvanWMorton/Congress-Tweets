'''
This class attempts to isolate the Oracle-specific aspects of
database access.  If we switch to another database, the first step
would be to create an abstract class and make this a child of that.
'''
import cx_Oracle
import read_config

class OracleDb:
    ''' See module comment '''
    # This is a class variable.
    have_initialized_oracle_client_lib = False

    def __init__(self):
        db_config = read_config.read_config("db_config.private.json")

        if not OracleDb.have_initialized_oracle_client_lib:
            oracle_client_lib_dir = db_config["oracle_client_lib_dir"]
            cx_Oracle.init_oracle_client(lib_dir=oracle_client_lib_dir)
            OracleDb.have_initialized_oracle_client_lib = True

        username = db_config["username"]
        password = db_config["password"]
        endpoint = db_config["endpoint"]
        port = db_config["port"]
        database = db_config["database"]
        connstr = username + "/" + password + "@" + endpoint + ":" + port + "/" + database
        self.connection = cx_Oracle.connect(connstr)

#    def get_some_stuff(self):
#        cursor = self.connection.cursor()
#        #Execute Query
#        cursor.execute("select * from raw_tweet")
#        result = cursor.fetchall()
#        #Fetch results
#        for row in result:
#            print(row)
#        cursor.close()
    def run_query(self, query):
        ''' Run a database query and return the result '''
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    def run_statement(self, statement):
        ''' Run a database statement '''
        cursor = self.connection.cursor()
        cursor.execute(statement)
        # How do you resturn result?
    def run_statement_with_variables(self, statement, dictionary):
        ''' Run a database statement with bind variables. '''
        cursor = self.connection.cursor()
        cursor.execute(statement, dictionary)
        # How do you resturn result?
    def commit(self):
        ''' Perform a COMMIT. '''
        self.connection.commit()
    def close(self):
        ''' Close the database connection. '''
        self.connection.close()
    def get_date_format_string():
        ''' Get a date format which, in the TO_DATE function for this database, gives a format that works for INSERT statements. '''
        return 'YYYY-MM-DD-HH24-MI-SS'

#odb = OracleDb()
#query_result = odb.run_query("select * from raw_tweet")
#for row in query_result:
#    print(row)
#odb.commit()
#odb.close()
