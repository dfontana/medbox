# MedBox

What's MedBox? It's a hacktober-fest project aiming to build a physical box that reminds the user when to take their medication. The goal is to have a Client-Server architecture, where the server is responsible for scheduling and triggering alerts, while the client is a thin-client displaying LED colors (when alerting) and has a push-button to ack the alert.

## Milestones

__MVP__:

- Axum server, with endpoints:
  - GET `/status/` to return current state the Client LED should be in (off, alert)
  - GET `/status/hit` to indicate to the server the Client's button was pressed, and what state should now be active.
- Raspberry Pico W client:
  - Shows RED in LEDs when a non-recoverable error has occurred, that warrants a restart or diagnosis
  - Shows Rainbow of colors when ALERT is active
  - Turns off LEDs when not needed
  - Can signal the server on button press, indicating user has responded to action

__Stretch 1__:

- Configurable:
  - Schedule for when the box should alert, based on Days-of-Week and Time(s)-of-Day
  - Vacation time, in which the schedule is disabled
- A local-network accessible configuration UI on the Server:
  - View the current, effective schedule
  - Add, remove, modify vacation time
  - Modify the schedule

__Stretch 2__:

- [Pushover](https://pushover.net/) notification to compliment the LED alerts, sent via server

__Stretch 3__:

- Global access to the configuration server, to make tweaks while away (like maybe [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)?)
- Ability to Acknowledge the alert when not home, but otherwise required to acknowledge when within home
  - Need a Geo-net around a home location
  - Configurable from the UI
  - And a way to ack the request, either from Notification (which Pushover may not support a means to) or a bookmarklet

## Client 

The client is thin: it polls the server every N seconds to figure out what it should be doing and does so. Only if the button is pressed will is ping the server and potentially change states sooner.
The States are:
- __ERROR__: Show all RED, something went wrong and a reboot may be needed
- __ALERT__: Show rainbow of colors, something is to be done (press the button)
- __OFF__: No LEDs showing because there is no action to take 
And the Actions are:
- __Synchronize__: Every N seconds invoke `/status/` to determine what should be happening in this moment
- __Press__: Invoke `/status/hit` and return back what should be done in response to this, if anything 

### Setup

- [Micropython Setup Docs](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
- [Micropython Library Docs](https://docs.micropython.org/en/latest/library/index.html)
- [Pico W Datasheet](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf)
- [Pico W Internet Docs](https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf)
- [Helpful Wiring On Button](https://www.youtube.com/watch?v=wFbfPt0RYPA)

#### One time
On the Pico W, hold the flashing button and connect to computer. That will enter flashing mode & mount it as a volume. Drag the firmware (from the pico site) for micropython onto the volume and wait for reboot. Note: Don't use Thonny to flash, or it will flash the non-w version.

Next connect the following:
- LED GND to GND
- LED Data to GP16
- LED PWR to VBUS
- Button GND to GND
- Button Data to GP17
_Notice this button is setup in Pull UP mode, alternatively could do Button to 3.3v+GP17 in Pull DOWN mode._
#### Transferring Scripts
Create a file called `secrets.py` on the Pico (Thonny can save it directly). It should contain (you fill in the templates though):
```py
SSID={}
SSID_PASSWD={}
SERVER_HOST={}
```
Finally save the client's `main.py` onto the Pico (Thonny can also do this). When booted, micropython will find and start this
