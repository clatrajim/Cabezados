# Untitled - By: jmart - ju. nov. 3 2022
import time
from lsm6dsox import LSM6DSOX
from machine import Pin, I2C

import network
import time
from machine import Pin
from simple import MQTTClient


INT_MODE = True         # Enable interrupts
INT_FLAG = False        # At start, no pending interrupts

SSID = 'LAPTOP'   # Network SSID
KEY  = '12345678'  # Network key (must be 10 chars)

# Init wlan module and connect to network
print("Trying to connect. Note this may take a while...")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

# We should have a valid IP now via DHCP
print("Wi-Fi Connected ", wlan.ifconfig())

#DockerCompose
mqtt_server = '172.20.154.201'
client_id = 'Arduino002'
topic_pub = b'/ul/4jggokgpepnvsb2uv4s40d59ov/Arduino002/attrs'

#Internet LocalHost
#mqtt_server = 'broker.hivemq.com'
#client_id = 'bigles'
#topic_pub = b'TomsHardware'
#topic_msg = b'cabezados'

def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, keepalive=3600)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)

# Define the interrupt handler function.
def imu_int_handler(pin):
    global INT_FLAG
    INT_FLAG = True

# Configure the external interrupt (IMU).
if (INT_MODE == True):
    int_pin = Pin(24)
    int_pin.irq(handler = imu_int_handler, trigger = Pin.IRQ_RISING)

try:
   client = mqtt_connect()
except OSError as e:
   reconnect()

# Initialize an I2C object.
i2c = I2C(0, scl=Pin(13), sda=Pin(12))

# Pre-trained model configuration
# NOTE: Selected data rate and scale must match the MLC data rate and scale configuration.
UCF_FILE = "lsm6dsox_head_gestures.ucf"
UCF_LABELS = {0: "Nod", 1: "Shake", 2: "Stationary", 3:"Swing", 4:"Walk"}
lsm = LSM6DSOX(i2c, gyro_odr = 26, accel_odr = 26, gyro_scale = 2000, accel_scale = 4, ucf = UCF_FILE)

print("\n--------------------------------")
print("- Cabezados -")
print("--------------------------------\n")
print("- MLC configured...\n")

while (True):
    if (INT_MODE):
        if (INT_FLAG):
            # Interrupt detected, read the MLC output and translate it to a human readable description
            INT_FLAG = False
            label = UCF_LABELS[lsm.read_mlc_output()[0]]
            if label is not None:
                print("-", label)
                topic_msg = label.encode('utf-8')
                client.publish(topic_pub, topic_msg)
    else:
        buf = lsm.read_mlc_output()
        if (buf != None):
            print(UCF_LABELS[buf[0]])
