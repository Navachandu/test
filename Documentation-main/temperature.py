import os
import glob
import time
import logging

logger = logging.getLogger(__name__)

class TemperatureSensor:
    MAX_TRIES = 5

    def open_file(self):
        for tries in range(self.MAX_TRIES):
            try:
                os.system('sudo modprobe w1-gpio')
                os.system('sudo modprobe w1-therm')
                folder = '/sys/bus/w1/devices/'
                sensor1 = glob.glob(folder+'28*')[0]
                sensor1_file = sensor1+'/w1_slave'

                with open(sensor1_file, 'r') as f:
                    sensor1_hexvalue = f.readlines()

                return sensor1_hexvalue

            except Exception as e:
                logger.error(e)
                logger.error(tries)
                time.sleep(0.5)
                continue
        return None

    def read_temperature(self):
        for tries in range(self.MAX_TRIES):
            try:
                value = self.open_file()
                if value is None:
                    return 25   # this is the random number to switch off the fan
                else:
                    while value[0].strip()[-3:] != 'YES':
                        time.sleep(0.2)
                        value = self.open_file()

                    equals_pos1 = value[1].find('t=')

                    if equals_pos1 != -1:
                        temp_string = value[1][equals_pos1 + 2:]
                        temp_c1 = float(temp_string) / 1000.0

                        return temp_c1

            except Exception as e:
                logger.error(e)
                logger.error(tries)
                time.sleep(0.5)
                continue
        return 25  # this is the random number to switch off the fan