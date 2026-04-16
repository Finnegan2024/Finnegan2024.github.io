# resource: https://fastapi.tiangolo.com/how-to/custom-request-and-route/?h=router#custom-apiroute-class-in-a-router
# https://fastapi.tiangolo.com/reference/templating/?h=jinja

# this file will validate incoming data and store the temperature reading within the db. 
# This demonstrates my ability to enhance db functionality within a user-friendly 
# environment by mitigating vulnerabilities through data authentication and replay
# protection.

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session
from db import get_session
from models import Reading
from validators import ingest_packet

router = APIRouter()

@router.post("/ingestion")
async def ingest_reading(req: Request, session: Session=Depends(get_session)):
    try:
        raw_body = await req.body()
        raw_packet = raw_body.decode("utf-8")
        validated_data = ingest_packet(raw_packet, session)

        reading = Reading(
            nonce = validated_data["nonce"],
            state = validated_data["state"],
            set_point=validated_data["set_point"],
            current_temp=validated_data["current_temp"],
            timestamp=validated_data["timestamp"],
            linked_device_id=validated_data["device_name"]
        )

        session.add(reading)
        session.commit()
        session.refresh(reading)

        return {
            "success": True,
            "reading_id": reading.reading_id
        }
    except ValueError as exc:
        return {
            "success": False,
            "reason": str(exc)
        }