##
## Functionality for PayloadGenerator class
##

#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description             |   Date
#------------------------------------------------------------------
#    1          Initial Enhancement         3/20/2026
#------------------------------------------------------------------
#

##
## Import needed for generating timestamp
##
import time

##
## Import needed for generating nonce
##
import random

##
## DEBUG flag - boolean value to indicate whether or not to print 
## status messages on the console of the program
## 
DEBUG = True

class PayloadGenerator():
    def create_payload(self, deviceId, state, setPoint, currTemp):

        # verify create_payload is called
        if (DEBUG):
            print("create_payload called")

        ##
        ## Ensure payload values are of correct type and length
        ##
        if not isinstance(deviceId, str) or deviceId.strip() == "":
            raise ValueError(
                "Device ID must not be an empty string"
            )
        
        if not isinstance(setPoint, int):
            raise ValueError(
                "Set point temperature must be an integer"
            )
        
        if not isinstance(currTemp, int):
            raise ValueError(
                "Current temperature must be an integer"
            )
        
        ##
        ## ensure state is an acceptable value and create timestamp & nonce for payload
        ##
        newState = self.normalize_state(state)
        timestamp = self.generate_timestamp()
        nonce = self.generate_nonce()

        ##
        ## return payload container as a dict
        ##
        return {
            "device_id": deviceId.strip(),
            "state": newState,
            "set_point_temp": setPoint,
            "curr_temp": currTemp,
            "timestamp": timestamp,
            "nonce": nonce
        }
    
    def normalize_state(self, state):

        # verify create_payload is called
        if (DEBUG):
            print("normalize_state called")

        normalizedState = state.strip().lower()
        allowedStates = {"off", "heat", "cool"}

        if normalizedState not in allowedStates:
            raise ValueError(
                f"Invalid state '{state}': Must be 'off', 'heat', or 'cool'"
            )
        
        return normalizedState
    
    def generate_timestamp(self):

        # verify create_payload is called
        if (DEBUG):
            print("generate_timestamp called")

        return time.time()
    
    def generate_nonce(self):

        # verify create_payload is called
        if (DEBUG):
            print("generate_nonce called")

        num = random.randint(10000, 999999)
        
        return f"{num}"
