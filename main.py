from aiohue import HueBridgeV2
import asyncio
import socket

# Insert the ip address and API key of you Philips Hue bridge
hue_ip = "192.168.1.123"
hue_api_key = "abcdefghijklmnopqrstuvwxyz"

# Insert the ip address and upd port of your Loxone miniserver
loxone_ip = "192.168.1.234"
loxone_udp_port = 1234


def parse_event(event_type, item):
    # print("received event", event_type.value, item)
    sensor_state = 0
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
        sensor_state = "{}/{}".format(item.metadata.control_id, sensor_state)
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

    if not sensor_id == "":
        event = "hue_event{}/{}".format(sensor_id, sensor_state)
        print("EVENT: {}".format(event))
        # Send UDP packet to Loxone Miniserver
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(event, "utf-8"), (loxone_ip, loxone_udp_port))


async def main():
    async with HueBridgeV2(hue_ip, hue_api_key) as bridge:
        print("Connected to bridge: ", bridge.bridge_id)
        print("Subscribing to events...")
        bridge.subscribe(parse_event)
        while True:
            await asyncio.sleep(3600)
try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass