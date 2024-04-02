import logging
from pinlayout import BMS_SLEEP_PIN

logger = logging.getLogger(__name__)


class SleepBms:
    def __init__(self):
        try:
            import RPi.GPIO
            self.GPIO = RPi.GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setup(BMS_SLEEP_PIN, self.GPIO.OUT)

        except Exception as e:
            logger.error(e)

    def bms_sleep(self):
        try:
            self.GPIO.output(BMS_SLEEP_PIN, 1)

        except Exception as e:
            logger.error(e)

        finally:
            self.GPIO.cleanup()

