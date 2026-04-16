# this file controls the logic to receive, parse, and validate payloads. This demonstrates 
# my ability to mitigate vulnerabilities through secure transportation, authentication,
# and replay protection. This meets the #3, #4, and #5 course outcomes.
# resource used: original server simulator code recieved in CS350 class

from sqlmodel import select
from models import Device, Reading
import json
import hmac
import hashlib
import time


##
## Import needed for env variable
##
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
        secret_key: str

        class Config:
                env_file = ".env"

settings = Settings()
secretKey = settings.secret_key

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
## This function ensures HMAC signature is valid and returns decoded inner packet
##
def read_and_verify(raw_packet):
        
        try:
                packet = json.loads(raw_packet)
        except json.JSONDecodeError as exc:
                raise ValueError("Packet is not valid JSON") from exc
        
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
        except json.JSONDecodeError as exc:
                raise ValueError("Payload is not valid JSON") from exc
        
        if not isinstance(payload, dict):
                raise ValueError("Inner payload must decode to dict.")
        
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
## This function ensures timestamp is received within 60 seconds for freshness
##
def validateTimestamp(timestamp):
        currTime = time.time()
        secondsPassed = currTime - timestamp

        if secondsPassed > ALLOWED_SECONDS:
                raise ValueError("Timestamp is older than 60 seconds")
        
        if secondsPassed < 0:
                raise ValueError("Timestamp is too far in the future")
        
##
## Helper function to convert pi field names to server's field names
##
def convert_payload(payload):
        return {
                "device_name": payload["device_id"],
                "state": payload["state"],
                "set_point": payload["set_point_temp"],
                "current_temp": payload["curr_temp"],
                "timestamp": float(payload["timestamp"]),
                "nonce": payload["nonce"]
        }
        
##
## Confirms device exists and returns matching device
##
def validate_device(device_name, session):
        statement = select(Device).where(Device.device_name == device_name)
        device = session.exec(statement).first()

        if device is None:
                raise ValueError("Unknown Device!")
        
        return device

##
## Confirms nonce does not already exist
##
def validate_nonce(nonce, session):
        statement = select(Device).where(Reading.nonce == nonce)
        existing_reading = session.exec(statement).first()

        if existing_reading is not None:
                # ensuring I don't specify nonce is already detected to avoid giving superfluous info to potential attackers
                raise ValueError("Replay detected!")
        
##
## Controls the validation process for the /ingestion route
##
def ingest_packet(raw_packet, session):
        payload = read_and_verify(raw_packet)
        validateFields(payload)
        validateTimestamp(float(payload["timestamp"]))
        
        converted_payload = convert_payload(payload)
        device = validate_device(converted_payload["device_name"], session)
        validate_nonce(converted_payload["nonce"], session)
        if device:
                return {
                        "device_name": converted_payload["device_name"],
                        "state": converted_payload["state"],
                        "set_point": converted_payload["set_point"],
                        "current_temp": converted_payload["current_temp"],
                        "timestamp": float(converted_payload["timestamp"]),
                        "nonce": converted_payload["nonce"]
                }
        else:
                raise ValueError("Could not add reading")