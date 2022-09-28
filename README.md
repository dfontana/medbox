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
