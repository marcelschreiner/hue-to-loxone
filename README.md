# Philips Hue to Loxone Bridge

![Pylint](https://github.com/marcelschreiner/hue-to-loxone/actions/workflows/pylint.yml/badge.svg)
[![HitCount](https://hits.dwyl.com/marcelschreiner/hue-to-loxone.svg?style=flat)](http://hits.dwyl.com/marcelschreiner/hue-to-loxone)

This Python script allows you to integrate your Philips Hue smart lighting system with your Loxone Miniserver. By running this script, you can listen for events from your Hue bridge and send corresponding updates to your Loxone Miniserver over UDP.

## Prerequisites

Before you can use this script, you'll need the following:

- Python 3
- The `aiohue` library
- The IP address and UDP port of your Loxone Miniserver
- The IP address of your Philips Hue bridge
- An API key generated for your Hue bridge (If you dont have a key, you can simple execute the script provided in this repo)
   ```shell
   python3 get_api_key.py
   ```

## Configuration

Open the script and modify the following variables to match your setup:

- `HUE_IP`: Set this to the IP address of your Philips Hue bridge.
- `HUE_API_KEY`: Set this to your Hue bridge's API key.
- `LOXONE_IP`: Set this to the IP address of your Loxone Miniserver.
- `LOXONE_UDP_PORT`: Set this to the UDP port your Loxone Miniserver is listening on.

## Usage

1. Clone this repository or download the script.

2. Install the required dependencies if you haven't already:
   (`pip3` is traditionally used on Rapberry Pis to install libraries for Python 3 other systems may use `pip`)

   ```shell
   pip3 install aiohue
   ```

3. Modify the configuration variables in the script as described in the Configuration section.

4. Run the script using the following command:

   ```shell
   python3 hue2lox.py
   ```

   The script will connect to your Philips Hue bridge, subscribe to events, and start listening for changes.

6. The script will send updates to your Loxone Miniserver whenever there's an event on your Philips Hue system.

## Event Handling

The script currently handles events for Philips Hue buttons, motion sensors, and light level sensors. You can customize the event handling logic in the `parse_event` function based on your specific requirements.
Feel free to modify and extend the script to support additional Philips Hue devices.

## License

This script is provided under the [MIT License](LICENSE.md). Feel free to modify and use it according to your needs.
