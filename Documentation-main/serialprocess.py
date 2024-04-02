"""this is updated code of display"""
import multiprocessing
import time
import logging
from utils import  checksum, dcarray, acarray, serial_write, serial_read, led_conversion
from pinlayout import VOLTAGE_DISCHARGE

logger = logging.getLogger(__name__)


class Serialprocess(multiprocessing.Process):
    """ this is Process which runs continously and update the can_dict(global variable)"""
    def __init__(self, number, inverter_dict):
        multiprocessing.Process.__init__(self)
        self.inverter_dict = inverter_dict
        self.inverter_dict['error_number']=None
        self.daemon = True
        self.start()

    def run(self) -> None:
        while True:
            try:

                power_arr = [None, None, None]
                invertervtg_arr = [None, None, None]
                mainspower_arr = [None, None, None]

                self.multipluserror()

                # Asking for GETINFO arrays
                #   DC ARRAY
                dc_array = [3, 255, 70, 0, 184]
                while True:
                    try:
                        serial_write(dc_array)
                        read_ser = serial_read(17)
                        response_array = [read_ser[i:i + 2] for i in range(0, len(read_ser), 2)]
                        if response_array[6].lower() == '0c':
                            dc_voltage, dccurrent_inverting, dccurrent_charging=dcarray(read_ser)
                            self.inverter_dict['dc_info'] = [dc_voltage, dccurrent_inverting, dccurrent_charging]
                            break
                        else:
                            self.batteryopertions()
                            self.setmultiplus()
                            time.sleep(0.5)
                            continue

                    except Exception as e:
                        self.batteryopertions()
                        self.setmultiplus()
                        logger.error(e)
                        time.sleep(1)
                        continue

                self.multipluserror()
                self.batteryopertions()
                self.setmultiplus()

                #   Phase 1 Array

                phase1_array = [3, 255, 70, 1, 183]
                while True:
                    try:
                        serial_write(phase1_array)
                        # reli = ser.readline().hex()
                        # response_array = [reli[i:i + 2] for i in range(0, len(read_ser), 2)]
                        read_ser = serial_read(17)
                        response_array = [read_ser[i:i + 2] for i in range(0, len(read_ser), 2)]
                        if response_array[6].lower() == '0a':
                            power_arr[0], invertervtg_arr[0], phase1_values = acarray(read_ser)
                            self.inverter_dict['phase1'] = phase1_values
                            break
                        else:
                            self.batteryopertions()
                            self.setmultiplus()
                            time.sleep(0.5)
                            continue
                    except Exception as e:
                        self.batteryopertions()
                        self.setmultiplus()
                        logger.error(e)
                        time.sleep(0.5)
                        continue

                self.multipluserror()
                self.batteryopertions()
                self.setmultiplus()

                    
                #   Phase 2 Array

                phase2_array = [3, 255, 70, 2, 182]
                while True:
                    try:
                        serial_write(phase2_array)
                        # reli = ser.readline().hex()
                        # response_array = [reli[i:i + 2] for i in range(0, len(read_ser), 2)]
                        read_ser = serial_read(17)
                        response_array = [read_ser[i:i + 2] for i in range(0, len(read_ser), 2)]
                        if response_array[6] == '07':
                            power_arr[1], invertervtg_arr[1], phase2_values = acarray(read_ser)
                            self.inverter_dict['phase2'] = phase2_values
                            break
                        else:
                            self.batteryopertions()
                            self.setmultiplus()
                            time.sleep(0.5)
                            continue
                    except Exception as e:
                        self.batteryopertions()
                        self.setmultiplus()
                        logger.error(e)
                        time.sleep(0.5)
                        continue

                self.multipluserror()
                self.batteryopertions()
                self.setmultiplus()
                    
                #   Phase 3 Array

                phase3_array = [3, 255, 70, 3, 181]
                while True:
                    try:
                        serial_write(phase3_array)
                        # reli = ser.readline().hex()
                        # response_array = [reli[i:i + 2] for i in range(0, len(read_ser), 2)]
                        read_ser = serial_read(17)
                        response_array = [read_ser[i:i + 2] for i in range(0, len(read_ser), 2)]
                        if response_array[6] == '06':
                            power_arr[2], invertervtg_arr[2], phase3_values = acarray(read_ser)
                            self.inverter_dict['phase3'] = phase3_values
                            break
                        else:
                            self.batteryopertions()
                            self.setmultiplus()
                            time.sleep(0.5)
                            continue
                    except Exception as e:
                        self.batteryopertions()
                        self.setmultiplus()
                        logger.error(e)
                        time.sleep(0.5)
                        continue
                
                
                self.inverter_dict['power'] = power_arr
                self.inverter_dict['voltage'] = invertervtg_arr

            except Exception as e:
                logger.error(e)
                time.sleep(2)
                continue


    def batteryopertions(self):
        try:
            constant = 'ff'
            f = '46'
            bol = '09'
            flag = '0f'
            bms = self.inverter_dict['bms']

            ''' voltage discharge is 45 v, so after converting into msb and lsb form we will get below values'''
            volt_disch_hex_msb = '11'
            volt_disch_hex_lsb = '94'

            # ------------current------------------

            curr_ch = bms[18]  # dc_charging_current
            fully_charge = bms[33]
            print('bms[16]',bms[16])
            print('type bms[16]',type(bms[16]))
            
            print('int bms[16]',float(bms[16]))

            if curr_ch <= 5 or fully_charge == 1:
                volt_ch = 0
                curr_ch_conv = 0
            elif float(bms[16]) >= 100:
                volt_ch = bms[19]
                curr_ch_conv = int(curr_ch * 9)
                
            else:
                volt_ch = bms[19]
                curr_ch_conv = int(curr_ch * 6)
            print('curr_ch_conv',curr_ch_conv)

            volt_ch_conv = int(volt_ch * 100)
            volt_ch_hex = "0x{:04x}".format(volt_ch_conv)
            volt_ch_hex_msb = volt_ch_hex[2:4]
            volt_ch_hex_lsb = volt_ch_hex[4:6]

            curr_ch_hex = "0x{:06x}".format(curr_ch_conv)
            curr_ch_hex_msb = curr_ch_hex[2:4]
            curr_ch_hex_mid = curr_ch_hex[4:6]
            curr_ch_hex_lsb = curr_ch_hex[6:8]
            self.inverter_dict['bol_current'] = curr_ch_conv


            curr_disch = bms[17]  # Limit_DC_discharge_current
            curr_disch_conv = int(curr_disch * 10)
            curr_disch_hex = "0x{:06x}".format(curr_disch_conv)
            curr_disch_hex_msb = curr_disch_hex[2:4]
            curr_disch_hex_mid = curr_disch_hex[4:6]
            curr_disch_hex_lsb = curr_disch_hex[6:8]

            # ---------creating the communication array--------------

            comm_arr = [constant, f, bol, flag, volt_ch_hex_lsb, volt_ch_hex_msb, curr_ch_hex_lsb,
                        curr_ch_hex_mid, curr_ch_hex_msb, volt_disch_hex_lsb, volt_disch_hex_msb, curr_disch_hex_lsb,
                        curr_disch_hex_mid, curr_disch_hex_msb]
            length = "{:02x}".format(len(comm_arr))

            comm_arr.insert(0, length)

            # --------checksum calculation----------------

            checksum_value = checksum(comm_arr)

            comm_arr.append(checksum_value)

            # --------conversion of comm_arr in different forms

            comm_arr1 = []
            for i in range(len(comm_arr)):
                s = '0x' + comm_arr[i]
                comm_arr1.append(int(s, 16))


            # --------------------For serial communication(Transfer)
            serial_write(comm_arr1)
            #self.ser.write(self.serial.to_bytes(comm_arr1))

        except OSError:
            logger.error('Couldnt open port. Please check the port')
        except Exception as e:
            time.sleep(1)
            logger.error(e)



    def setmultiplus(self):
        try:
            # ------------ flags-----------------
            constant = 'ff'
            S = '53'
            switch_state = "{:02x}".format(self.inverter_dict['switch_state'])
            constant1 = '01'
            flag = '80'
            current = self.inverter_dict['current']  # current

            curr_ch = current
            curr_ch_conv = int(curr_ch * 10)
            curr_ch_hex = "0x{:04x}".format(curr_ch_conv)
            curr_ch_hex_msb = curr_ch_hex[2:4]
            curr_ch_hex_lsb = curr_ch_hex[4:6]

            # ---------creating the communication array--------------
            # here curr_ch_hex_LSB, curr_ch_hex_MSB, no self. for these variables because these are method variables
            comm_arr = [constant, S, switch_state,curr_ch_hex_lsb, curr_ch_hex_msb,  constant1,
                        flag]
            
            length = "{:02x}".format(len(comm_arr))
            comm_arr.insert(0, length)
            

            # --------checksum calculation----------------
            checksum_value = checksum(comm_arr)
            comm_arr.append(checksum_value)

            # --------conversion of comm_arr in different forms
            comm_arr1 = []
            for i in range(len(comm_arr)):
                s = '0x' + comm_arr[i]
                comm_arr1.append(int(s, 16))

            # -----------------Serial Communication(transfer)----

            i = 0
            while i < 2:
                serial_write(comm_arr1)
                i = i + 1
        except Exception as e:
            logger.error(e)
            time.sleep(2)


    def multipluserror(self):
        while True:
            try:
                import serial
                ser = serial.Serial('/dev/ttyUSB0', baudrate=2400, timeout=0.5, bytesize=8,
                                    stopbits=serial.STOPBITS_ONE)

                multipluserrors_list = [False, False, False, False, False, False, False, False, False, False, False,
                                        False, False, False, False, False, False, False, False, False, False, False,
                                        [False, False, False, False, False]]
                error_arr = [2, 255, 76, 179]
                while True:
                    try:
                        serial_write(error_arr)
                        ser.reset_output_buffer()
                        reli = ser.readline().hex()
                        response_array = [reli[i:i + 2] for i in range(0, len(reli), 2)]

                        if reli[4:6] == '4c' and checksum(response_array) == '00':
                            break
                        else:
                            self.batteryopertions()
                            continue
                    except Exception as e:
                        self.batteryopertions()
                        logger.error(e)
                        time.sleep(0.5)
                        continue
                ser.reset_input_buffer()

                # =========== Dividing the array ================
                if checksum(response_array) == '00':

                    # ================ LED ON ========================
                    led_on = led_conversion(response_array[3])

                    # ================ LED BLINK ========================
                    led_blink = led_conversion(response_array[4])

                    if led_blink[7] == '1':
                        multipluserrors_list[22][4] = True  # Inverter_Overtemperature warning

                    if led_on[7] == '1':
                        multipluserrors_list[22][2] = True  # Inverter_Overtemperature Alaram

                    elif led_on[5] == '1':
                        multipluserrors_list[22][1] = True  # Inverter_Overload Alaram

                    elif led_blink[5] == '1':
                        multipluserrors_list[22][3] = True  # Inverter_Overload warning

                    elif led_blink[4] == 0 or led_on[4] == 0:
                        print('eneter in multiplus error ')
                        if led_on[1] ==1 or led_on[2] == 1 or led_on[3] == 1 or led_blink[1] == 1 or led_blink[2] == 1 or led_blink[3]==1 :
                            multipluserrors_list[22][0] = True  # Error
                            self.inverter_dict['error_number']=str(int(led_on+led_blink,2))

                    elif led_on[0] == '1':
                        multipluserrors_list[0] = True

                    elif led_on[4] == '1':
                        multipluserrors_list[1] = True

                    else:
                        pass
                else:
                    pass
                self.inverter_dict['time'] = time.time()
                self.inverter_dict['errors'] = multipluserrors_list
                break
            except Exception as e:
                logger.error(e)
                time.sleep(0.5)
                continue
            
'''            
def multipluserror(self):
    while True:
        try:
            import serial
            ser = serial.Serial('/dev/ttyUSB0', baudrate=2400, timeout=0.5, bytesize=8,
                                stopbits=serial.STOPBITS_ONE)

            multipluserrors_list = [False, False, False, False, False, False, False, False, False, False, False,
                                    False, False, False, False, False, False, False, False, False, False, False,
                                    [False, False, False, False, False]]
            error_arr = [2, 255, 76, 179]
            while True:
                try:
                    serial_write(error_arr)
                    ser.reset_output_buffer()
                    reli = ser.readline().hex()
                    response_array = [reli[i:i + 2] for i in range(0, len(reli), 2)]

                    if reli[4:6] == '4c' and checksum(response_array) == '00':
                        break
                    else:
                        continue
                except Exception as e:
                    logger.error(e)
                    time.sleep(1)
                    continue
            ser.reset_input_buffer()

            # =========== Dividing the array ================
            if checksum(response_array) == '00':

                # ================ LED ON ========================
                led_on = led_conversion(response_array[3])

                # ================ LED BLINK ========================
                led_blink = led_conversion(response_array[4])
                # print('led_blink', led_blink)

                if led_on[5:7] == '11':  # 109 multiplus ripple alarm
                    multipluserrors_list[21] = True
                    multipluserrors_list[22][0] = True  # Inverter Error

                elif led_on[6] == '1':  # 103 multiplus low battery alarm
                    multipluserrors_list[16] = True

                elif led_on[7] == '1':  # 105 multiplus temperature alarm
                    multipluserrors_list[18] = True
                    multipluserrors_list[22][2] = True  # Inverter_Overtemperature Error

                elif led_on[5] == '1':  # 101 multiplus overload alarm
                    multipluserrors_list[14] = True
                    multipluserrors_list[22][1] = True  # Inverter_Overload Error

                elif led_on[5:7] == '11':  # 108 multiplus ripple warning
                    multipluserrors_list[20] = True

                elif led_on[0] == '1':
                    multipluserrors_list[0] = True

                elif led_on[0] == '0':
                    multipluserrors_list[0] = False

                else:
                    print('multiplus error wrong response')

                self.inverter_dict['time'] = time.time()
                self.inverter_dict['errors'] = multipluserrors_list
                break
            else:
                print('multiplus error some error occured')
        except Exception as e:
            logger.error(e)
            time.sleep(1)
            continue
               
'''


            
            



