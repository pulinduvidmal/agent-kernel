
import os, sys
sys.path.insert(0, os.getcwd())  


import local_agents 

# start the REST API
from agentkernel.api import RESTAPI
RESTAPI.run()   
