#!/usr/bin/python3

import os
import sys
import sdnotify

from smartmeter.reader import Reader
from smartmeter.publisher import Publisher


def print_data(data):
    print("Wirkenergie A+: "      + str(data["total/P"]) + " kWh")
    print("Wirkenergie A-: "      + str(data["total/N"]) + " kWh")
    print("Momentanleistung P+: " + str(data["power/P"]) + " W")
    print("Momentanleistung P-: " + str(data["power/N"]) + " W")
    print("Momentanleistung: "    + str(data["power"])   + " W")
    print("Spannung L1: "         + str(data["voltage/L1"]) + " V")
    print("Spannung L2: "         + str(data["voltage/L2"]) + " V")
    print("Spannung L3: "         + str(data["voltage/L3"]) + " V")
    print("Strom L1: "            + str(data["current/L1"]) + " V")
    print("Strom L2: "            + str(data["current/L2"]) + " A")
    print("Strom L3: "            + str(data["current/L3"]) + " A")
    print("Leistungsfaktor: "     + str(data["factor/efficiency"]))
    print()


###

verbose = os.environ.get("DEBUG", "0") == "1"
useMqtt = os.environ.get("MQTT", "0") == "1"
inSystemd = os.environ.get("INVOCATION_ID", "") != ""

reader = Reader(
    key=os.environ.get("KEY", ""),
    serial_port=os.environ.get("SERIAL_PORT", "/dev/ttyUSB0"),
    verbose=verbose,
)


if inSystemd:
    notifier = sdnotify.SystemdNotifier()
else:
    notifier = None


if useMqtt:
    try:
        publisher = Publisher(
            os.environ.get("MQTT_CLIENT_ID", "SmartMeter"),
            os.environ.get("MQTT_HOST", "127.0.0.1"),
            os.environ.get("MQTT_USER"),
            os.environ.get("MQTT_PASS"),
            os.environ.get("MQTT_PORT", 1883),
        )

    except Exception as e:
        print("Error initializing MQTT publisher: " + str(e))
        sys.exit(1)

else:
    publisher = None


print("Ready. Reading data...")

if notifier:
    notifier.notify("READY=1")


try:
    while True:
        if notifier:
            notifier.notify("WATCHDOG=1")

        data = reader.read_and_parse()

        if data is None:
            continue;

        if verbose or not publisher:
            print_data(data)

        if publisher:
            publisher.publish_data(data)

except KeyboardInterrupt:
    reader.close()
