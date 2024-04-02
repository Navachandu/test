from statemachine import Statemachine
from batteryerrors import BatteryErrors
from temperature import TemperatureSensor
'''
Ion_hub_state = 2  -  Run
                 3  -  Stop
                 4 -  Error
                 5 - shutdown'''

class StateMachine_Error:

    ion_hub_state = 2

    def errors_Statemachine(self):

        statemachine_obj = Statemachine()
        data = statemachine_obj.getting_data()

        batteryerrors_obj = BatteryErrors()
        error,battery_empty = batteryerrors_obj.battery_errors()

        temperature_obj = TemperatureSensor()
        temperature_obj.read_temperature()

        for i in range(len(error)):
            if error[i] is True:
                self.ion_hub_state = 4


        for j in range(1,len(data[2])):  #
            if data[2][i] is True:
                self.ion_hub_state = 4


        if data[4] is True:
            self.ion_hub_state = 5

        if battery_empty is True:
            if data[2][0] is True:
                pass
            else:
                self.ion_hub_state = 5

        if data[0][22] > 50 or data[0][23] > 50:
            ionhub_temperature = 'warm'
            self.ion_hub_state = 3
        else:
            ionhub_temperature = 'ok'

        if data[0][22] < -20 or data[0][23] > -20:
            ionhub_temperature = 'cold'
            self.ion_hub_state = 3
        else:
            ionhub_temperature = 'ok'












