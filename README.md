# M-Bus zu MQTT Konverter für EVN Kaifa MA309M

## Beschreibung

Dieses Projekt ermöglicht den einfachen Export von Kaifa MA309M Drehstromzählerwerten nach MQTT.

Im Fehlerfall wird alle 20 Sekunden ein Neustart versucht, ein Watchdog startet das Service nach 3 Minuten Inaktivität ebenfalls neu.

Der Code läuft seit mehreren Jahren fehlerfrei gemeinsam mit Home Assistant.

### MQTT topics

- `smartmeter/total/P`: Wirkenergie A+
- `smartmeter/total/N`: Wirkenergie A-
- `smartmeter/power/P`: Momentanleistung P+
- `smartmeter/power/N`: Momentanleistung P-
- `smartmeter/power`: Momentanleistung
- `smartmeter/voltage/L1`: Spannung L1
- `smartmeter/voltage/L2`: Spannung L2
- `smartmeter/voltate/L3`: Spannung L3
- `smartmeter/current/L1`: Strom L1
- `smartmeter/current/L2`: Strom L2
- `smartmeter/current/L3`: Strom L3
- `smartmeter/factor/efficiency`: Leistungsfaktor

### Links & Dank

Dank an Michael Reitbauer für Doku und grundsätzliche Implementierung.

- https://www.michaelreitbauer.at/kaifa-ma309-auslesen-smart-meter-evn/
- https://github.com/greenMikeEU/SmartMeterEVNKaifaMA309


## Installation

Beispielhafte manuelle Installation (das systemd unit file ist kompatibel mit Jinja2 / Ansible):

### Smartmeter

```bash
# Projekt auschecken
mkdir /opt/smartmeter
cd /opt/smartmeter
git clone https://github.com/aleho/evn-kaifa-ma309m-to-mqtt.git

# Python venv setup
./setup.sh

# systemd service
cp systemd/smartmeter.service /etc/systemd/system/smartmeter.service
vi /etc/systemd/system/smartmeter.service
## Variablen ersetzen

systemctl daemon-reload
systemctl start smartmeter.service
```

### Home Assistant

```yaml
# mqtt.yaml

sensor:
  - state_topic: "smartmeter/total/P"
    name: SmartMeter Total P
    device_class: energy
    state_class: total_increasing
    unit_of_measurement: kWh

  - state_topic: "smartmeter/total/N"
    name: SmartMeter Total N
    device_class: energy
    state_class: total_increasing
    unit_of_measurement: kWh

  - state_topic: "smartmeter/power/P"
    name: SmartMeter Power P
    device_class: power
    state_class: measurement
    unit_of_measurement: W

  - state_topic: "smartmeter/power/N"
    name: SmartMeter Power N
    device_class: power
    state_class: measurement
    unit_of_measurement: W

  - state_topic: "smartmeter/power"
    name: SmartMeter Power
    device_class: power
    state_class: measurement
    unit_of_measurement: W

  - state_topic: "smartmeter/voltage/L1"
    name: SmartMeter V L1
    device_class: voltage
    state_class: measurement
    unit_of_measurement: V

  - state_topic: "smartmeter/voltage/L2"
    name: SmartMeter V L2
    device_class: voltage
    state_class: measurement
    unit_of_measurement: V

  - state_topic: "smartmeter/voltate/L3"
    name: SmartMeter V L3
    device_class: voltage
    state_class: measurement
    unit_of_measurement: V

  - state_topic: "smartmeter/current/L1"
    name: SmartMeter I L1
    device_class: current
    state_class: measurement
    unit_of_measurement: A

  - state_topic: "smartmeter/current/L2"
    name: SmartMeter I L2
    device_class: current
    state_class: measurement
    unit_of_measurement: A

  - state_topic: "smartmeter/current/L3"
    name: SmartMeter I L3
    device_class: current
    state_class: measurement
    unit_of_measurement: A

  - state_topic: "smartmeter/factor/efficiency"
    name: SmartMeter Efficiency Factor
```
