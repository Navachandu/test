from bms.bmsreceive import BmsReceive
from bms.bmswakeup import BmsWakeup
from bms.bmscharge import BmsCharge
from pinlayout import BMS_SLEEP_PIN
from globalvar import write_soc_stop_inverter, read_battery_empty
import time
import subprocess
import logging
import datetime
logger = logging.getLogger(__name__)


class StartingExecution:

    def __init__(self):
        try:
            import RPi.GPIO
            self.GPIO = RPi.GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setup(BMS_SLEEP_PIN, self.GPIO.OUT)
        except Exception as e:
            logger.error(e)

    def start_sequence(self):

        try:
            for activate in range(9):   # TO wake up the BMS

                self.GPIO.output(BMS_SLEEP_PIN, 1)
                time.sleep(.1)
                self.GPIO.output(BMS_SLEEP_PIN, 0)

                # send wakeup BMS
                bmswakeup_obj = BmsWakeup()
                bmswakeup_obj.wakeup_bms()
                time.sleep(1)

                # Get BMS data
                bmsreceive_obj = BmsReceive()
                can_values = bmsreceive_obj.bms_receive()
                timestamp=datetime.datetime.fromtimestamp(can_values[49])
                set_time = timestamp.strftime('%H:%M:%S %Y-%m-%d')
                #subprocess.run(['sudo','date','--set',set_time])
                print(timestamp)
                print(can_values)
                logger.info('can values from Bms Receive after waking up')
                logger.info(can_values)

                if can_values[38] == 1:  # checking status_battery is active or not
                    logger.info('bms status is 1 and sending BMS charge')
                    break
                else:
                    continue

            for receive in range(9):  # this loop will occur 10 times untill we get the bmsreceive

                logger.info('bms status is 1 and sending BMS charge')
                bmscharge_obj = BmsCharge()
                bmscharge_obj.charge_bms()

                time.sleep(1)

                # Get BMS data
                bmsreceive_obj = BmsReceive()
                can_values = bmsreceive_obj.bms_receive()

                if can_values[38] == 3:
                    logger.info('bms status can_values[38]')
                    battery_empty = float(read_battery_empty())
                    energy_value = ((can_values[26] - battery_empty) / (100 - battery_empty)) * 100

                    if energy_value < 10:
                        logger.info('charging is less than 10 percent, making soc_stop_inverter=1')
                        write_soc_stop_inverter(1)  # we are sending 1 in soc_stop_inverter.txt file if
                        # charging is less than 10 percent
                    else:
                        write_soc_stop_inverter(0)  # we are sending 0 in soc_stop_inverter.txt file if
                        # charging is more than 10 percent
                    break

                else:
                    # print(f'charge error counter up for {receive} time(s)')
                    continue

        except Exception as e:
            logger.error(e)
