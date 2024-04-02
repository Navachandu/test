"""                         Waking up BMS                     """

import logging
logger = logging.getLogger(__name__)


class BmsWakeup:

    def __init__(self):
        try:
            import os
            os.system('sudo ip link set can0 up type can bitrate 500000')
            import can
            self.can = can
            self.bus = self.can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)
        except Exception as e:
            logger.error(e)

    def wakeup_bms(self):
        try:
            msg = self.can.Message(arbitration_id=0x02, data=[3, 240, 63], is_extended_id=False)
            self.bus.send(msg, 5)

        except Exception as e:
            logger.error(e)
