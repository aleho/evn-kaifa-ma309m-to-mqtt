import serial
import time

from bs4 import BeautifulSoup
from binascii import unhexlify
from gurux_dlms.GXDLMSTranslator import GXDLMSTranslator
from Crypto.Cipher import AES


XML_VALUES = {
    "0100010800FF": "total/P", # Wirkenergie A+, Wh
    "0100020800FF": "total/N", # Wirkenergie A-, Wh

    "0100010700FF": "power/P", # Momentanleistung P+, W
    "0100020700FF": "power/N", # Momentanleistung P-, W

    "0100200700FF": "voltage/L1", # Spannung L1, V * 10
    "0100340700FF": "voltage/L2", # Spannung L2, V * 10
    "0100480700FF": "voltage/L3", # Spannung L3, V * 10

    "01001F0700FF": "current/L1", # Strom L1, mA
    "0100330700FF": "current/L2", # Strom L2, mA
    "0100470700FF": "current/L3", # Strom L3, mA

    "01000D0700FF": "factor/efficiency", # Leistungsfaktor, 0 - 1000
}

CONVERSION = {
    "total/P": 1000, # kWh
    "total/N": 1000, # kWh

    "power/P": 1, # W
    "power/N": 1, # W

    "voltage/L1": 10, # V
    "voltage/L2": 10, # V
    "voltage/L3": 10, # V

    "current/L1": 100, # A
    "current/L2": 100, # A
    "current/L3": 100, # A

    "factor/efficiency": 1000, # 0 - 1
}


class Reader:
    def __init__(self, key, serial_port, verbose):
        if len(key) != 32:
            raise ValueError("Invalid smartmeter key length (expected 32, got " + len(key) + ")")

        self.key = unhexlify(key)
        self.verbose = verbose

        self.translator = GXDLMSTranslator()

        if self.verbose:
            print("Opening serial")

        self.serial = serial.Serial(
            port=serial_port,
            baudrate=2400,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )


    def close(self):
        if self.verbose:
            print("Closing serial")

        self.serial.flushOutput()
        self.serial.close()


    def reconnect_serial(self):
        self.close()
        time.sleep(2.5) # sleep longer than the send interval of 2 seconds

        if self.verbose:
            print("Opening serial")

        self.serial.open()


    def _read_xml(self):
        data = self.serial.read(size=282).hex()

        mBusStart = data[0:8]
        frameLen = int("0x" + mBusStart[2:4], 16)
        title = data[22:38]
        counter = data[44:52]
        frame = data[52:12 + frameLen * 2]

        if not (mBusStart[0:2] == "68"
            and mBusStart[6:8] == "68"
            and mBusStart[2:4] == mBusStart[4:6]
        ):
            if self.verbose:
                print("Wrong M-Bus start header")

            self.reconnect_serial()
            return None


        frame = unhexlify(frame)
        init_vector = unhexlify(title + counter)
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=init_vector)
        apdu = cipher.decrypt(frame).hex()

        if apdu[0:4] != "0f80":
            if self.verbose:
                print("Invalid APDU data")

            return None


        try:
            xml = self.translator.pduToXml(apdu)
        except BaseException as err:
            if self.verbose:
                print("Invalid APDU", format(err))
                print(format(apdu))

            return None


        return BeautifulSoup(xml, "lxml")



    def read_and_parse(self):
        xml = self._read_xml()

        if xml is None:
            return None

        data = {}

        for value, name in XML_VALUES.items():
            el = xml.find('octetstring', {
                "value": value
            })

            if el:
                uint = el.find_next_sibling()

                if uint:
                    hex = uint["value"]
                    if hex:
                        value = int(hex, 16)

                        if value >= 0:
                            data[name] = value / CONVERSION[name]

                            continue

            # fall-through to empty value
            data[name] = None


        # Momentanleistung, W
        if data["power/P"] is not None and data["power/N"] is not None:
            data["power"] = data["power/P"] - data["power/N"]
        else:
            data["power"] = None


        return data
