import logging
from utils import led_status
from pinlayout import I_AC_MIN, I_AC_MAX
from relay import Relaycontrol

logger = logging.getLogger(__name__)


class GridControl:
    # grid_mode = 4

    def __init__(self, ionhubstate, button_status, dutycycle_percent, inverterdata):

        try:
            import RPi.GPIO
            self.GPIO = RPi.GPIO
            self.ionhubstate = ionhubstate
            self.gridinterrupt = button_status
            self.dutycycle_percent = dutycycle_percent
            self.grid_supply = inverterdata[0]
            self.inverter_on = inverterdata[1]

        except Exception as e:
            logger.error('grid control init', e)

    def setlimits(self):

        try:
            relaycontrol_obj = Relaycontrol()

            if self.ionhubstate == 2:
                if 4 < self.dutycycle_percent < 96:
                    relaycontrol_obj.control_relay(1)  # making as low and then it will connect relay to ground
                    current = self.currentcalculation(self.dutycycle_percent)  # sending percent to current calculation
                    if self.gridinterrupt is True:
                        current = I_AC_MIN
                        if self.grid_supply is True:    # Blue is on
                            led_status(1, 0)
                        elif self.inverter_on is True:
                            led_status(0, 1)

                        else:                           # Green is on
                            led_status(0, 0)

                    else:
                        if self.grid_supply is True:    # Blue is on
                            led_status(1, 0)
                        elif self.inverter_on is True:
                            led_status(0, 1)
                        else:                           # Green is on
                            led_status(0, 0)
                else:

                    relaycontrol_obj.control_relay(0)
                    if self.grid_supply is True:
                        led_status(1, 0)
                        if self.gridinterrupt is True:   # Blue is on
                            current = I_AC_MIN
                        else:                            # Blue is on
                            current = I_AC_MAX
                    else:
                        current = I_AC_MIN
                        if self.gridinterrupt is True:  # No color
                            led_status(0, 0)
                        elif self.inverter_on is True:
                            led_status(0, 1)

            else:
                relaycontrol_obj.control_relay(0)
                current = I_AC_MIN
                led_status(0, 0)
            return current
        except Exception as e:
            logger.error(e)

    def currentcalculation(self, percent):
        try:

            wallbox_dutycycle = percent

            if 8 <= wallbox_dutycycle < 10:
                i_ac_wallbox_limit = 6
            elif 10 <= wallbox_dutycycle < 85:
                i_ac_wallbox_limit = min((wallbox_dutycycle * 0.6), I_AC_MAX)
            elif 85 <= wallbox_dutycycle < 97:
                i_ac_wallbox_limit = min((wallbox_dutycycle * 0.6), I_AC_MAX)
            else:
                i_ac_wallbox_limit = 6

            return i_ac_wallbox_limit

        except Exception as e:
            logger.error(e)
