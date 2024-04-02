"""this is updated code of display"""
import logging

from globalvar import (write_inverter_switch_state, read_inverter_switch_state, write_battery_empty,
                       write_soc_stop_inverter, read_soc_stop_inverter)
logger = logging.getLogger(__name__)

'''from state machine, we get Ion_hub_state

Ion_hub_state = 2  -  Run
                 3  -  Stop
                 4 -  Error
                 5 - shutdown
'''


class InverterControl:

    def __init__(self, ionhubstate, button_status, battery_empty, energy_value, grid_supply, soc_system_trimmed,
                 fully_charge):

        try:
            import RPi.GPIO
            self.GPIO = RPi.GPIO
            self.ionhubstate = ionhubstate
            self.button_status = button_status
            self.battery_empty = battery_empty
            self.energy_value = energy_value
            self.grid_supply = grid_supply
            self.soc_system_trimmed = soc_system_trimmed
            self.fully_charge = fully_charge

        except Exception as e:
            logger.error(e)

    def setinverters(self):

        try:
            if self.ionhubstate in (3, 4, 5) or self.button_status is True:
                write_inverter_switch_state(4)
                inverter_switch_state_multiplus = 4

            else:
                if self.battery_empty is True and self.grid_supply is False:
                    write_battery_empty(self.soc_system_trimmed)
                    write_soc_stop_inverter(1)
                    inverter_switch_state_multiplus = 1

                else:
                    if float(read_soc_stop_inverter()) == 1:   # here 1 is active
                        if self.energy_value < 15:
                            inverter_switch_state_multiplus = 1

                        else:
                            write_soc_stop_inverter(0)
                            inverter_switch_state_multiplus = 3

                    else:
                        if self.fully_charge == 1 and self.grid_supply is True:
                            inverter_switch_state_multiplus = 4
                        else:
                            inverter_switch_state_multiplus = 3

            return inverter_switch_state_multiplus

        except Exception as e:
            logger.error(e)
