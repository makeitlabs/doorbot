# doorbot
Doorbot is a Python-based RFID access control system that is generally run on Raspberry Pi or other Linux-based systems.  It was primarily developed to control physical access to exterior doors in our Makerspace facility.

Doorbot can run 'headless' with no display (typically using an LED for user feedback), or optionally provide a GUI display for rich user feedback.

Doorbot exists alongside RATT (https://github.com/makeitlabs/ratt/), which is a lower-cost RFID access control endpoint implemented on an entirely different platform.  Both Doorbot and RATT use the authbackend database (https://github.com/makeitlabs/authbackend) to obtain their access control lists, allowing for centralized access control.

