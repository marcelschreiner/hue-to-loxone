"""A python script to get a hue api key from a Philips Hue bridge."""
import asyncio
from aiohue import create_app_key

# Insert the ip address of you Philips Hue bridge
HUE_IP = "192.168.1.123"


async def main():
    """Creates a hue api key, after pressing the link button on the bridge."""
    print("Creating hue_app_key for bridge: ", HUE_IP)
    input("Press the link button on the bridge, then press enter to continue...")

    # request api_key from bridge
    try:
        api_key = await create_app_key(HUE_IP, "authentication_example")
        print("Authentication succeeded, api key: ", api_key)
        print("NOTE: Add hue_app_key in main.py for next connections, it does not expire.")
    except Exception as exc: # pylint: disable=broad-exception-caught
        print("ERROR: ", str(exc))


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
