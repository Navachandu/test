import time
import logging
from globalvar import (write_start_shutdown_timer, write_start_gridinterrupt_timer,
                       read_start_shutdown_timer, read_start_gridinterrupt_timer, shutdown_timer, gridinterrupt_timer,
                       write_ionhub_state, read_ionhub_state, read_full_charge, write_full_charge, write_off_time,
                       read_off_time, write_soc_offset, write_old_energy,write_voltage,read_voltage, read_old_energy, read_soc_offset)
from pinlayout import GRID_INTERRUPT_BUTTON

logger = logging.getLogger(__name__)


# from main program, we have two variables before loop
#   start_shutdown_timer = 0
#   stop_shutdown_timer = 0
#   grid_interrupt_timer = 0


class GridButton:
    def __init__(self, energy, voltage, fully_charge_latch):
        try:
            import RPi.GPIO
            self.GPIO = RPi.GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setup(GRID_INTERRUPT_BUTTON, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
            self.energy = energy
            self.voltage = voltage
            self.fully_charge_latch = fully_charge_latch

        except Exception as e:
            logger.error(e)

    def setgridinterrupt(self):
        try:
            led_push_button = self.GPIO.input(GRID_INTERRUPT_BUTTON)
            standby = None

            if int(read_ionhub_state()) == 2:
                shutdown_trigger = False

                if led_push_button == 1:
                    button_status = False
                    if float(read_start_shutdown_timer()) != 0:
                        write_start_shutdown_timer(0)

                    if float(read_start_gridinterrupt_timer()) == 0:
                        grid_interrupt = False
                    else:
                        if gridinterrupt_timer() > 25:
                            write_start_gridinterrupt_timer(0)
                            grid_interrupt = False
                        else:
                            grid_interrupt = True

                else:
                    button_status = True
                    grid_interrupt = True
                    if float(read_start_shutdown_timer()) == 0:
                        write_start_shutdown_timer(time.time()-2)
                    else:
                        if shutdown_timer() > 0.4:
                            write_off_time(time.time())
                            write_old_energy(self.energy)
                            write_voltage(self.voltage)
                            write_ionhub_state(3)
                            standby = 3

                if self.fully_charge_latch and self.voltage > 100:
                    write_start_gridinterrupt_timer(time.time())
                    write_start_shutdown_timer(time.time())
                    write_voltage(self.voltage)
                    grid_interrupt = True
                    write_ionhub_state(3)
                    write_full_charge(1)
                    standby = 3

            # IONHUB_STATE =3
            elif int(read_ionhub_state()) == 3:
                standby = 3
                if led_push_button == 1:
                    button_status = False
                    shutdown_trigger = False
                    grid_interrupt = True

                    if (float(read_off_time())) > 3600:
                        real_soc = float(read_old_energy()) - 0.06
                        energy_offset = real_soc - self.energy
                        total_offset = float(read_soc_offset()) + energy_offset
                        write_soc_offset(total_offset)
                        write_off_time(time.time())
                        write_old_energy(self.energy)
                    
                    if int(read_voltage())> 100 and self.voltage > 100:
                        pass
                    else:
                        write_voltage(0)
                        
                    if (int(read_full_charge()) == 0 and self.voltage > 100 and int(read_voltage())==0):
                        print('going to 2')
                        write_ionhub_state(2)
                        time.sleep(1)
                        write_start_shutdown_timer(0)
                        write_start_gridinterrupt_timer(0)


                    elif ((gridinterrupt_timer() > 6) and float(read_start_gridinterrupt_timer())!= 0) or (int(read_full_charge()) == 1 and self.energy < 95 and self.voltage > 100):
                        print('going to 2')
                        print(gridinterrupt_timer())
                        print((int(read_full_charge()) == 1 and self.energy < 95 and self.voltage > 100))
                        write_ionhub_state(2)
                        write_full_charge(0)
                        write_start_shutdown_timer(0)
                        write_start_gridinterrupt_timer(0)

                    else:
                        standby = 3
                        # here button is released,now check grid_interrupt timer >5, then go to ionhubstate =2
                        write_start_shutdown_timer(time.time())
                        write_start_gridinterrupt_timer(time.time())

                else:  # BUTTON PRESSED
                    button_status = True
                    print('ion 3 button pressed')
                    grid_interrupt = True
                    if shutdown_timer() > 20:
                        standby = 5
                        shutdown_trigger = True
                    elif shutdown_timer() > 0.5:
                        write_start_gridinterrupt_timer(time.time())
                        standby = 3
                        shutdown_trigger = False

                    else:
                        if float(read_start_gridinterrupt_timer()) == 0:
                            shutdown_trigger = False
                            standby = 3

                        elif gridinterrupt_timer() > 20:  # and check grid_interrupt timer>18, go to shutdown mode
                            standby = 5
                            shutdown_trigger = True
                        elif gridinterrupt_timer() > 2:  # and check grid_interrupt timer>18, go to shutdown mode
                            write_start_shutdown_timer(time.time())
                            shutdown_trigger = False
                            standby = 9

                        elif gridinterrupt_timer() > 0.1:  # and check grid_interrupt timer>18, go to shutdown mode
                            # write_ionhub_state(2)
                            write_start_gridinterrupt_timer(time.time()-6)
                            write_start_shutdown_timer(time.time())
                            shutdown_trigger = False
                            standby = 9
                        else:
                            write_start_shutdown_timer(time.time())
                            standby = 3
                            shutdown_trigger = False
            # IONHUB STATE =4
            else:
                if led_push_button == 1:
                    button_status = False
                    write_start_shutdown_timer(time.time())
                    write_start_gridinterrupt_timer(time.time())
                    grid_interrupt = False
                    shutdown_trigger = False
                    standby = None
                    write_ionhub_state(2)

                else:
                    button_status = True
                    if shutdown_timer() > 20:
                        standby = 5
                        shutdown_trigger = True
                        grid_interrupt = True
                    else:
                        grid_interrupt = False
                        shutdown_trigger = False
                        standby = None

            return grid_interrupt, shutdown_trigger, standby,button_status

        except Exception as e:
            logger.error(e)

