import paho.mqtt.client as mqtt


class Publisher:
    def __init__(self, client_id, host, user, password, port):
        print(f"Connecting to MQTT; client_id={client_id}, port={port}")

        self.client = mqtt.Client(
            client_id=client_id,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )

        self.client.username_pw_set(user, password)
        self.client.reconnect_delay_set(min_delay=5, max_delay=120)
        self.client.connect(host, port=port)

    def publish_data(self, data):
        self.client.publish("smartmeter/total/P", data["total/P"])
        self.client.publish("smartmeter/total/N", data["total/N"])

        self.client.publish("smartmeter/power/P", data["power/P"])
        self.client.publish("smartmeter/power/N", data["power/N"])
        self.client.publish("smartmeter/power",   data["power"])

        self.client.publish("smartmeter/voltage/L1", data["voltage/L1"])
        self.client.publish("smartmeter/voltage/L2", data["voltage/L2"])
        self.client.publish("smartmeter/voltage/L3", data["voltage/L3"])
        self.client.publish("smartmeter/current/L1", data["current/L1"])
        self.client.publish("smartmeter/current/L2", data["current/L2"])
        self.client.publish("smartmeter/current/L3", data["current/L3"])

        self.client.publish("smartmeter/factor/efficiency", data["factor/efficiency"])
