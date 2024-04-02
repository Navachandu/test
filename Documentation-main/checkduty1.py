import time
from statistics import mean
import logging
from pinlayout import PWM_SIGNAL_WALLBOX_PIN

logger = logging.getLogger(__name__)


class DutyCycle:
    input_pin = PWM_SIGNAL_WALLBOX_PIN

    def __init__(self):
        try:
            import RPi.GPIO
            self.GPIO = RPi.GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setup(self.input_pin, self.GPIO.IN)
        except Exception as e:
            logger.error(e)

    def duty_cycle(self):
        try:
            timing = []
            duty_count = 0
            no_duty_count = 0

            while duty_count < 5:
                self.GPIO.wait_for_edge(self.input_pin, self.GPIO.RISING, timeout=5)
                rising_time = time.time()
                self.GPIO.wait_for_edge(self.input_pin, self.GPIO.FALLING, timeout=5)
                falling_time = time.time()
                dutycycle_time = falling_time - rising_time
                if dutycycle_time < 0.001:
                    timing.append(dutycycle_time)
                    percent = mean(timing) * 100000
                    duty_count = duty_count+1
                elif dutycycle_time < 0.002:
                    dutycycle_time = dutycycle_time-0.001
                    timing.append(dutycycle_time)
                    percent = mean(timing) * 100000
                    duty_count = duty_count + 1

                else:
                    if no_duty_count > 9:
                        percent = 100
                        break
                    else:
                        no_duty_count = no_duty_count+1
                        continue

            return percent

        except Exception as e:
            logger.error(e)
