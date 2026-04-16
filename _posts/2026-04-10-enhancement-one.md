---
layout: post
title: "Enhancement #1: Raspberry Pi Thermostat with State Machine and Secure Telemetry"
date: 2026-04-10
categories: [EMBEDDED-SYSTEMS, STATE-MACHINE]
author: Finnegan Thomas
---
{{ post.author }}

**Repository:** [Thermostat Device](https://github.com/Finnegan2024/Finnegan2024.github.io/tree/main/thermostat_device)

## Overview

This enhancement extends a Raspberry Pi-based thermostat originally built to manage three operational states: `off`, `heat`, and `cool` via physical GPIO buttons and a 16x2 LCD display. The original artifact read sensor data locally and controlled LEDs to reflect the current state, but had no mechanism for transmitting device telemetry off-device in a structured or secure way.

The enhancement introduces two significant additions: a **structured payload pipeline** through a `PayloadGenerator` class, and a **signed packet transmission system** using HMAC-SHA256. The device now periodically serializes its state and ships it to a server endpoint over HTTP. A `ThermostatServer-Simulator.py` script serves as a local stand-in for ingestion and validation while the full server implementation is developed in enhancement 3.

## Design Decisions and Trade-offs

**State machine as the control core.** The `TemperatureMachine` class extends `StateMachine` from the `python-statemachine` library, defining three states:

```python
cycle = (
    off.to(heat) |
    heat.to(cool) |
    cool.to(off)
)
```

Entry and exit functions (`on_enter_heat`, `on_exit_cool`, etc.) handle LED cleanup. There's no risk of a light staying on after a state transition because the exit function always fires before the next state's entry logic. This is a meaningful design that a simple flag-based approach wouldn't provide.

**Separating payload construction from device logic.** The original implementation had no payload abstraction at all. Rather than embedding serialization logic directly in `TemperatureMachine`, a dedicated `PayloadGenerator` class was extracted to own that responsibility:

```python
generator = PayloadGenerator()
payload = generator.create_payload(
    self.deviceId,
    self.current_state.id,
    self.setPoint,
    floor(self.getFahrenheit())
)
```

`PayloadGenerator.create_payload()` validates input types, normalizes state strings, and attaches a Unix timestamp and random nonce before returning a clean dict. This keeps the state machine focused on device control and makes the payload structure independently testable.

**Nonce and timestamp as replay defense.** Each payload includes both a timestamp and a nonce generated at send time:

```python
def generate_timestamp(self):
    return time.time()

def generate_nonce(self):
    num = random.randint(10000, 999999)
    return f"{num}"
```

On the receiving end, the simulator validates that the timestamp falls within a 60-second window and that the nonce has not been seen before for that device ID. These two checks together reject replayed packets. An attacker capturing a valid packet cannot resubmit it outside the freshness window or reuse the same nonce.

**HMAC signing over the serialized payload.** Before transmission, the thermostat signs the JSON-serialized payload with a shared secret using HMAC-SHA256:

```python
def create_packet(self):
    payloadText = self.setup_payload()
    payloadBytes = payloadText.encode("utf-8")
    signature = self.generate_HMAC(secretKey, payloadBytes)
    return {
        "payload": payloadText,
        "signature": signature
    }
```

Critically, the payload is serialized with `sort_keys=True` before signing:

```python
output = json.dumps(payload, separators=(",", ":"), sort_keys=True)
```

This ensures the byte representation is deterministic. The signature computed on the device will match the one recomputed on the server regardless of insertion order. The simulator verifies using `hmac.compare_digest()` rather than a direct string comparison, which is constant-time and avoids timing-based signature attacks.

**Transport shift: serial to HTTP.** The original design sent data over a serial port. This enhancement transitions to HTTP POST, which is more practical for integration with a real server and removes the physical cable dependency:

```python
requests.post("http://127.0.0.1:8000/ingestion", packet)
```

The serial write is retained but commented out, preserving the original interface as a fallback.

**Display management on a background thread.** The LCD update loop runs on a dedicated thread spawned by `tsm.run()`, keeping the main loop free to handle button events and the sleep cycle without blocking:

```python
def run(self):
    myThread = Thread(target=self.manageMyDisplay)
    myThread.start()
```

The display alternates between current temperature and thermostat state every five seconds, and calls `updateLights()` every ten seconds to keep LED state synchronized without requiring a state transition event.

## The Server Simulator

`ThermostatServer-Simulator.py` is a local validation harness, not the finalized server. It reads from the serial port, reconstructs packets, and runs the full verification pipeline: HMAC check, field validation, timestamp freshness, and nonce deduplication, before writing accepted payloads to a local SQLite database. Its purpose is to validate the thermostat's transmission pipeline end-to-end during development, independently of the server implementation covered in enhancement 3.

The server-side nonce store uses an in-memory dictionary keyed by `device_id`:

```python
def validateAndStoreNonce(deviceId, nonce):
    if deviceId not in nonces:
        nonces[deviceId] = {}
    if nonce in nonces[deviceId]:
        raise ValueError("Replay detected: nonce has been used and stored")
    else:
        nonces[deviceId][nonce] = True
```

This is appropriate for a development simulator but would need to move to persistent storage in production. The full server enhancement addresses this with a proper database implementation.

## Reflection

The most instructive part of this enhancement was thinking through the boundary between the device and the server as a security surface rather than just a communication channel. A payload without a signature represents unauthenticated data. Adding HMAC forces the question of key management, serialization determinism, and what exactly is being signed. These decisions are easy to get subtly wrong. The choice to sort keys before signing, for instance, is not clear until you consider what happens when two packets produce the same data in different byte orders.

Extracting `PayloadGenerator` also reinforced the value of separation of concerns in embedded contexts. Device logic and data formatting have different reasons to change and different testing surfaces. Keeping them separate made both easier to reason about.
