"""A python script to send Philips Hue accessory events
   (Dimmer switch, motion sensor, ...) to a Loxone Miniserver."""

import asyncio
import socket
import traceback
import requests  # pylint: disable=import-error
from aiohue import HueBridgeV2  # pylint: disable=import-error

# Insert the ip address and API key of you Philips Hue bridge
HUE_IP = "192.168.1.123"
HUE_API_KEY = "abcdefghijklmnopqrstuvwxyz"

# Insert the ip address and upd port of your Loxone Miniserver
LOXONE_IP = "192.168.1.234"
LOXONE_UDP_PORT = 1234

# Prefix of the UDP messages sent to the Loxone Miniserver
EVENT_PREFIX = "hue_event"

# If True, only sensor data and button presses are sent, no light/group states
SENSORS_AND_BUTTONS_ONLY = True

# Seconds to wait before reconnecting if the bridge is unreachable
RETRY_DELAY = 30

# Seconds between polling all motion sensors (in case an event got lost)
MOTION_POLL_INTERVAL = 60

# Global variable to store the names of the lights and sensors
# DO NOT CHANGE THIS VARIABLE
names = {}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# pylint: disable=unused-argument,too-many-branches
def parse_event(event_type, item):
    """Parse Philips hue events"""
    try:
        item_type = item.type.name
        if SENSORS_AND_BUTTONS_ONLY and item_type in ["LIGHT", "GROUPED_LIGHT"]:
            return

        if item_type == "BUTTON":
            button_event = item.button.value.value
            if button_event in ["initial_press", "repeat"]:
                item_state = f"{item.metadata.control_id}/1"
            elif button_event in ["short_release", "long_release"]:
                item_state = f"{item.metadata.control_id}/0"
            else:
                return
        elif item_type == "MOTION":
            item_state = int(item.motion.motion)
        elif item_type == "LIGHT_LEVEL":
            item_state = max(int(10 ** ((item.light.light_level - 1) / 10000)), 0)
        elif item_type == "TEMPERATURE":
            item_state = item.temperature.temperature
        elif item_type == "GROUPED_LIGHT":
            item_state = int(item.on.on)
        elif item_type == "LIGHT":
            item_state = int(item.is_on)
        elif item_type == "DEVICE_POWER":
            item_state = item.power_state.battery_level
        else:
            return

        send_to_loxone(item.id_v1, item_state)
    except Exception:  # pylint: disable=broad-exception-caught
        traceback.print_exc()


def send_to_loxone(item_id, item_state, source="EVENT"):
    """Send a UDP packet to the Loxone Miniserver"""
    event = f"{EVENT_PREFIX}{item_id}/{item_state}"
    print(f"{source}: {event}     # {names.get(item_id, '')}")
    sock.sendto(bytes(event, "utf-8"), (LOXONE_IP, LOXONE_UDP_PORT))


async def poll_motion(bridge):
    """Read the current state of all motion sensors directly from the bridge"""
    for sensor in await bridge.request("get", "clip/v2/resource/motion"):
        if sensor.get("id_v1"):
            send_to_loxone(sensor["id_v1"], int(sensor["motion"]["motion"]), "POLL")


def get_names():
    """Get the names of the lights groups and sensors"""
    url = f"http://{HUE_IP}/api/{HUE_API_KEY}"
    data = requests.get(url, timeout=15).json()

    for item_type in ["lights", "groups", "sensors"]:
        for key, value in data[item_type].items():
            names[f"/{item_type}/{key}"] = value["name"]
            print(f"{item_type}/{key}: {value['name']}")

    # Special addition for the group "0" which is all lights
    names["/groups/0"] = "All lights"


async def refresh_names():
    """Run get_names without blocking the event loop or crashing the script"""
    try:
        await asyncio.to_thread(get_names)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"WARN: could not load item names: {exc!r}")


async def main():
    """Main application, reconnects if the bridge is unreachable"""
    while True:
        # No "async with": it would not close the session if connecting fails
        bridge = HueBridgeV2(HUE_IP, HUE_API_KEY)
        try:
            await bridge.initialize()
            print("Connected to bridge: ", bridge.bridge_id)
            print("Getting item names...")
            await refresh_names()
            print("Subscribing to events...")
            bridge.subscribe(parse_event)
            seconds = 0
            while True:
                await asyncio.sleep(MOTION_POLL_INTERVAL)
                await poll_motion(bridge)
                seconds += MOTION_POLL_INTERVAL
                if seconds >= 3600:
                    seconds = 0
                    await refresh_names()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"ERROR: bridge connection failed ({exc!r}), retrying in {RETRY_DELAY}s")
        finally:
            await bridge.close()
        await asyncio.sleep(RETRY_DELAY)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
