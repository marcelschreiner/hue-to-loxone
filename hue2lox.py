"""A python script to send Philips Hue accessory events 
   (Dimmer switch, motion sensor, ...) to a Loxone Miniserver."""

import asyncio
import requests
import socket
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


def parse_event(event_type, item):
    """Parse Philips hue events"""
    # print("received event", event_type.value, item)
    state = 0  # pylint: disable=unused-variable
    id = ""

    if item.type.name == "BUTTON":
        if item.button.last_event.value in ["initial_press", "repeat"]:
            state = 1
        elif item.button.last_event.value in ["short_release", "long_release"]:
            state = 0
        else:
            # Leave function early
            print("EVENT: unknown button event")
            return
        state = f"{item.metadata.control_id}/{state}"
        id = item.id_v1

    elif item.type.name == "MOTION":
        state = int(item.motion.motion)
        id = item.id_v1

    elif item.type.name == "LIGHT_LEVEL":
        state = item.light.light_level
        id = item.id_v1

    elif item.type.name == "TEMPERATURE":
        state = item.temperature.temperature
        id = item.id_v1

    elif item.type.name == "GROUPED_LIGHT":
        state = int(item.on.on)
        id = item.id_v1

    elif item.type.name == "LIGHT":
        state = int(item.is_on)
        id = item.id_v1

    elif item.type.name == "DEVICE_POWER":
        state = item.power_state.battery_level
        id = item.id_v1

    if id != "":
        try:
            event = f"hue_event{id}/{state}     # {names[id]}"
        except KeyError:
            # If the name is not found, do not send include it in the event
            event = f"hue_event{id}/{state}"

        print(f"EVENT: {event}")
        # Send UDP packet to Loxone Miniserver
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(event, "utf-8"), (LOXONE_IP, LOXONE_UDP_PORT))


def get_names():
    """Get the names of the lights groups and sensors"""
    url = f"http://{HUE_IP}/api/{HUE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    for type in ["lights", "groups", "sensors"]:
        for key, value in data[type].items():
            names[f"/{type}/{key}"] = value["name"]

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
