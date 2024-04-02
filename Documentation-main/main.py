import logging
import os
import time
import datetime as dt
import numpy as np
import csv
from statemachine import Statemachine
from startingsequence import StartingExecution
from globalvar import write_inverter_switch_state, write_start_shutdown_timer,write_start_gridinterrupt_timer,write_full_charge
from globalvar import write_ionhub_state, write_battery_empty, write_voltage, write_old_energy, read_battery_empty, read_soc_stop_inverter,write_soc_offset
from bms.bmscharge import BmsCharge
from bms.canthread import Bmsthread
from pinlayout import FAN_CONTROL
from epaper.examples.display import Epaper
#from dataacq import main_data
import serial
ser = serial.Serial('/dev/ttyUSB0', baudrate=2400, timeout=0.5, bytesize=8, stopbits=serial.STOPBITS_ONE)
logname = f'{dt.datetime.today().date()}'
logpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(filename=f'{logpath}/{logname}.log', level=logging.INFO,
                    format='%(filename)s : %(asctime)s: %(message)s')
    

if __name__ == '__main__':
    while True:
        try:
            
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(FAN_CONTROL, GPIO.OUT)
            GPIO.output(FAN_CONTROL, 0)

            epaper_obj = Epaper()
            epaper_obj.start_display()
            
            
            last_month_file = f'{dt.datetime.today().date() - dt.timedelta(weeks=4)}.csv'
            last_month_log = f'{dt.datetime.today().date() - dt.timedelta(weeks=4)}.log'

            
            if os.path.isfile(last_month_file) is True:
                #main_data_obj.hour_data(last_month_file)
                os.remove(last_month_file)
            if os.path.isfile(last_month_log) is True:
                os.remove(last_month_log)
            ser.reset_output_buffer()
            ser.flushOutput()
            ser.write(serial.to_bytes([7, 255, 83, 4, 50, 0, 1, 128, 240]))

            display_timer = 0
            power_arr = np.array([0, 0, 0])

            # starting the thread
            bmsthread_obj = Bmsthread()
            
            # making the shutdown timer and grid timer to zero
            write_start_gridinterrupt_timer(0)
            write_start_shutdown_timer(0)
            write_voltage(0)
            write_old_energy(0)
            write_inverter_switch_state(4)
            write_ionhub_state(2)
            write_full_charge(0)

            # Starting Sequence
            startingsequence_obj = StartingExecution()
            startingsequence_obj.start_sequence()
            logging.info('the starting sequence is done')
            
            time.sleep(3)
            bmscharge_obj = BmsCharge()
            bmscharge_obj.charge_bms()
            time.sleep(2)
            bmscharge_obj.charge_bms()
            statemachine_obj = Statemachine()   # calling this class at here only because of writing ionhub_state
            time.sleep(4)
            bmscharge_obj.charge_bms()
            time.sleep(3)
            bmscharge_obj.charge_bms()
            time.sleep(3)
            bmscharge_obj.charge_bms()

            header_name = ['time', 'ionhub state', 'cell_voltage_1', 'cell_voltage_2', 'cell_voltage_3',
                           'cell_voltage_4', 'cell_voltage_5', 'cell_voltage_6', 'cell_voltage_7', 'cell_voltage_8',
                           'cell_voltage_9', 'cell_voltage_10', 'cell_voltage_11', 'cell_voltage_12', 'cell_voltage_13',
                           'cell_voltage_14', 'cell_voltage_15',
                           'cell_voltage_16', 'limit_dc_charge_current', 'limit_dc_discharge_current',
                           'dc_charging_current', 'dc_charging_voltage', 'dc_battery_voltage', 'dc_battery_current',
                           'battery_temp1', 'battery_temp2', 'cell_voltage_min', 'cell_voltage_max',
                           'soc_system_trimmed', 'soc_system_internal',
                           'remaining_pack_capacity', 'pack_capacity_fullycharged', 'soh', 'bms_error_counter',
                           'status_fully_charged', 'status_fully_charged_latched', 'status_load_active',
                           'status_charge_active', 'status_precharge_active', 'status_balancing_active', 'status_bms',
                           'status_main_release', 'actualerror_num',
                           'booterrors_num', 'errors_list', 'gridsupply', 'inverter_switch_state',
                           'multipluserrors_list', 'grid_interrupt', 'shutdown_trigger', 'wallbox', 'circuit_breaker',
                           'Energy', 'power', 'charge_status', 'temperature', 'Fan', 'DC_voltage',
                           'DC_current_inverting', 'DC_current_charging',
                           'phase1_Mains_voltage', 'phase1_Mains_current', 'phase1_Inverter_voltage',
                           'phase1_Inverter_current', 'phase2_Mains_voltage', 'phase2_Mains_current',
                           'phase2_Inverter_voltage', 'phase2_Inverter_current', 'phase3_Mains_voltage',
                           'phase3_Mains_current', 'phase3_Inverter_voltage',
                           'phase3_Inverter_current', 'button_status']
            
            #main_data_obj = main_data()
            starting_time = time.time()
            while True:
                try:
                    p=time.time()
                    battery_empty = float(read_battery_empty())
                    data, ionhub_state, voltage = statemachine_obj.getting_data(battery_empty)

                    if ionhub_state == 2:
                        if float(read_soc_stop_inverter()) == 1 and voltage < 100:
                            pass
                        else:
                            bmscharge_obj.charge_bms()
                    elif ionhub_state == 3:
                        pass
                    elif ionhub_state == 5:
                        print('its going to shutdown')
                        time.sleep(25)  # this time is to display the shudown image
                        logging.info('its going to shutdown')
                        os.system('sudo shutdown now')


                    elif ionhub_state == 4:
                        bmscharge_obj.charge_bms()

                    if time.time() - starting_time > 1:
                        data = [{'time':  dt.datetime.now().time(), 'ionhub state': ionhub_state, 'cell_voltage_1': data[0][0], 'cell_voltage_2':data[0][1], 'cell_voltage_3':data[0][2], 'cell_voltage_4':data[0][3], 'cell_voltage_5':data[0][4], 'cell_voltage_6':data[0][5], 'cell_voltage_7':data[0][6], 'cell_voltage_8':data[0][7], 'cell_voltage_9':data[0][8], 'cell_voltage_10':data[0][9], 'cell_voltage_11':data[0][10], 'cell_voltage_12':data[0][11], 'cell_voltage_13':data[0][12], 'cell_voltage_14':data[0][13], 'cell_voltage_15':data[0][14],
                                'cell_voltage_16':data[0][15], 'limit_dc_charge_current':data[0][16], 'limit_dc_discharge_current':data[0][17], 'dc_charging_current':data[0][18], 'dc_charging_voltage':data[0][19], 'dc_battery_voltage':data[0][20], 'dc_battery_current':data[0][21], 'battery_temp1':data[0][22], 'battery_temp2':data[0][23], 'cell_voltage_min':data[0][24], 'cell_voltage_max':data[0][25], 'soc_system_trimmed':data[0][26], 'soc_system_internal':data[0][27],
                                'remaining_pack_capacity':data[0][28], 'pack_capacity_fullycharged':data[0][29], 'soh':data[0][30], 'bms_error_counter':data[0][31], 'status_fully_charged':data[0][32], 'status_fully_charged_latched':data[0][33], 'status_load_active':data[0][34], 'status_charge_active':data[0][35], 'status_precharge_active':data[0][36], 'status_balancing_active':data[0][37], 'status_bms':data[0][38], 'status_main_release':data[0][39], 'actualerror_num':data[0][40],
                                'booterrors_num':data[0][41], 'errors_list':data[0][42], 'gridsupply':data[2][0], 'inverter_switch_state':data[1], 'multipluserrors_list':data[2], 'grid_interrupt':data[3], 'shutdown_trigger':data[4], 'wallbox':data[5], 'circuit_breaker':data[6],'Energy': data[7], 'power':data[8], 'charge_status':data[16] , 'temperature':data[10], 'Fan':data[11], 'DC_voltage':data[15][0], 'DC_current_inverting':data[15][1], 'DC_current_charging':data[15][2],
                                'phase1_Mains_voltage':data[12][0], 'phase1_Mains_current':data[12][1], 'phase1_Inverter_voltage':data[12][2], 'phase1_Inverter_current':data[12][3], 'phase2_Mains_voltage':data[13][0], 'phase2_Mains_current':data[13][1], 'phase2_Inverter_voltage':data[13][2], 'phase2_Inverter_current':data[13][3], 'phase3_Mains_voltage':data[14][0], 'phase3_Mains_current':data[14][1], 'phase3_Inverter_voltage':data[14][2], 'phase3_Inverter_current':data[14][3], 'button_status':data[17]}]
                        file_exist = os.path.isfile(f'{dt.datetime.today().date()}.csv')

                        with open(f'{dt.datetime.today().date()}.csv', mode='a', newline='') as file:
                            writer = csv.DictWriter(file, fieldnames=header_name)
                            if not file_exist:
                                writer.writeheader()
                            writer.writerows(data)

                        
                        
                        starting_time = time.time()

                except Exception as e:
                    print(e)
                    logging.error(e)
                    time.sleep(1)
                    continue

        except Exception as e:
            print(e)
            write_soc_offset(0)
            logging.error(e)
            time.sleep(2)
            continue
        
