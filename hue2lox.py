"""A python script to send Philips Hue accessory events 
   (Dimmer switch, motion sensor, ...) to a Loxone Miniserver."""

import asyncio
import socket
import requests  # pylint: disable=import-error
from aiohue import HueBridgeV2  # pylint: disable=import-error

# Insert the ip address and API key of you Philips Hue bridge
HUE_IP = "192.168.1.123"
HUE_API_KEY = "abcdefghijklmnopqrstuvwxyz"

# Insert the ip address and upd port of your Loxone Miniserver
LOXONE_IP = "192.168.1.234"
LOXONE_UDP_PORT = 1234

# Global variable to store the names of the lights and sensors
# DO NOT CHANGE THIS VARIABLE
names = {}


# pylint: disable=unused-argument
def parse_event(event_type, item):
    """Parse Philips hue events"""
    # print("received event", event_type.value, item)
    item_state = 0  # pylint: disable=unused-variable
    item_id = ""

    if item.type.name == "BUTTON":
        if item.button.last_event.value in ["initial_press", "repeat"]:
            item_state = 1
        elif item.button.last_event.value in ["short_release", "long_release"]:
            item_state = 0
        else:
            # Leave function early
            print("EVENT: unknown button event")
            return
        item_state = f"{item.metadata.control_id}/{item_state}"
        item_id = item.id_v1

    elif item.type.name == "MOTION":
        item_state = int(item.motion.motion)
        item_id = item.id_v1

    elif item.type.name == "LIGHT_LEVEL":
        item_state = item.light.light_level
        item_id = item.id_v1

    elif item.type.name == "TEMPERATURE":
        item_state = item.temperature.temperature
        item_id = item.id_v1

    elif item.type.name == "GROUPED_LIGHT":
        item_state = int(item.on.on)
        item_id = item.id_v1

    elif item.type.name == "LIGHT":
        item_state = int(item.is_on)
        item_id = item.id_v1

    elif item.type.name == "DEVICE_POWER":
        item_state = item.power_state.battery_level
        item_id = item.id_v1

    if item_id != "":
        try:
            event = f"hue_event{item_id}/{item_state}     # {names[item_id]}"
        except KeyError:
            # If the name is not found, do not send include it in the event
            event = f"hue_event{item_id}/{item_state}"

        print(f"EVENT: {event}")
        # Send UDP packet to Loxone Miniserver
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(event, "utf-8"), (LOXONE_IP, LOXONE_UDP_PORT))


def get_names():
    """Get the names of the lights groups and sensors"""
    url = f"http://{HUE_IP}/api/{HUE_API_KEY}"
    response = requests.get(url, timeout=60)
    data = response.json()

    for item_type in ["lights", "groups", "sensors"]:
        for key, value in data[item_type].items():
            names[f"/{item_type}/{key}"] = value["name"]

    # Special addition for the group "0" which is all lights
    names["/groups/0"] = "All lights"


async def main():
    """Main application"""
    async with HueBridgeV2(HUE_IP, HUE_API_KEY) as bridge:
        print("Connected to bridge: ", bridge.bridge_id)
        print("Getting light names...")
        get_names()
        print("Subscribing to events...")
        bridge.subscribe(parse_event)
        while True:
            await asyncio.sleep(3600)
            get_names()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
