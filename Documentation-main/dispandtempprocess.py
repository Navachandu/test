import multiprocessing
import time
import logging
from temperature import TemperatureSensor
from epaper.examples.display import Epaper

logger = logging.getLogger(__name__)


class Dispandtemp(multiprocessing.Process):
    def __init__(self, number, display_dict):
        multiprocessing.Process.__init__(self)
        self.display_dict = display_dict
        self.daemon = True
        self.start()

    def run(self) -> None:

        epaper_obj = Epaper()
        temp_obj = TemperatureSensor()
        temperature_value = temp_obj.read_temperature()
        self.display_dict['temperature'] = temperature_value
        time.sleep(10)

        while True:
            start_time = time.time()
            intermediate_status = None

            try:
                while True:
                    energy = self.display_dict['energy_status']
                    power = self.display_dict['power_status']
                    value = self.display_dict['charge_status']
                    soc = self.display_dict['energy_status']
                    status = self.display_dict['status']
                    error = self.display_dict['error']
                    charge_power = self.display_dict['chargepower_status']
                    phase_power = self.display_dict['phase_power']

                    if energy is None or power is None or value is None:  # move to the top while loop so that it will execute only once.
                        pass
                    else:
                        # if status != intermediate_status and status != 3 and status != None and status != 9 and status != 10 and status != 11:  # for Errors
                        if status != intermediate_status and status not in (3, 9, 10, 11, 12, 13,14):  # for Errors
                            epaper_obj.error_display(soc, status, error)
                            intermediate_status = status
                            continue
                        elif intermediate_status != 3 and status != None and status not in (10, 11, 12, 13,14):  # for Standby mode
                            if status == 3:
                                stanby_start = time.time()
                                epaper_obj.error_display(soc, status, error)
                                self.display_dict['temperature'] = 25   # this is random number for switching of fan
                                intermediate_status = 3
                                continue

                        elif status == 9:  # status = 9 coming from standby display to normal display
                            epaper_obj.display(energy, power, charge_power, value, phase_power)
                            intermediate_status = 9

                        elif status == 10 or status == 11 or status == 12 or status == 13 or status == 14:  # status = 10 to display overload warning for 2 seconds
                            epaper_obj.error_display(soc, status, error)
                            time.sleep(2)
                            epaper_obj.display(energy, power,  charge_power, value, phase_power)

                        elif status is None:
                            if time.time() - start_time < 10:
                                continue
                            else:
                                epaper_obj.display(energy, power, charge_power, value, phase_power)
                                temperature_value = temp_obj.read_temperature()
                                self.display_dict['temperature'] = temperature_value
                                break
                        if status == 3 and time.time()-stanby_start > 3600:
                            epaper_obj.error_display(soc, status, error)
                            stanby_start = time.time()

            except IOError as e:
                logger.error(e)
                continue

            except Exception as e:
                logger.error(e)
                continue



