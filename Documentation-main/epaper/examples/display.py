import sys
import os
import traceback
import time
from PIL import Image, ImageDraw, ImageFont
import math
import logging

logger = logging.getLogger(__name__)
class Epaper:

    def display(self, energy, power, charge_power, value, phase_power):
        try:
            picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pics')
            libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')

            if os.path.exists(libdir):
                sys.path.append(libdir)

            from waveshare_epd import epd3in7
            epd = epd3in7.EPD()
            energydir = os.path.join(picdir, 'energy')
            powerdir = os.path.join(picdir, 'power')
            energyflowdir = os.path.join(picdir, 'energyflow')
            phasepowerdir = os.path.join(picdir, 'phasepower')

            logging.basicConfig(level=logging.DEBUG)

            epd.init(0)
            epd.Clear(0xFF, 0)  # FULL REFRESH

            new_image = Image.new('1', (epd.width, epd.height), 255)

            if value == 4 and energy < 10:
                if energy < 0:
                    energy_value = Image.open(os.path.join(energydir, f'Energy_less10_0.png'))
                else:
                    energy_value = Image.open(os.path.join(energydir, f'Energy_less10_{energy}.png'))

            else:
                if energy <= 0:
                    energy_value = Image.open(os.path.join(energydir, f'Energy_0.png'))
                else:
                    energy_value = Image.open(os.path.join(energydir, f'Energy_{math.ceil(energy)}.png'))

            new_image.paste(energy_value, (0, 0))

            if value != 4:
                if charge_power >= 100:
                    power_value = Image.open(os.path.join(powerdir, 'Power_100.png'))
                elif charge_power <= 0:
                    power_value = Image.open(os.path.join(powerdir, 'Power_0.png'))
                else:
                    power_value = Image.open(os.path.join(powerdir, f'Power_{round(charge_power)}.png'))

                if value == 2:
                    bmp = Image.open(os.path.join(energyflowdir, 'Energyflow_IN.png'))
                elif value == 3:
                    bmp = Image.open(os.path.join(energyflowdir, 'Energyflow_IN_charge_only.png'))
                elif value == 5:
                    bmp = Image.open(os.path.join(energyflowdir, 'Energyflow_charge_only.png'))
                elif value == 6:
                    bmp = Image.open(os.path.join(energyflowdir, 'Energyflow_IN_nocharge.png'))
                else:
                    bmp = Image.open(os.path.join(energyflowdir, 'Energyflow_OUT.png'))

                new_image.paste(power_value, (0, 289))
                new_image.paste(bmp, (0, 373))
                power_value.close()
                bmp.close()

            else:

                if power < 5:
                    power_value = Image.open(os.path.join(powerdir, 'Power_0.png'))
                elif power >= 200:
                    power_value = Image.open(os.path.join(powerdir, 'Power_200.png'))
                else:
                    power_value = Image.open(os.path.join(powerdir, f'Power_{power}.png'))

                phase_power = [-1 if value < 1 else 16 if value >= 16 else round(value) for value in phase_power]

                phase1 = Image.open(os.path.join(phasepowerdir, f'{phase_power[0]}A.png'))
                phase2 = Image.open(os.path.join(phasepowerdir, f'{phase_power[1]}A.png'))
                phase3 = Image.open(os.path.join(phasepowerdir, f'{phase_power[2]}A.png'))
                l1 = Image.open(os.path.join(phasepowerdir, 'L1.png'))
                l2 = Image.open(os.path.join(phasepowerdir, 'L2.png'))
                l3 = Image.open(os.path.join(phasepowerdir, 'L3.png'))

                new_image.paste(power_value, (0, 289))
                new_image.paste(l1, (0, 373))
                new_image.paste(phase1, (25, 373))
                new_image.paste(l2, (96, 373))
                new_image.paste(phase2, (120, 373))
                new_image.paste(l3, (191, 373))
                new_image.paste(phase3, (215, 373))
                power_value.close()
                l1.close()
                l2.close()
                l3.close()
                phase1.close()
                phase2.close()
                phase3.close()

            time.sleep(0.5)
            epd.display_1Gray(epd.getbuffer(new_image))
            energy_value.close()
            epd.sleep()

        except IOError as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)

    def error_display(self, soc, error_value, error = None):

        """
        starting = 2,
        status_off =3,
        overload=4,
        status_shutdown =5,
        status_cold=6,
        status_hot = 7,
        status_error=8
        status = 9 coming from standby display to normal display
        status = 10  status_highload warning message
        status = 11  status_warm warning message
        status = 12  status_singlephase
        status = 13  status_threephase
        status = 14  status_isolation error"""

        try:
            if error_value is None:
                pass
            else:
                picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pics')
                libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')

                if os.path.exists(libdir):
                    sys.path.append(libdir)

                from waveshare_epd import epd3in7
                epd = epd3in7.EPD()
                logger.info(f'displaying {soc} {error_value} {error}')
                statusdir = os.path.join(picdir, 'status')
                socdir = os.path.join(picdir, 'soc')

                logging.basicConfig(level=logging.DEBUG)

                epd.init(0)  # 1 Gary mode
                epd.Clear(0xFF, 0)

                new_image = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
                if soc <= 0:
                    soc = 0
                soc_value = Image.open(os.path.join(socdir, f'SoC_{soc}.png'))
                new_image.paste(soc_value, (0, 0))

                if error_value == 3:
                    img = Image.open(os.path.join(statusdir, f'status_off.png'))
                    error = None
                elif error_value == 4:
                    img = Image.open(os.path.join(statusdir, f'status_overload.png'))
                elif error_value == 5:
                    img = Image.open(os.path.join(statusdir, f'status_shutdown.png'))
                elif error_value == 6:
                    img = Image.open(os.path.join(statusdir, f'status_cold.png'))
                elif error_value == 7:
                    img = Image.open(os.path.join(statusdir, f'status_hot.png'))
                elif error_value == 8:
                    img = Image.open(os.path.join(statusdir, f'status_error.png'))
                elif error_value == 10:
                    img = Image.open(os.path.join(statusdir, f'status_highload.png'))
                elif error_value == 11:
                    img = Image.open(os.path.join(statusdir, f'status_warm.png'))
                elif error_value == 12:
                    img = Image.open(os.path.join(statusdir, f'status_singlephase.png'))
                elif error_value == 13:
                    img = Image.open(os.path.join(statusdir, f'status_threephase.png'))
                elif error_value == 14:
                    img = Image.open(os.path.join(statusdir, f'status_isolation.png'))
                else:
                    pass

                new_image.paste(img, (0, 31))
                if error is not None:
                    if error[0] == 3:
                        error_img = Image.open(os.path.join(statusdir, f'status_battery.png'))
                        new_image.paste(error_img, (0, 449))
                        error_img = ''
                        if error[1] is not None:
                            for error in error[1]:
                                error_img = error_img + f'{error} '

                        font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
                        draw = ImageDraw.Draw(new_image)
                        draw.text((105, 450), error_img, font=font18, fill=0)
                    elif error[0] == 2:
                        error_img = Image.open(os.path.join(statusdir, f'status_inverter.png'))
                        new_image.paste(error_img, (0, 449))
                        if error[1] is not None:
                            font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
                            draw = ImageDraw.Draw(new_image)
                            draw.text((105, 450), error[1], font=font18, fill=0) 
                        
                    else:
                        pass
                soc_value.close()
                img.close()
                time.sleep(0.5)
                epd.display_1Gray(epd.getbuffer(new_image))
                epd.sleep()

        except IOError as e:
            logger.error(e)

        except Exception as e:
            print(e)
            logger.error(e)

    def start_display(self):
        try:
            picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pics')
            libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')

            if os.path.exists(libdir):
                sys.path.append(libdir)

            from waveshare_epd import epd3in7
            epd = epd3in7.EPD()

            statusdir = os.path.join(picdir, 'status')

            epd.init(0)  # 1 Gary mode
            epd.Clear(0xFF, 0)
            new_image = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
            start_img = Image.open(os.path.join(statusdir, 'status_starting.png'))
            new_image.paste(start_img, (0, 45))
            time.sleep(0.5)
            start_img.close()
            epd.display_1Gray(epd.getbuffer(new_image))
            epd.sleep()
        except Exception as e:
            logger.error(e)

