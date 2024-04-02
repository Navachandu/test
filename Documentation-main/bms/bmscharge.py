"""Bring BMS to Charge Mode"""

import time
import logging

logger = logging.getLogger(__name__)


class BmsCharge:
    def __init__(self):

        try:
            import os
            os.system('sudo ip link set can0 up type can bitrate 500000')
            import can
            self.can = can
            self.bus = self.can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)
        except Exception as e:
            logger.error(e)

    def charge_bms(self):
        try:
            msg = self.can.Message(arbitration_id=0x01, data=[1, 0, 0, 0, 1, 0, 0, 0], is_extended_id=False)
            self.bus.send(msg)

        except Exception as e:
            logger.error(e)


