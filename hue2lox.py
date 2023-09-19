"""A python script to send Philips Hue accessory events 
   (Dimmer switch, motion sensor, ...) to a Loxone Miniserver."""
import asyncio
import socket
from aiohue import HueBridgeV2 # pylint: disable=import-error

# Insert the ip address and API key of you Philips Hue bridge
HUE_IP = "192.168.1.123"
HUE_API_KEY = "abcdefghijklmnopqrstuvwxyz"

# Insert the ip address and upd port of your Loxone Miniserver
LOXONE_IP = "192.168.1.234"
LOXONE_UDP_PORT = 1234


def parse_event(event_type, item):
    """Parse Philips hue events"""
    print("received event", event_type.value, item)
    sensor_state = 0 # pylint: disable=unused-variable
    sensor_id = ""

    if item.type.name == "BUTTON":
        if item.button.last_event.value in ["initial_press", "repeat"]:
            sensor_state = 1
        elif item.button.last_event.value in ["short_release", "long_release"]:
            sensor_state = 0
        else:
            # Leave function early
            print("EVENT: unknown button event")
            return
        sensor_state = "{item.metadata.control_id}/{sensor_state}"
        sensor_id = item.id_v1

    elif item.type.name == "MOTION":
        if item.motion.motion:
            sensor_state = 1
        else:
            sensor_state = 0
        sensor_id = item.id_v1

    elif item.type.name == "LIGHT_LEVEL":
        sensor_state = item.light.light_level
        sensor_id = item.id_v1

    # else:
    #     print("received event", event_type.value, item)

    if sensor_id != "":
        event = "hue_event{sensor_id}/{sensor_state}"
        print("EVENT: {event}")
        # Send UDP packet to Loxone Miniserver
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(event, "utf-8"), (LOXONE_IP, LOXONE_UDP_PORT))


async def main():
    """Main application"""
    async with HueBridgeV2(HUE_IP, HUE_API_KEY) as bridge:
        print("Connected to bridge: ", bridge.bridge_id)
        print("Subscribing to events...")
        bridge.subscribe(parse_event)
        while True:
            await asyncio.sleep(3600)
try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
