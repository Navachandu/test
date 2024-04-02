
import logging
logger = logging.getLogger(__name__)
# ======================= SERIAL COMMUNICATION OPERATIONS===============

# --------------- Writing the output-------------------------
import serial
ser = serial.Serial('/dev/ttyUSB0', baudrate=2400, timeout=0.5, bytesize=8, stopbits=serial.STOPBITS_ONE)

def serial_write(comm_arr1: list) -> None:

    """serial_write is for sending hex commands to the multiplus"""
    ser.reset_output_buffer()
    ser.flushOutput()
    ser.write(serial.to_bytes(comm_arr1))

# ----------------Reading the Input--------------------------


def serial_read(number_of_bytes:int):
    """serial_read is to read byte array from multiplus """
    ser.reset_input_buffer()
    ser.flushInput()  # after reading flush the input
    received_array = ser.read(number_of_bytes).hex()
    return received_array


# ============== Converting arrays into values for GetInfo ==============

# --------------------AC Array -----------------------------------------------
def acarray(bytearr:str):
    arr = [bytearr[i:i + 2] for i in range(0, len(bytearr), 2)]

    # ----------- AC FRAME---------------------

    # ---------- BF FACTOR ---------

    bf_factor = arr[2]

    # ------------INVERTER FACTOR-------

    inverter_factor = arr[3]

    # --------- STATE -------------

    state = arr[5]

    # ------PHASE INFO ----------

    phase_info = arr[6]
    # ----------MAINS Voltage------------
    mainsvoltage_array = arr[8] + arr[7]
    mains_voltage = int(mainsvoltage_array, 16) / 100

    # ----------MAINS Current------------
    mainscurrent_array = arr[10] + arr[9]
    mains_current = int(mainscurrent_array, 16) / 100

    # ----------INVERTERS Voltage------------
    invertervoltage_array = arr[12] + arr[11]
    inverter_voltage = int(invertervoltage_array, 16) / 100

    # ----------INVERTERS Current------------
    invertercurrent_array = arr[14] + arr[13]
    inverter_current = int(invertercurrent_array, 16) / 100
    if inverter_current > 300:
        inverter_current = 0

    # ---------------MAINS PERIOD ----------
    mains_period_array = arr[15]
    mains_period = int(mains_period_array, 16)
    # ----------------Check sum----------

    checksum_acframe = arr[16]

    inverter_power = inverter_voltage * inverter_current
    inverter_value = [mains_voltage, mains_current, inverter_voltage, inverter_current]

    return inverter_power, mains_voltage, inverter_value


#  --------------------  DC Array ---------------------------------------
def dcarray(bytearr:str):


    arr = [bytearr[i:i + 2] for i in range(0, len(bytearr), 2)]
    # ---------DC FRAME------------------------------------------

    # -----Phase Info--------------

    phase_info = arr[6]

    # ----------DC Voltage------------
    dcvoltage_array = arr[8] + arr[7]
    dc_voltage = int(dcvoltage_array, 16) / 100


    # --------DC Current Inverting-------------
    dccurrent_array_inverting = arr[11] + arr[10] + arr[9]
    dccurrentwith10_inverting = int(dccurrent_array_inverting, 16)
    dccurrent_inverting = dccurrentwith10_inverting / 10


    # -------DC Current Charging--------------------
    dccurrent_array_charging = arr[14] + arr[13] + arr[12]
    dccurrentwith10_charging = int(dccurrent_array_charging, 16)
    dccurrent_charging = dccurrentwith10_charging / 10

    # -------------Inverter Period----------
    inverter_period = int(arr[15], 16)
    # ---------------Check Sum--------
    checksum_dcframe = arr[16]
    return dc_voltage, dccurrent_inverting, dccurrent_charging


# ================================CHECK SUM =======================

# --------------------Calculation of Checksum
def checksum(comm_arr: list) -> str:
    number = sum(int(num, 16) for num in comm_arr)
    twocompli = (256 - (number % 256)) % 256
    return "{:02x}".format(twocompli)

# ========================== Twos Compliment =============================

def twoscomplement(value: str) -> str:
    """It takes the 8-bit hex value, value should given in string format
        input:  hex in string format
        returns: 2 bit hex value
    """
    twocompli = (256 - int(value, 16)) % 256
    return "{:02x}".format(twocompli)

# ========================== CAN PROTOCOL ===========================

def can_array_conversion(receiveddata:bytearray, lsb:int, msb:int):
    receiveddata_hex = receiveddata.hex()
    receiveddata_array = [receiveddata_hex[i:i + 2] for i in range(0, len(receiveddata_hex), 2)]

    value_str = ''
    for i in range(msb, lsb - 1, -1):
        value_str = value_str + receiveddata_array[i]
    num = bin(int(value_str, 16))[2:].zfill(16)
    value = int(value_str, 16)
    return value


def can_array_conversion_error(receiveddata:bytearray, lsb:int, msb:int):
    """takes the bytearray with lsb and msb(according to onenote) and return decimal value of  the particular byte
         it follows big endian format
         """
    receiveddata_hex = receiveddata.hex()
    receiveddata_array = [receiveddata_hex[i:i + 2] for i in range(0, len(receiveddata_hex), 2)]

    if msb is None:
        value = int(receiveddata_array[lsb], 16)
        binary_number = '0b{:08b}'.format(value)
        if binary_number[2] == '1':
            value_hex = twoscomplement(receiveddata_array[lsb])
            value = int(value_hex, 16)*-1

    else:
        receivedarray_msb = int(receiveddata_array[msb], 16)
        binary_number = '0b{:08b}'.format(receivedarray_msb)
        if binary_number[2] == '1':
            value_str = ''
            for i in range(msb, lsb - 1, -1):
                value_str = value_str + receiveddata_array[i]
            value_hex = twoscomplement(value_str)
            value = int(value_hex, 16)*-1
        else:
            value_str = ''
            for i in range(len(receiveddata_array)-msb-1, len(receiveddata_array)-lsb):
                value_str = value_str+receiveddata_array[i]
                value = int(value_str, 16)
    return value


def canarray_conv_curr(receiveddata:bytearray, lsb:int, msb:int, no_bits:int):
    receiveddata_hex = receiveddata.hex()
    receiveddata_array = [receiveddata_hex[i:i + 2] for i in range(0, len(receiveddata_hex), 2)]
    value_str = ''
    for i in range(msb, lsb - 1, -1):
        value_str = value_str + receiveddata_array[i]
    num = bin(int(value_str, 16))[2:].zfill(no_bits)
    if num[0] == '1':
        inverted = ''
        for bit in num:
            if bit == '0':
                inverted += '1'
            else:
                inverted += '0'

        int_inverted = int(inverted, 2)
        if no_bits == 32:
            s = int_inverted + 1
            if s > 4294967295:
                s = s - 4294967296
        elif no_bits == 16:
            s = int_inverted + 1
            if s > 65535:
                s = s - 65536
        else:
            s = int_inverted + 1
            if s > 255:
                s = s - 256

        bin_invertered = bin(s)
        s = bin_invertered[2:].zfill(no_bits)
        value = int(s, 2) * -1
    else:
        value = int(value_str, 16)

    return value
# =============== LED STATUS ================================

def led_conversion(byte:str):
    lsb = byte[0]
    msb = byte[1]
    bi_lsb = bin(int(lsb, 16))[2:].zfill(4)
    bi_msb = bin(int(msb, 16))[2:].zfill(4)
    lsb_frame = bi_lsb[::-1]
    msb_frame = bi_msb[::-1]
    byte = msb_frame + lsb_frame
    return byte

# ===================== LED Status ===============================

def led_status(blue, green):
    try:
        import RPi.GPIO as GPIO
        from pinlayout import BLUE_LED_PIN
        from pinlayout import GREEN_LED_PIN
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BLUE_LED_PIN, GPIO.OUT)
        GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
        GPIO.output(BLUE_LED_PIN, blue)
        GPIO.output(GREEN_LED_PIN, green)
    except Exception as e:
        logger.error(e)
