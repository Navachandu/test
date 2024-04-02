"""this is updated code of display"""
import os
import time

def write_start_shutdown_timer(value):
    with open('start_shutdown_timer.txt', 'w') as f:
        f.write(f'{value}')
        f.close()


def read_start_shutdown_timer():
    with open('start_shutdown_timer.txt', 'r') as f:
        contents = f.read()
        f.close()
    return contents


def write_start_gridinterrupt_timer(value):
    with open('start_gridinterrupt_timer.txt', 'w') as f:
        f.write(f'{value}')
        f.close()


def read_start_gridinterrupt_timer():
    with open('start_gridinterrupt_timer.txt', 'r') as f:
        contents = f.read()
        f.close()
    return contents


def shutdown_timer():
    import time
    timer_value = time.time() - float(read_start_shutdown_timer())
    return timer_value


def gridinterrupt_timer():
    import time
    timer_value = time.time() - float(read_start_gridinterrupt_timer())
    return timer_value


def write_inverter_switch_state(value):
    with open('inverter_switch_state.txt', 'w') as f:
        f.write(f'{value}')
        f.close()


def read_inverter_switch_state():
    with open('inverter_switch_state.txt', 'r') as f:
        contents = f.read()
        f.close()
    return contents


def write_soc_stop_inverter(value):
    with open('soc_stop_inverter.txt', 'w') as f:
        f.write(f'{value}')
        f.close()


def read_soc_stop_inverter():
    with open('soc_stop_inverter.txt', 'r') as f:
        contents = f.read()
        f.close()
    return contents


def write_ionhub_state(value):
    with open('ionhub_state.txt', 'w') as f:
        f.write(f'{value}')
        f.close()


def read_ionhub_state():
    with open('ionhub_state.txt', 'r') as f:
        contents = f.read()
        f.close()
    return contents


def write_battery_empty(value):
    with open('battery_empty.txt', 'w') as f:
        f.write(f'{value}')
        f.close()


def read_battery_empty():
    with open('battery_empty.txt', 'r') as f:
        contents = f.read()
        f.close()
    return contents


def write_soc_offset(value):
    with open('soc_offset.txt', 'w') as f:
        f.write(f'{value}')
        f.close()


def read_soc_offset():
    with open('soc_offset.txt', 'r') as f:
        contents = f.read()
        f.close()
    return contents


def write_off_time(value):
    with open('off_time.txt', 'w') as f:
        f.write(f'{value}')
        f.close()


def read_off_time():
    with open('off_time.txt', 'r') as f:
        contents = f.read()
        difference = float(time.time() - float(contents))
        f.close()
    return difference

def write_old_energy(value):
    with open('old_energy.txt', 'w') as f:
        f.write(f'{value}')
        f.close()


def read_old_energy():
    with open('old_energy.txt', 'r') as f:
        contents = f.read()
        f.close()
    return contents

def write_full_charge(value):
    with open('full_charge.txt', 'w') as f:
        f.write(f'{value}')
        f.close()


def read_full_charge():
    with open('full_charge.txt', 'r') as f:
        contents = f.read()
        f.close()
    return contents

def write_voltage(value):
    with open('voltage.txt', 'w') as f:
        f.write(f'{value}')
        f.close()


def read_voltage():
    with open('voltage.txt', 'r') as f:
        contents = f.read()
        f.close()
    return contents