import os
import sys
from utils import can_array_conversion, can_array_conversion_error, canarray_conv_curr
from bms.canthread import Bmsextract
from pinlayout import CELL_VOLTAGE_STOP
import logging

logger = logging.getLogger(__name__)

project_location = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(project_location)

    
class BmsReceive:
    def bms_receive(self):
        try:
            bmsextract_obj = Bmsextract()
            bmsvalues_dict = bmsextract_obj.bms_extract()
            errors_list = []
            bms_values = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                          None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                          None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                          None, None, None, None, None]
            for message_id, message in bmsvalues_dict.items():
                if message_id == 5:
                    received_data = bmsvalues_dict[5]
                    bms_values[49] = (can_array_conversion(received_data, 0, 3))  # cell_voltage_1                    

                if message_id == 6:
                    received_data = bmsvalues_dict[6]
                    bms_values[0] = '%0.4f' % (can_array_conversion(received_data, 0, 1) * (0.1 * (10 ** -3)))  # cell_voltage_1
                    bms_values[1] = '%0.4f' % (can_array_conversion(received_data, 2, 3) * (0.1 * (10 ** -3))) # cell_voltage_2
                    bms_values[2] = '%0.4f' % (can_array_conversion(received_data, 4, 5) * (0.1 * (10 ** -3))) # cell_voltage_3
                    bms_values[3] = '%0.4f' % (can_array_conversion(received_data, 6, 7) * (0.1 * (10 ** -3))) # cell_voltage_4

                elif message_id == 7:
                    received_data = bmsvalues_dict[7]
                    bms_values[4] = '%0.4f' % (can_array_conversion(received_data, 0, 1) * (0.1 * (10 ** -3))) # cell_voltage_5
                    bms_values[5] = '%0.4f' % (can_array_conversion(received_data, 2, 3) * (0.1 * (10 ** -3))) # cell_voltage_6
                    bms_values[6] = '%0.4f' % (can_array_conversion(received_data, 4, 5) * (0.1 * (10 ** -3))) # cell_voltage_7
                    bms_values[7] = '%0.4f' % (can_array_conversion(received_data, 6, 7) * (0.1 * (10 ** -3))) # cell_voltage_8

                elif message_id == 8:
                    received_data = bmsvalues_dict[8]
                    bms_values[8] = '%0.4f'%(can_array_conversion(received_data, 0, 1) * (0.1 * (10 ** -3))) # cell_voltage_9
                    bms_values[9] = '%0.4f' %(can_array_conversion(received_data, 2, 3) * (0.1 * (10 ** -3))) # cell_voltage_10
                    bms_values[10] = '%0.4f'%(can_array_conversion(received_data, 4, 5) * (0.1 * (10 ** -3))) # cell_voltage_11
                    bms_values[11] = '%0.4f'%(can_array_conversion(received_data, 6, 7) * (0.1 * (10 ** -3))) # cell_voltage_12


                elif message_id == 9:
                    received_data = bmsvalues_dict[9]
                    bms_values[12] = '%0.4f'%(can_array_conversion(received_data, 0, 1) * (0.1 * (10 ** -3))) # cell_voltage_13
                    bms_values[13] = '%0.4f'%(can_array_conversion(received_data, 2, 3) * (0.1 * (10 ** -3))) # cell_voltage_14
                    bms_values[14] = '%0.4f'%(can_array_conversion(received_data, 4, 5) * (0.1 * (10 ** -3))) # cell_voltage_15
                    bms_values[15] = '%0.4f'%(can_array_conversion(received_data, 6, 7) * (0.1 * (10 ** -3))) # cell_voltage_16

                elif message_id == 10:
                    received_data = bmsvalues_dict[10]
                    bms_values[16] = '%0.4f'%(can_array_conversion(received_data, 0, 1) * 0.1)  # limit_dc_charge_current
                    bms_values[17] = round((can_array_conversion(received_data, 2, 3) * 0.1), 4)  # limit_dc_discharge_current
                    bms_values[18] = round((can_array_conversion(received_data, 4, 5) * 0.1), 4)       # dc_charging_current
                    bms_values[19] = round((can_array_conversion(received_data, 6, 7) * 0.1), 4)       # dc_charging_voltage
                elif message_id == 11:
                    received_data = bmsvalues_dict[11]
                    bms_values[20] = '%0.4f'%(can_array_conversion(received_data, 0, 1) * 0.1)  # dc_battery_voltage
                    bms_values[21] = '%0.4f'%(canarray_conv_curr(received_data, 2, 5, 32) * (0.01 * (10 ** -3)))  # dc_battery_current
                    bms_values[22] = canarray_conv_curr(received_data, 6, 6, 8)  # battery_temp1
                    bms_values[23] = canarray_conv_curr(received_data, 7, 7, 8)  # battery_temp2

                elif message_id == 12:
                    received_data = bmsvalues_dict[12]
                    bms_values[24] = can_array_conversion(received_data, 0, 1) * (0.1 * (10 ** -3))  # cell_voltage_min
                    bms_values[25] = can_array_conversion(received_data, 2, 3) * (0.1 * (10 ** -3))  # cell_voltage_max
                    bms_values[26] = can_array_conversion(received_data, 4, 5) * 0.01  # soc_system_trimmed
                    bms_values[27] = round((canarray_conv_curr(received_data, 6, 7, 16) * 0.01), 3)  # soc_system_internal
                    if  bms_values[27] < -100 or bms_values[27] > 200:
                        bms_values[27] = 0

                elif message_id == 13:
                    received_data = bmsvalues_dict[13]
                    bms_values[28] = can_array_conversion(received_data, 0, 1) * (0.1 * (10 ** -3))  # remaining_pack_capacity
                    bms_values[29] = can_array_conversion(received_data, 2, 3) * (0.1 * (10 ** -3))  # pack_capacity_fullycharged
                    bms_values[30] = can_array_conversion(received_data, 4, 5) * 0.01                # soh
                    bms_values[31] = can_array_conversion(received_data, 6, 7) * 0.01    # bms_error_counter

                elif message_id == 14:
                    received_data = bmsvalues_dict[14]
                    bms_values[32] = can_array_conversion(received_data, 0, 0)  # status_fully_charged
                    bms_values[33] = can_array_conversion(received_data, 1, 1)  # status_fully_charged_latched
                    bms_values[34] = can_array_conversion(received_data, 2, 2)  # status_load_active
                    bms_values[35] = can_array_conversion(received_data, 3, 3)  # status_charge_active
                    bms_values[36] = can_array_conversion(received_data, 4, 4)  # status_precharge_active
                    bms_values[37] = can_array_conversion(received_data, 5, 5)  # status_balancing_active
                    bms_values[38] = can_array_conversion(received_data, 6, 6)  # status_bms
                    bms_values[39] = can_array_conversion(received_data, 7, 7)  # status_main_release

                elif message_id == 26:
                    received_data = bmsvalues_dict[26]
                    bms_values[40] = can_array_conversion_error(received_data, 2, 3)  # actualerror_num
                elif message_id == 27:
                    received_data = bmsvalues_dict[27]
                    bms_values[41] = can_array_conversion_error(received_data, 4, 7)  # booterrors_num

                elif 28 <= message_id <= 75:
                    received_data = bmsvalues_dict[message_id]
                    errors_list.append(can_array_conversion_error(received_data, 0, 1))
                    bms_values[42] = errors_list
            
            if bms_values[38] != 3:
                if bms_values[42] is not None and bms_values[40] != 0:
                    for i in range(len(bms_values[42])):
                        if bms_values[42][i] == 2005:
                            bms_values[43] = True  # battery_error_list[0] is battery_overtemperature

                        elif bms_values[42][i] == 2004:
                            bms_values[44] = True  # battery_error_list[1] is battery_undertemperature

                        elif bms_values[42][i] == 2009 or bms_values[42][i] == 2010 or bms_values[42][i] == 2008:
                            bms_values[45] = True  # battery_error_list[2] is battery_overload

                        elif bms_values[42][i] == 2000:
                            bms_values[46] = True  # battery_error_list[3] is battery_shutdown
                        elif bms_values[42][i] == 401:
                            pass
                        else:
                            bms_values[47] = True
            else:
                bms_values[42] = None
                    
                
                # display the error imaage if it is not 3
            if bms_values[24] < CELL_VOLTAGE_STOP:
                bms_values[48] = True
            else:
                bms_values[48] = False
            return bms_values
        except Exception as e:
            logger.error(e)


