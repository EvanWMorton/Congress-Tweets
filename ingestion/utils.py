import os
import sys
import logging

def get_env_var(name, error_if_missing):
   ''' Gets the value of an environment variable.  If the variable is
       missing, and error_if_missing is True, give an error and exit.
   '''
   value = os.getenv(name)
   if value == None and error_if_missing:
       errmsg = "Exiting due to missing environment variable '" + name + "'."
       print (errmsg)
       logging.error(errmsg)
       sys.exit(errmsg)
   return value
