import _thread
import socket
import time

import dht
import machine
import network
from machine import Pin, SoftI2C

from bh1750 import BH1750

# Shared variables and lock
temperature = None
humidity = None
lux = None
lock = _thread.allocate_lock()

# Wi-Fi setup (modify with your credentials)
SSID = ""
PASSWORD = ""
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)


print("Attempting to connect to " + SSID + " ")
while not wifi.isconnected():
    time.sleep(1)
    print(".", end="")

print("Connected")

# Setup DHT22 sensor
dht_sensor = dht.DHT22(machine.Pin(4))  # Change to your pin

# Setup BH1750 light sensor
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)  # Adjust pins as needed
light_sensor = BH1750(bus=i2c, addr=0x23)


# Background thread function to listen for packets
def listen_for_requests():
    global temperature, humidity, lux
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 12345))  # Listen on port 12345

    while True:
        data, addr = sock.recvfrom(1024)  # Receive data
        if data:
            lock.acquire()
            try:
                response = (
                    f"Temp: {temperature}°C, Humidity: {humidity}%, Lux: {lux} lx"
                    if temperature is not None
                    else "No data"
                )
            finally:
                lock.release()
            sock.sendto(response.encode(), addr)  # Send response


# Start background thread
_thread.start_new_thread(listen_for_requests, ())

# Main thread reads sensors every 10 sec
while True:
    try:
        dht_sensor.measure()
        hum = dht_sensor.humidity()
        temp_c = dht_sensor.temperature()  # Get temperature in Celsius
        temp_f = (temp_c * 9 / 5) + 32  # Convert to Fahrenheit
        time.sleep(1)
        light = light_sensor.luminance(BH1750.CONT_HIRES_2)

        lock.acquire()
        try:
            temperature = temp_f
            humidity = hum
            lux = light
        finally:
            lock.release()

        print(f"Updated readings - Temp: {temp_f}°F, Humidity: {hum}%, Lux: {light} lx")
    except Exception as e:
        print("Sensor error:", e)

    time.sleep(10)
