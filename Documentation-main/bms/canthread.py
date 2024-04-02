import threading
import os
import logging

logger = logging.getLogger(__name__)

can_dict = {}  # global variable


class Bmsthread(threading.Thread):
    """ this is Thread which runs continously and update the can_dict(global variable)"""
    def __init__(self):
        threading.Thread.__init__(self)

        self.daemon = True
        self.start()

    def run(self):
        try:
            import can
            os.system('sudo ip link set can0 up type can bitrate 500000')
            global can_dict
            bus = can.interface.Bus(bustype='socketcan', channel='can0', baudrate=500000)

            while True:
                message = bus.recv(5)
                can_dict[message.arbitration_id] = message.data

        except Exception as e:
            logger.error(e)


class Bmsextract:
    """this is class which take can_dict(global variable which continously updatde by thread class
        and it  will return same can_dict only
        USE: if we access the directly can_dict it will print as {}, because it is starting of class,
        with this function we will get the updated value"""
    def bms_extract(self):
        global can_dict
        can_dict_copy = can_dict
        return can_dict_copy

