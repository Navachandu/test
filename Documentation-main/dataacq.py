import pandas as pd
import logging
logger = logging.getLogger(__name__)
import os
import csv
import datetime as dt


class main_data:
    
    final_df = {'time': None, 'ionhub_2': None,'ionhub_3': None, 'ionhub_4' : None, 'ionhub_5':None,'dc_charging_current_min':None,'dc_charging_current_max':None,
            'dc_battery_voltage_min':None,'dc_battery_voltage_max':None,'battery_temp1_min' : None,'battery_temp1_max':None,'battery_temp2_min':None,
            'battery_temp2_max':None,'cell_voltage_min' : None, 'cell_voltage_max':None,'soc_system_trimmed_min':None,'soc_system_trimmed_max':None,
            'soh':None, 'status_balancing_active':None, 'status_bms_1':None, 'status_bms_2':None,'status_bms_3':None,'actualerror_num':None, 'booterrors_num':None,
            'gridsupply':None, 'inverter_switch_state_1':None,'inverter_switch_state_2':None, 'inverter_switch_state_3':None,'inverter_switch_state_4':None, 'grid_interrupt':None,
            'wallbox':None, 'circuit_breaker':None,'Energy_min':None,'Energy_max':None, 'temperature_min':None,'temperature_max':None,'DC_voltage_min':None, 'DC_voltage_max':None,
            'DC_current_inverting_min':None, 'DC_current_inverting_max':None, 'DC_current_charging_min':None, 'DC_current_charging_max':None, 'phase1_power':None, 'phase2_power':None,
            'phase3_power':None, 'bms_error':None}

    header = ['time','ionhub_2', 'ionhub_3', 'ionhub_4', 'ionhub_5', 'dc_charging_current_min', 'dc_charging_current_max',
              'dc_battery_voltage_min', 'dc_battery_voltage_max', 'battery_temp1_min',
              'battery_temp1_max', 'battery_temp2_min', 'battery_temp2_max', 'cell_voltage_min', 'cell_voltage_max',
              'soc_system_trimmed_min', 'soc_system_trimmed_max', 'soh', 'status_balancing_active', 'status_bms_1',
              'status_bms_2',
              'status_bms_3', 'actualerror_num', 'booterrors_num', 'gridsupply', 'inverter_switch_state_1',
              'inverter_switch_state_2',
              'inverter_switch_state_3', 'inverter_switch_state_4', 'grid_interrupt', 'wallbox', 'circuit_breaker',
              'Energy_min', 'Energy_max',
              'temperature_min', 'temperature_max', 'DC_voltage_min', 'DC_voltage_max',
              'DC_current_inverting_min', 'DC_current_inverting_max', 'DC_current_charging_min',
              'DC_current_charging_max', 'phase1_power', 'phase2_power', 'phase3_power', 'bms_error']
    def hour_data(self,file_name):
        df = pd.read_csv(file_name, low_memory=False) # here file name should be there
        start_index = 0
        batch_size = 3600
        
        while start_index < len(df):
            file_exist = os.path.isfile('hour_file.csv')
            end_index = start_index+batch_size
            if end_index<len(df):
                pass
            else:
                end_index=len(df)
            df_hour = df.iloc[start_index:end_index]

            self.final_df['time'] = df_hour['time'].iloc[1]
            # IONHUB COUNT
            self.final_df['ionhub_2'] = (df_hour['ionhub state'] == 2).sum()
            self.final_df['ionhub_3'] = (df_hour['ionhub state'] == 3).sum()
            self.final_df['ionhub_4'] = (df_hour['ionhub state'] == 4).sum()
            self.final_df['ionhub_5'] = (df_hour['ionhub state'] == 5).sum()
        
            # DC_CHARGING_CURRENT
            self.final_df['dc_charging_current_min'] = df_hour['dc_charging_current'].min()
            self.final_df['dc_charging_current_max'] = df_hour['dc_charging_current'].max()
        
            # DC_BATTERY_CURRENT
            self.final_df['dc_battery_voltage_min'] = df_hour['dc_battery_current'].min()
            self.final_df['dc_battery_voltage_max'] = df_hour['dc_battery_current'].max()
        
            # BATTERY TEMPERATURES
            self.final_df['battery_temp1_min'] = df_hour['battery_temp1'].min()
            self.final_df['battery_temp1_max'] = df_hour['battery_temp1'].max()
            self.final_df['battery_temp2_min'] = df_hour['battery_temp2'].min()
            self.final_df['battery_temp2_max'] = df_hour['battery_temp2'].max()
        
            self.final_df['cell_voltage_min'] = df_hour['cell_voltage_min'].min()
            self.final_df['cell_voltage_max'] = df_hour['cell_voltage_max'].max()
        
            # SOC_SYSTEM_TRIMMED
        
            self.final_df['soc_system_trimmed_min'] = df_hour['soc_system_trimmed'].min()
            self.final_df['soc_system_trimmed_max'] = df_hour['soc_system_trimmed'].max()
        
            # SOH
            self.final_df['soh'] = df_hour['soh'].mean()
        
            # status_balancing_active
            self.final_df['status_balancing_active'] = (df_hour['status_balancing_active'] == 1).sum()
        
            # status_bms
            self.final_df['status_bms_1'] = (df_hour['status_bms'] == 1).sum()
            self.final_df['status_bms_2'] = (df_hour['status_bms'] == 2).sum()
            self.final_df['status_bms_3'] = (df_hour['status_bms'] == 3).sum()
        
            # actual and boot errors
            self.final_df['actualerror_num'] = df_hour['actualerror_num'].max()
            self.final_df['booterrors_num'] = df_hour['booterrors_num'].max()
        
            # GRID SUPPLY
            self.final_df['gridsupply'] = (df_hour['gridsupply']).sum()
        
            # INVERTER SWITCH COUNT
            self.final_df['inverter_switch_state_1'] = (df_hour['inverter_switch_state'] == 1).sum()
            self.final_df['inverter_switch_state_2'] = (df_hour['inverter_switch_state'] == 2).sum()
            self.final_df['inverter_switch_state_3'] = (df_hour['inverter_switch_state'] == 3).sum()
            self.final_df['inverter_switch_state_4'] = (df_hour['inverter_switch_state'] == 4).sum()
        
            # GRID INTERRUPT
            self.final_df['grid_interrupt'] = (df_hour['grid_interrupt']).sum()
        
            # WALLBOX
            self.final_df['wallbox'] = (df_hour['wallbox'] != 100).sum()
        
            # CIRCUIT BREAKER
            self.final_df['circuit_breaker'] = (df_hour['circuit_breaker'] == 0).sum()
        
            # ENERGY
            self.final_df['Energy_min'] = df_hour['Energy'].min()
            self.final_df['Energy_max'] = df_hour['Energy'].max()
        
            # TEMPERATURE
            self.final_df['temperature_min'] = df_hour['temperature'].min()
            self.final_df['temperature_max'] = df_hour['temperature'].max()
        
            # DC VOLTAGE
            self.final_df['DC_voltage_min'] = df_hour['DC_voltage'].min()
            self.final_df['DC_voltage_max'] = df_hour['DC_voltage'].max()
        
            # DC_current_inverting
            self.final_df['DC_current_inverting_min'] = df_hour['DC_current_inverting'].min()
            self.final_df['DC_current_inverting_max'] = df_hour['DC_current_inverting'].max()
        
            # DC_current_charging
            self.final_df['DC_current_charging_min'] = df_hour['DC_current_charging'].min()
            self.final_df['DC_current_charging_max'] = df_hour['DC_current_charging'].max()
        
            # PHASE POWER
            self.final_df['phase1_power'] = (df_hour['phase1_Inverter_voltage'].max()) * (df_hour['phase1_Inverter_current'].max())
            self.final_df['phase2_power'] = (df_hour['phase2_Inverter_voltage'].max()) * (df_hour['phase2_Inverter_current'].max())
            self.final_df['phase3_power'] = (df_hour['phase3_Inverter_voltage'].max()) * (df_hour['phase3_Inverter_current'].max())
            
            # ERRORS
            bms_errors = []
            while start_index < end_index:
                p = df_hour['errors_list'][start_index]
                if pd.isna(p) == True:
                    pass
                else:
                    a = p.strip('[]').split(',')
                    for i in a:
                        if i not in bms_errors:
                            bms_errors.append(i)
                start_index+=1
            self.final_df['bms_error'] = bms_errors

            with open('hour_file.csv', mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.header)
                print(file_exist)
                if not file_exist:
                    print('inside file exit')
                    writer.writeheader()
                writer.writerows([self.final_df])
            start_index=end_index
