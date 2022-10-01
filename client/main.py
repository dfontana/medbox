import secrets
import urequests
import network
import _thread
from utime import sleep_ms
from machine import Pin
from neopixel import NeoPixel

SYNC_INTERVAL_MS= 10 * 1000
MAX_WIFI_WAIT_MS= 60 * 1000
NUM_LEDS=7
LED_DATA_PIN=16
BUTTON_PIN=17

# https://docs.micropython.org/en/latest/library/neopixel.html
# Strip can be either `fill()`d with a RGBW color tuple or addressable
# up to NUM_LEDs to set individual pixels (eg strip[1] = RGBW_tuple)
strip = NeoPixel(Pin(LED_DATA_PIN), NUM_LEDS, bpp=4)

# In your case, you bought a latching switch accidentally...
# https://www.nteinc.com/switches/pdf/pushbutton.pdf#page=6
# Configuring this can be done either GPIO+Ground+PULL_UP resistor
# or GPIO+3.3v+PULL_DOWN
latch = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

# Enable the WIFI module inside, in client mode. This will only
# turn on the WLAN adapter and does nothing more
wlan = network.WLAN(network.STA_IF)
wlan.active(True)


class State:
    # Acts as our signal for what the system is doing at this point in time
    # There is no enum class in Micropython so this is a semi-functional version
    # but at least ensures we're working somewhat correctly
    ALERT = 'alert'
    OFF = 'off'
    ERROR = 'error'
    
    @classmethod
    def from_str(inp):
        if inp == None:
            return (None, False)
        norm = inp.lower()
        for st in [ALERT, OFF, ERROR]:
            if st == norm:
                return (name, True)
        return (None, False)


# Multi-core lock, so the NeoPixel thread can read from the main thread safely
CURRENT_STATE = State.OFF


def wifi_connect():
    # Attempt a wifi connection if not already connected or attempting to connect,
    # waiting MAX_WIFI_WAIT seconds to succeed or assume failure
    wlan_status = wlan.status()
    if wlan_status != network.STAT_CONNECTING or wlan_status != network.STAT_GOT_IP:
        wlan.connect(secrets.SSID, secrets.SSID_PASSWD)
        
    wait = MAX_WIFI_WAIT_MS
    while wait > 0:
        if wlan.isconnected():
            print(f"Wifi Connected (status={wlan.status()})")
            return True
        wait -= 1000
        sleep_ms(1000)
        
    print(f"Wifi Connection failed (status={wlan.status()})")
    return False

    
def get_state(from_press=False, retry_num=0):
    # Fetches expected state from server, should the device need synchronizing,
    # or an action occurred that may alter state. This is because the server is
    # the source of truth, not the button on the device
    if retry_num >= 3:
        return State.ERROR
    
    hit_slug = ""
    if from_press:
        hit_slug = "hit"
    r = None
    try:  
        r = urequests.get(f"http://{secrets.SERVER_HOST}/status/{hit_slug}")
        if r.status_code != 200:
            return State.ERROR
        return State.from_str(r.text)
    except Exception as error:
        # Ensure wifi connection & retry
        print(f"HTTP call failed (status={str(wlan.status())})")
        print(error)
        wifi_connect()
        get_state(from_press=from_press,retry_num=retry_num+1)
    finally:
        if r not None:
            r.close()


def update_state(state):
    global CURRENT_STATE
    print(f"Changing to State {state}")
    CURRENT_STATE = state
    
    
def color_task():
    rgb_off = (0, 0, 0, 0)
    rgb_red = (255, 0, 0, 0)
    colors = [
        (255, 0, 125, 0),
        (255, 0, 210, 0),
        (0, 255, 210, 0),
        (0, 255, 125, 0),
        (255, 210, 0, 0),
        (255, 125, 0, 0),
    ]
    color_1 = 0
    color_2 = 1

    while True:
        if CURRENT_STATE == State.ALERT:
            for i in range(3):
                strip[i] = colors[color_1]
            for i in range(4):
                strip[3 + i] = colors[color_2]
            color_1 = (color_1 + 1) % len(colors)
            color_2 = (color_2 + 1) % len(colors)
            strip.write()
        elif CURRENT_STATE == State.OFF:
            strip.fill(rgb_off)
            strip.write()
        elif CURRENT_STATE == State.ERROR:
            strip.fill(rgb_red)
            strip.write()
        sleep_ms(300)


def listen():
    # Since this is a latching switch and not momentary, we can't use interrupts
    # (irq). I wanted a momentary switch though, so let's fix this with software
    # by detecting state changes...
    loop_delay_ms = 100
    last_value = latch.value()
    last_sync = 0
    while True:
        if last_sync <= 0:
            update_state(get_state())
            last_sync = SYNC_INTERVAL_MS/loop_delay_ms
        last_sync -= 1
        
        new_value = latch.value()
        if new_value != last_value:
            print("Button pressed")
            last_value = new_value
            update_state(get_state(from_press=True))

        sleep_ms(loop_delay_ms)


try:
    print("Initializing...")
    wifi_connect()
    
    print("Spawning NeoPixel thread")
    _thread.start_new_thread(color_task, ())

    print("Listening...")
    listen()
except KeyboardInterrupt:
    # In the case of running interactively, eg in Thonny
    strip.fill(RGB_OFF)
    strip.write()
except:
    # If the program excepted in any spectacular way let's just reboot
    machine.reset()