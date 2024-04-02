from pinlayout import RELAY_PIN

import logging
logger = logging.getLogger(__name__)

class Relaycontrol:
    relaypin = RELAY_PIN

    def __init__(self):
        try:
            import RPi.GPIO
            self.GPIO = RPi.GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setup(self.relaypin, self.GPIO.OUT)

        except Exception as e:
            logger.error('relay control init',e)

    def control_relay(self, mode):
        """ if Mode is 0 , it will be ground
            if Mode is 1, then it will be 3.3 v
            so it is normally pull_down_resistor"""
        try:
            self.GPIO.output(self.relaypin, mode)

        except Exception as e:
            logger.error(e)

            
