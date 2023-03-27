import asyncio
from aiohue import create_app_key

# Insert the ip address of you Philips Hue bridge
hue_ip = "192.168.1.123"


async def main():
    print("Creating hue_app_key for bridge: ", hue_ip)
    input("Press the link button on the bridge, then press enter to continue...")

    # request api_key from bridge
    try:
        api_key = await create_app_key(hue_ip, "authentication_example")
        print("Authentication succeeded, api key: ", api_key)
        print("NOTE: Add hue_app_key in main.py for next connections, it does not expire.")
    except Exception as exc:
        print("ERROR: ", str(exc))


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass