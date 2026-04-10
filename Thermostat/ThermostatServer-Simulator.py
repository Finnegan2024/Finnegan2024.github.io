#
# ThermostatServer-Simulator.py - This is the Python code that will be used
# to simulate the Thermostat Server. It will read the data that the
# thermostat is sending to the server over the serial port and print it 
# to the screen. 
#
# This script will loop until the user interrupts the program by 
# pressing CTRL-C
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description             |   Date
#------------------------------------------------------------------
#    1          Initial Development
#------------------------------------------------------------------
#    2          Initial Enhancement         3/20/2026
#------------------------------------------------------------------
#

# Load the time module so that we can utilize the sleep method to 
# inject a pause into our operation
import time

# This imports the Python serial package to handle communications over the
# Raspberry Pi's serial port. 
import serial

##
## Import needed for deserializing payload dict
##
import json

##
## Import needed for HMAC verification
##
import hmac
import hashlib

##
## Import needed for timestamp verification
##
import time

##
## Import needed persistent data
##
import sqlite3

##
## secret key placed here for convenience, needs to be stored in env variable
##
secretKey = "This is my secret key".encode("utf-8")

##
## Using a dictionary to hold nonces for development
##
nonces = {}

##
## constant variable as timestamps should be received within 60 seconds of creation
##
ALLOWED_SECONDS = 60

##
## List to hold required fields that payload should have
##
requiredFields = ["curr_temp", "device_id", "nonce", "set_point_temp", "state", "timestamp"]

##
## List to hold eligible state that payload should have
##
eligibleStates = ["off", "heat", "cool"]

##
##
##
database = 'thermostat.db'

# Because we imported the entire package instead of just importing Serial and
# some of the other flags from the serial package, we need to reference those
# objects with dot notation.
#
# e.g. ser = serial.Serial
#
ser = serial.Serial(
        port='/dev/ttyUSB0', # This command assumes that the USB -> TTL cable
                             # is installed and the device that it uses is 
                             # /dev/ttyUSB0. This is the case with the USB -> TTL
                             # cable and Raspberry Pi 4B included in your kit.
        baudrate = 115200,   # This sets the speed of the serial interface in
                             # bits/second
        parity=serial.PARITY_NONE,      # Disable parity
        stopbits=serial.STOPBITS_ONE,   # Serial protocol will use one stop bit
        bytesize=serial.EIGHTBITS,      # We are using 8-bit bytes 
        timeout=1          # Set timeout to 1
)

# Setup loop variable
repeat = True

##
## DEBUG flag - boolean value to indicate whether or not to print 
## status messages on the console of the program
## 
DEBUG = True

##
## This function ensures HMAC signature is valid
##
def read_and_verify(dataLine):
        
        try:
                packet = json.loads(dataLine)
        except json.JSONDecodeError:
                raise ValueError("Packet is not valid JSON")
        
        if "payload" not in packet or "signature" not in packet:
                raise ValueError("Packet missing payload and/or signature")

        payloadStr = packet["payload"]
        receivedSignature = packet["signature"]

        if not isinstance(payloadStr, str) or not payloadStr.strip():
                raise ValueError("Payload must be non-empty string")
        
        if not isinstance(receivedSignature, str) or not receivedSignature.strip():
                raise ValueError("Signature must be non-empty string")

        expectedSignature =  hmac.new(secretKey, payloadStr.encode("utf-8"), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(receivedSignature, expectedSignature):
                raise ValueError("Invalid HMAC signature")
        
        try:
                payload = json.loads(payloadStr)
        except json.JSONDecodeError:
                raise ValueError("Payload is not valid JSON")
        
        return payload


##
## This function ensures all data fields are present and correct
##
def validateFields(payload):
        for field in requiredFields:
                if field not in payload:
                        raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(payload["curr_temp"], int):
                raise ValueError("Current Temperature must be non-empty integer")
        
        if not isinstance(payload["device_id"], str) or not payload["device_id"].strip():
                raise ValueError("Device ID must be non-empty string")
        
        if not isinstance(payload["nonce"], str) or not payload["nonce"].strip():
                raise ValueError("Nonce must be non-empty string")
        
        if not isinstance(payload["set_point_temp"], int):
                raise ValueError("Set point temperature must be non-empty integer")
        
        if not isinstance(payload["state"], str) or not payload["state"] or payload["state"] not in eligibleStates:
                raise ValueError("Invalid State: state can onlye be 'off', 'heat', or 'cool'")
        
        if not isinstance(payload["timestamp"], float) or not payload["timestamp"]:
                raise ValueError("Timestamp must be non-empty float")
        

##
## This function ensures timestamp is receive within 60 seconds for freshness
##
def validateTimestamp(timestamp):
        currTime = time.time()
        secondsPassed = currTime - timestamp

        if secondsPassed > ALLOWED_SECONDS:
                raise ValueError("Timestamp is older than 60 seconds")
        
        if secondsPassed < 0:
                raise ValueError("Timestamp is too far in the future")
        

##
## This function ensures nonce is valid and stored
##
def validateAndStoreNonce(deviceId, nonce):
        if deviceId not in nonces:
                nonces[deviceId] = {}

        if nonce in nonces[deviceId]:
                raise ValueError("Replay detected: nonce has been used and stored")
        else:
                nonces[deviceId][nonce] = True


##
##
##
def init_db():
        try:
                with sqlite3.connect(database) as conn:
                        cursor = conn.cursor()

                        cursor.execute("""
                                CREATE TABLE IF NOT EXISTS payloads (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                curr_temp INTEGER NOT NULL,
                                device_id TEXT NOT NULL,
                                nonce TEXT NOT NULL,
                                set_point_temp INTEGER NOT NULL,
                                state TEXT NOT NULL,
                                timestamp REAL NOT NULL)
                                """)
        
                        conn.commit()

                        print("Tables created successfully")
        
        except sqlite3.OperationalError as e:
                print(f"Failed to create database and tables {e}")


##
##
##
def insert_payload(payload):
        try:
                with sqlite3.connect(database) as conn:
                        cursor = conn.cursor()

                        cursor.execute("""
                                INSERT INTO payloads (
                                curr_temp,
                                device_id,
                                nonce,
                                set_point_temp,
                                state,
                                timestamp)
                                VALUES(?,?,?,?,?,?)
                        """,(
                                payload["curr_temp"],
                                payload["device_id"],
                                payload["nonce"],
                                payload["set_point_temp"],
                                payload["state"],
                                payload["timestamp"]
                        ))

                        conn.commit()

        except sqlite3.Error as e:
                print(f"Failed to insert payload: {e}")


##
## Test Script
##
def read_payloads():
        try:
                with sqlite3.connect(database) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM payloads ORDER BY id DESC LIMIT 1")
                        row = cursor.fetchone()
                        print(row)

        except sqlite3.Error as e:
                print(f"Failed to read latest payload: {e}")

init_db()

# Loop until the user enters a keyboard interrupt with CTRL-C
while repeat:
        try:
                # Read a line from the serial port. 
                # This also decodes the result into a utf-8 String (utf-8 is the
                # default North American English character set) and
                # normalizes the input to lower case.
                #
                # This will block until data is available
                dataline = ser.readline().decode("utf-8").strip()

                #
                # Display to the console
                #
                if(len(dataline) > 1):
                        payload = read_and_verify(dataline)

                        validateFields(payload)
                        validateTimestamp(payload["timestamp"])
                        validateAndStoreNonce(payload["device_id"], payload["nonce"])
                        
                        insert_payload(payload)
                        read_payloads()
                        print(payload)

        except UnicodeDecodeError:
                print("Error decoding packet")
        
        except ValueError as e:
                print(f"Invalid Packet: {e}")

        except KeyboardInterrupt:
                # We only reach here when the user has processed a Keyboard
                # Interrupt by pressing CTRL-C, so Exit cleanly
                repeat = False
