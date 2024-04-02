import logging
import multiprocessing
from bms.bmsreceive import BmsReceive
from gridcontrol import GridControl
from invertercontrol import InverterControl
from gridinterrupt import GridButton
from pinlayout import CIRCUIT_BREAKER, FAN_CONTROL
from checkduty1 import DutyCycle
from serialprocess import Serialprocess
from dispandtempprocess import Dispandtemp
import numpy as np
from globalvar import write_ionhub_state, read_ionhub_state, read_battery_empty, read_soc_stop_inverter,write_old_energy
from globalvar import read_full_charge, read_soc_offset, write_soc_offset, read_old_energy, write_full_charge
import math

'''
Ion_hub_state = 2  -  Run
                 3  -  Stop
                 4 -  Error
                 5 - shutdown'''

# """ this function needs to return two values"""
logger = logging.getLogger(__name__)


class Statemachine:
    # ion_hub_state = 2
    # write_ionhub_state(2)
    data = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
    avg_power = []
    avg_voltage = []
    power = 0

    def __init__(self):
        try:
            import RPi.GPIO
            self.GPIO = RPi.GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            manager = multiprocessing.Manager()
            self.inverter_dict = manager.dict()
            self.display_dict = manager.dict()
            self.process = Serialprocess(2, self.inverter_dict)  # 2 is just a random number
            self.process = Dispandtemp(3, self.display_dict)
            self.display_dict['charge_status'] = None
            self.display_dict['power_status'] = None
            self.display_dict['energy_status'] = None
            self.display_dict['status'] = None
            self.display_dict['error'] = None
            self.display_dict['chargepower_status'] = None
            self.display_dict['phase_power'] = None

        except Exception as e:
            logger.error(e)

    def getting_data(self, battery_empty):
        try:
            bmsreceive_obj = BmsReceive()
            can_values = bmsreceive_obj.bms_receive()
            self.data[0] = can_values
            self.data[9] = can_values[48]

            self.inverter_dict['bms'] = self.data[0]
            calculated_energy = ((self.data[0][27] - battery_empty) / (100 - battery_empty)) * 100

            # Getting Duty Cycle
            dutycycle_obj = DutyCycle()
            percent = dutycycle_obj.duty_cycle()
            self.data[5] = percent

            ''' Circuit breaker'''
            self.GPIO.setup(CIRCUIT_BREAKER, self.GPIO.IN)
            circuit_break = self.GPIO.input(CIRCUIT_BREAKER)
            self.data[6] = circuit_break

            self.data[2] = self.inverter_dict['errors']
            gridsupply = self.data[2][0]

            phase_voltage = self.inverter_dict['voltage']
            voltage = 230 if all(volt > 100 for volt in phase_voltage) else 0

            gridinterrupt_obj = GridButton(self.data[0][27], voltage, self.data[0][33])
            grid_interrupt, shutdown_trigger, standby, button_status = gridinterrupt_obj.setgridinterrupt()
            self.data[3] = grid_interrupt
            self.data[4] = shutdown_trigger
            self.data[17] = button_status
            # may be after the grid interrupt,finalize the ionhub whether 2 or 3 and write to txt file

            power_arr = self.inverter_dict['power']
            charge_power = (float(self.data[0][21]) / 85) * 100
            self.display_dict['chargepower_status'] = charge_power

            if all(volt > 100 for volt in phase_voltage):
                disp_voltage = 230
            elif all(volt < 100 for volt in phase_voltage):
                disp_voltage = 0
            else:
                disp_voltage = 101

            if self.data[0][38] != 3 and voltage < 100:  # this condition is for when we reach
                self.data[2] = [False, False, False, False, False, False, False, False, False, False, False,
                                False, False, False, False, False, False, False, False, False, False, False,
                                [False, False, False, False, False]]
                power_arr = [0, 0, 0]

            # RUN STATE
            ''' this normal state, it will make display status'''

            self.ion_hub_state = int(read_ionhub_state())

            if standby == 3:
                self.display_dict['status'] = 3
            elif standby == 5:
                self.display_dict['status'] = 5
                print('stand shut')
            elif standby == 9:
                self.display_dict['status'] = 9
            else:
                self.display_dict['status'] = None
                
            
            if circuit_break == 1:
                self.display_dict['status'] = 14
                self.display_dict['error'] = (2,None)
                

            # ERROR STATE
            '''here it will check the system errors and make the ionhub status and display status'''

            if ((self.data[0][47] is True) and standby != 3) or (self.data[2][22][0] is True):  # Battery Error  and Inverter Error
                if self.data[2][22][0] is True:
                    self.display_dict['error'] = (2,self.inverter_dict['error_number'])
                    logger.error('unknown inverter error')
                else:
                    self.display_dict['error'] = (3,self.data[0][42])
                    logger.error('unknown battery error')
                    logger.error(self.data[0])
                self.ion_hub_state = 4  # ionhub_state  = Error
                write_ionhub_state(4)
                self.display_dict['status'] = 8

            elif (self.data[0][43] is True) or (self.data[0][44] is True) or (self.data[0][45] is True):
                logger.error(self.data[0])
                self.ion_hub_state = 4
                write_ionhub_state(4)
                self.display_dict['error'] = (3,None)
                if (self.data[0][43] is True) and standby != 3:
                    logger.error('battery error,status hot')
                    self.display_dict['status'] = 7
                elif self.data[0][44] is True and standby != 3:
                    self.display_dict['status'] = 6
                    logger.error('battery error,status cold')
                #  elif (self.data[0][45] is True) or (self.data[2][22][1] is True)
                elif (self.data[0][45] is True) and standby != 3:
                    self.display_dict['status'] = 4
                    logger.error('battery error,status overload ')

            # SHUTDOWN state
            ''' this is shutdown state and it will make the ionhub = 5'''
            if self.data[4] is True:  # Shutdown Trigger
                self.ion_hub_state = 5  # ionhub_state = Shutdown
                write_ionhub_state(5)
                self.display_dict['status'] = 5
                logger.error('pressed 20 sec')

            if self.data[0][24] < 2.5:  # battery empty
                if voltage < 100:
                    self.ion_hub_state = 5  # ionhub_state = Shutdown
                    write_ionhub_state(5)
                    self.display_dict['status'] = 5
                    logger.error('less than 2.5 reached')
            if self.ion_hub_state == 2:
                if len(self.avg_voltage) > 600:
                    if all(volt == 230 for volt in self.avg_voltage) and gridsupply is False and self.ion_hub_state == 2 and self.data[2][22][4] is False and self.data[2][22][3] is False:
                        self.display_dict['status'] = 13
                        logger.error('three phase error')
                        if len(self.avg_voltage) > 602:
                            self.avg_voltage.pop(0)
                    elif all(volt == 101 for volt in self.avg_voltage):
                        self.display_dict['status'] = 12
                        logger.error('single phase error')
                        if len(self.avg_voltage) > 602:
                            self.avg_voltage.pop(0)
                    else:
                        del self.avg_voltage[:]
                        
                    self.display_dict['error'] = (2,None)
                else:
                    self.avg_voltage.append(disp_voltage)
            else:
                del self.avg_voltage[:]
            

            # after this write ionhub state once more whether it is 4 or 5
            # RETURN IOBHUB STATE IN THE STATE MACHINE AND WRITE IT IN MAIN PROGRAM

            if self.ion_hub_state == 5:
                self.display_dict['status'] = 5
                self.display_dict['error'] = (2,None)
            elif self.data[2][22][2] is True and self.data[2][22][4] is False and standby != 3:
                self.display_dict['status'] = 7
                self.display_dict['error'] = (2,None)
                logger.error('inverter status hot')
                if voltage < 100:
                    self.data[2] = [False, False, False, False, False, False, False, False, False, False, False,
                                    False, False, False, False, False, False, False, False, False, False, False,
                                    [False, False, False, False, False]]
            elif self.data[2][22][1] is True and standby != 3:
                self.display_dict['status'] = 4
                self.display_dict['error'] = (2,None)
                logger.error('inverter status overload')
                if voltage < 100:
                    self.data[2] = [False, False, False, False, False, False, False, False, False, False, False,
                                    False, False, False, False, False, False, False, False, False, False, False,
                                    [False, False, False, False, False]]
            elif self.data[2][22][4] is True and standby != 3:
                self.display_dict['status'] = 11
                self.display_dict['error'] = (2,None)
                logger.error('inverter status warm')
            elif self.data[2][22][3] is True and standby != 3:
                self.display_dict['status'] = 10
                self.display_dict['error'] = (2,None)
                logger.error('inverter status highload')

            gridcontrol_obj = GridControl(self.ion_hub_state, self.data[3], self.data[5], self.data[2])
            # sending as follows ionhub_state,grid interrupt, dutycycle_percent, grid_supply
            current = gridcontrol_obj.setlimits()

            self.inverter_dict['current'] = current
            energy_value = math.ceil(calculated_energy + float(read_soc_offset()))

            
            if energy_value < 0:
                energy_value = 0

            invertercontrol_obj = InverterControl(self.ion_hub_state, self.data[3], self.data[9], energy_value,
                                                  gridsupply, self.data[0][27], self.data[0][33])
            # sending as follows ionhub_state,button_status, battery_empty, charging, grid supply
            inverter_switch_state_multiplus = invertercontrol_obj.setinverters()

            self.data[1] = inverter_switch_state_multiplus
            self.inverter_dict['switch_state'] = inverter_switch_state_multiplus

            if self.data[0][33] == 1:
                write_soc_offset(0)
                # write_full_charge(1)
                self.data[7] = 100
            elif self.data[0][48] is True:
                write_soc_offset(0)
                write_old_energy(0)
                self.data[7] = 0
            elif energy_value >= 100 and self.data[0][33] != 1:
                self.data[7] = 99
            else:
                self.data[7] = int(energy_value)

            self.display_dict['energy_status'] = self.data[7]

            if len(self.avg_power) > 100:  # checking 100 values because averaging power for 25 sec
                self.power = round((np.mean(self.avg_power)) / 72)
                del self.avg_power[:]
                self.data[8] = self.power
                self.display_dict['power_status'] = self.power

            else:
                self.avg_power.append(int(sum(power_arr)))

            if self.data[1] == 1 and voltage < 100:
                self.data[16] = 5  # value =5 charge only
                charge_value = 5
            elif self.data[1] == 1:
                charge_value = 3  # value = 3 then charge_in
                self.data[16] = 3
            elif voltage > 100 and inverter_switch_state_multiplus == 2:
                charge_value = 6  # value = 2 then in
                self.data[16] = 6
            elif voltage > 100:
                charge_value = 2   # value = 2 then in
                self.data[16] = 2
            else:
                charge_value = 4  # else out
                self.data[16] = 4

            # self.data[9] = charge_value
            self.display_dict['charge_status'] = charge_value

            self.data[10] = self.display_dict['temperature']
            self.GPIO.setup(FAN_CONTROL, self.GPIO.OUT)

            if self.data[10] > 32 or ((self.power > 50 or self.data[2][22][4] is True or self.data[2][22][3] is True or self.data[2][22][1] is True or self.data[2][22][2] is True) and self.data[10] > 10):
                self.GPIO.output(FAN_CONTROL, 1)
                self.data[11] = 'ON'
            elif self.data[10] < 28:
                self.GPIO.output(FAN_CONTROL, 0)
                self.data[11] = 'OFF'
            self.data[12] = self.inverter_dict['phase1']
            self.data[13] = self.inverter_dict['phase2']
            self.data[14] = self.inverter_dict['phase3']
            self.display_dict['phase_power'] = [self.data[12][3], self.data[13][3], self.data[14][3]]
            self.data[15] = self.inverter_dict['dc_info']

            return self.data, self.ion_hub_state, voltage  # because self.ion_hub_state is RUN

        except Exception as e:
            logger.error(e)

