# Raspberry pi 5 version 2
# Support for different screen sizes
# Shift light uses Adafruit_Blinka_Raspberry_Pi5_Neopixel lirary

import pygame
import time
import struct

# PC test mode
TEST_MODE = True

# Screen size
SIZE = WIDTH, HEIGHT = (1280, 720)
pygame.display.init()
pygame.font.init()

if TEST_MODE is False:
    import os
    import can
    import mcp3002
    import psutil
    import shift_light_rpi5
    shift_light_rpi5
    from rpi_hardware_pwm import HardwarePWM
    psutil.cpu_percent()
    screen = pygame.display.set_mode(SIZE)
    pygame.mouse.set_visible(False)
    PATH = "/home/your_user_name/Dash/"
    # Can bus
    os.system('sudo ip link set can0 type can bitrate 500000')
    os.system('sudo ifconfig can0 up')
    can_bus_filter = [{"can_id": 0x607, "can_mask": 0x5F8 , "extended": False}]
    can_bus = can.Bus(channel="can0", interface="socketcan", can_filters=can_bus_filter)
    # Pwm
    backlight = HardwarePWM(pwm_channel=2, hz=500, chip=2)
    backlight.start(70)
else:
    screen = pygame.display.set_mode(SIZE)
    PATH = "/home/your_user_name/Dash/"

# Read needed files
units_memory = open(PATH + "units_memory.txt", "r")
units = units_memory.read().splitlines()
units_memory.close()
odometer_memory = open(PATH + "odometer_memory.txt", "r")
odometer = float(odometer_memory.readline())
odometer_memory.close()

# Variables
start_up = True
timeout_counter = 0
rpm = 0
speed = 0
gear = 0
out_temp = 0
fuel_level = None
fuel_used = 0
raw_fuel_level = 0
refuel = False
batt_v = 0
left_blinker = False
right_blinker = False
high_beam = False
errors = 0
speed_sum = 0
speed_sum_counter = 0
old_rpm = None
old_gear = None
old_speed = None
old_out_temp = None
old_odometer = odometer
old_clock = None
old_error_list = None
old_refuel = None
old_right_blinker = None
old_left_blinker = None
old_high_beam = None
values = {x : 0 for x in units}
old_values = {x : None for x in units}
odometer_start = odometer
clear = True
loop = True
touch = False
start = True
filter_counter = 0
filter_sum = 0
countdown = 10
unit_change = None
units_ok = True
draw_menu = False
old_cpu_temp = None
shift_changed = 10
shift_light_off = False
power_off = False
cpu_timer = time.monotonic()
blink_timer = time.monotonic()
dimmer_timer_1 = time.monotonic()
dimmer_timer_4 = time.monotonic()
distance_timer = time.monotonic()

test_message_order = 0

# Needed for cordinates
def calc(whole, percentage):
    return int(whole / 100 * percentage)

# CONSTANTS
ECU_CAN_ID = 0x600
FUEL_MAX = 197
FUEL_MIN = 36
FUEL_DIVIDER = (FUEL_MAX - FUEL_MIN) / 100
CENTER_X, CENTER_Y = (WIDTH / 2, HEIGHT / 2)
RED = (155, 0, 0)
WHITE = (255, 255, 255)
DARK_BLUE = (0, 64, 128)
LIGHT_BLUE = (0, 128, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
# Shift light
END = 8600
STEP = 300
# Rectangle sizes and cordinates
RPM_HEIGHT = calc(HEIGHT, 16)
BOTTOM_BAR_HEIGHT = calc(HEIGHT, 8)
BOTTOM_BAR = (0, HEIGHT - BOTTOM_BAR_HEIGHT, WIDTH, BOTTOM_BAR_HEIGHT)
BOX_WIDTH = calc(WIDTH, 23)
BOX_HEIGHT = calc(HEIGHT, 21)
SPACING = int((HEIGHT - (RPM_HEIGHT + BOTTOM_BAR_HEIGHT + BOX_HEIGHT * 3)) / 4)
TOP_LEFT = (0, RPM_HEIGHT + SPACING, BOX_WIDTH, BOX_HEIGHT)
CENTER_LEFT = (0, TOP_LEFT[1] + SPACING + BOX_HEIGHT, BOX_WIDTH, BOX_HEIGHT)
BOTTOM_LEFT = (0, CENTER_LEFT[1] + SPACING + BOX_HEIGHT, BOX_WIDTH, BOX_HEIGHT)
TOP_RIGHT = (WIDTH - BOX_WIDTH, TOP_LEFT[1], BOX_WIDTH, BOX_HEIGHT)
CENTER_RIGHT = (WIDTH - BOX_WIDTH, CENTER_LEFT[1], BOX_WIDTH, BOX_HEIGHT)
BOTTOM_RIGHT = (WIDTH - BOX_WIDTH, BOTTOM_LEFT[1], BOX_WIDTH, BOX_HEIGHT)
BOX_TEXT_X = calc(BOX_WIDTH, 5)
UNIT_TEXT_Y = calc(BOX_HEIGHT, 5)
VALUE_TEXT_Y = calc(BOX_HEIGHT, 28)
CENTER_TOP = (CENTER_X - calc(HEIGHT, 8), TOP_LEFT[1], calc(HEIGHT, 16), calc(HEIGHT, 16))
CENTER = (CENTER_X - calc(WIDTH, 14), calc(HEIGHT, 38), calc(WIDTH, 28), calc(HEIGHT, 31))
CENTER_BOTTOM = (CENTER[0], calc(HEIGHT, 71), CENTER[2], calc(HEIGHT, 17.5))
MENU_RECT = (calc(WIDTH, 24), calc(HEIGHT, 15))
MENU_SPACING = (int((WIDTH - MENU_RECT[0] * 4) / 5), int((HEIGHT - MENU_RECT[1] * 6) / 7))
MENU_TEXT_XY = (calc(WIDTH, 2), calc(HEIGHT, 5))

# Close io devices
def close_io():
    mcp3002.close()
    can_bus.shutdown()
    os.system('sudo ifconfig can0 down')
    backlight.stop()

# Touchscreen coordinate return
def touch_xy(x, y):
    return (int(x * WIDTH), int(y * HEIGHT))

# Odometer calculations and file save
def odometer_save(speed_sum, speed_sum_counter, distance_timer, odometer, PATH):
    if speed_sum == 0:
        return odometer
    average_speed = (speed_sum / speed_sum_counter) * 0.27777778
    timer = time.monotonic() - distance_timer
    distance = (average_speed * timer) / 1000
    odometer = odometer + distance
    # Saving to memory
    odometer_memory = open(PATH + "odometer_memory.txt", "w")
    odometer_memory.write(str(odometer))
    odometer_memory.close()
    return odometer

def menu(pos):
    if pygame.Rect.collidepoint(rpm_button, pos):
        return "rpm"
    elif pygame.Rect.collidepoint(tps_button, pos):
        return "tps"
    elif pygame.Rect.collidepoint(iat_button, pos):
        return "iat"
    elif pygame.Rect.collidepoint(map_button, pos):
        return "map"
    elif pygame.Rect.collidepoint(inj_pw_button, pos):
        return "inj_pw"
    elif pygame.Rect.collidepoint(oil_t_button, pos):
        return "oil_t"
    elif pygame.Rect.collidepoint(oil_p_button, pos):
        return "oil_p"
    elif pygame.Rect.collidepoint(fuel_p_button, pos):
        return "fuel_p"
    elif pygame.Rect.collidepoint(clt_t_button, pos):
        return "clt_t"
    elif pygame.Rect.collidepoint(ign_ang_button, pos):
        return "ign_ang"
    elif pygame.Rect.collidepoint(dwell_button, pos):
        return "dwell"
    elif pygame.Rect.collidepoint(lambda_button, pos):
        return "lambda"
    elif pygame.Rect.collidepoint(lambda_corr_button, pos):
        return "lambda_corr"
    elif pygame.Rect.collidepoint(egt_1_button, pos):
        return "egt_1"
    elif pygame.Rect.collidepoint(egt_2_button, pos):
        return "egt_2"
    elif pygame.Rect.collidepoint(ethanol_cont_button, pos):
        return "ethanol_cont"
    elif pygame.Rect.collidepoint(batt_v_button, pos):
        return "batt_v"
    elif pygame.Rect.collidepoint(dbw_pos_button, pos):
        return "dbw_pos"
    elif pygame.Rect.collidepoint(boost_t_button, pos):
        return "boost_t"
    elif pygame.Rect.collidepoint(dsg_mode_button, pos):
        return "dsg_mode"
    elif pygame.Rect.collidepoint(lambda_t_button, pos):
        return "lambda_t"
    elif pygame.Rect.collidepoint(fuel_used_button, pos):
        return "fuel_used"
    elif pygame.Rect.collidepoint(fuel_level_button, pos):
        return "fuel_level"
    elif pygame.Rect.collidepoint(fuel_consumption_button, pos):
        return "fuel_consum"

# Read light sensor value
def is_dark(old_value):
    a_val = mcp3002.read_adc(0)
    # print(a_val)
    if a_val < 150:
        return True
    elif a_val > 250:
        return False
    else:
        return old_value

# Dimmer
def dimmer(value):
    global led_br
    # Dark
    if value is True:
        backlight.change_duty_cycle(70)
        led_br = 10
    # Bright
    else:
        backlight.change_duty_cycle(0)
        led_br = 80


if TEST_MODE is False:
    old_dark = is_dark(True)
    dimmer(old_dark)

# Return CPU temperature as a character string
def getCPUtemperature():
    temp = os.popen('vcgencmd measure_temp').readline()
    temp = temp.replace("temp=", "")
    return temp.replace("'C\n", "°C")

def error_flags(number):
    # Convert to bit list
    bit_list = [True if x == "1" else False for x in "{:016b}".format(number)]
    # Get the errors that are on
    errors_on = []
    for x in range(len(bit_list)):
        if bit_list[x]:
            errors_on.append(ERRORFLAGS[x])
    return errors_on

# Reading 3 bit bitfield from Can extension board (message 0x610)
def bitfield_3_return(number):
    # Convert to bit list
    bit_list = [True if x == "1" else False for x in "{:03b}".format(number)]
    return bit_list

# Emu Black error flags
ERRORFLAGS = ("", "OILP", "EWG", "DSG", "DIFFCTRL", "FPR", "DBW", "FF_SENSOR",
              "KNOCKING", "EGT_ALARM", "EGT2", "EGT1", "WBO", "MAP", "IAT", "CLT")

title_text_units = {"rpm": "RPM", "tps": "TPS                 %",
                    "iat": "IAT                 °C", "map": "MAP              kPa",
                    "inj_pw": "Inj pw.           ms", "oil_t": "Oil temp.       °C",
                    "oil_p": "Oil press.      bar", "fuel_p": "Fuel press.    bar",
                    "clt_t": "Clt temp.       °C", "ign_ang": "Ign angle  °btdc",
                    "dwell": "Dwell time    ms", "lambda": "Lambda",
                    "lambda_corr": "Lambda corr.  %", "egt_1": "EGT 1             °C",
                    "egt_2": "EGT 2             °C", "batt_v": "Battery  voltage",
                    "ethanol_cont": "Ethanol           %", "dbw_pos": "Dbw position  %",
                    "boost_t": "Boost target  kPa", "dsg_mode": "DSG mode",
                    "lambda_t": "Lambda target", "fuel_used": "Fuel used         L",
                    "fuel_level": "Fuel level        %", "fuel_consum": "Fuel c.  L/100km"}

dsg_mode_return = {0: "0", 2: "P", 3: "R", 4: "N", 5: "D", 6: "S", 7: "M", 15: "Fault"}

FONT_1 = pygame.font.SysFont("dejavusans", calc(HEIGHT, 4.3))
FONT_2 = pygame.font.SysFont("dejavusans", calc(HEIGHT, 6))
FONT_3 = pygame.font.SysFont("dejavusans", calc(HEIGHT, 13))
FONT_4 = pygame.font.SysFont("dejavusans", calc(HEIGHT, 17))

# Text box sizes
DIGITS_2 = [FONT_2.size("0"), FONT_2.size("00"), FONT_2.size("000")]
KMH_2 = FONT_2.size("km/h")
ONE_DIGIT_3 = FONT_3.size("0")
ONE_LETTER_3 = FONT_3.size("N")
DIGITS_4 = [FONT_4.size("0"), FONT_4.size("00"), FONT_4.size("000")]

# Renders
CELSIUS_20 = FONT_1.render("°C", True, WHITE, BLACK)
KMH_TEXT = FONT_2.render("km/h", True, WHITE, BLACK)
NO_CAN_BUS_R = FONT_1.render("No Can Bus communication", True, WHITE, BLACK)
# RPM bar numbers
rpm_list = [FONT_3.render(str(x), True, WHITE) for x in range(1, 10)]

image0 = pygame.image.load(PATH + "High_beam_blue.png")
image1 = pygame.image.load(PATH + "High_beam_black.png")
image2 = pygame.image.load(PATH + "Fuel_pump_yellow.png")
image3 = pygame.image.load(PATH + "Fuel_pump_black.png")

IMAGE_SIZE = (int(WIDTH / 1920 * 120), int(WIDTH / 1920 * 120))
HIGH_BEAM_BLUE = pygame.transform.smoothscale(image0, IMAGE_SIZE)
HIGH_BEAM_BLACK = pygame.transform.smoothscale(image1, IMAGE_SIZE)
FUEL_PUMP_YELLOW = pygame.transform.smoothscale(image2, IMAGE_SIZE)
FUEL_PUMP_BLACK = pygame.transform.smoothscale(image3, IMAGE_SIZE)
# X, Y, SIZE
HIGH_BEAM = (calc(WIDTH, 30) - IMAGE_SIZE[0] / 2, CENTER_BOTTOM[1], IMAGE_SIZE[0], IMAGE_SIZE[1])
FUEL_PUMP = (calc(WIDTH, 70) - IMAGE_SIZE[0] / 2, CENTER_BOTTOM[1], IMAGE_SIZE[0], IMAGE_SIZE[1])

unit_buttons = [pygame.Rect(TOP_LEFT), pygame.Rect(CENTER_LEFT), pygame.Rect(BOTTOM_LEFT),
                pygame.Rect(TOP_RIGHT), pygame.Rect(CENTER_RIGHT), pygame.Rect(BOTTOM_RIGHT)]

# Creating title texts
units_r = []
for x in range(6):
    units_r.append(FONT_1.render(title_text_units[units[x]], True, WHITE, BLACK))

while loop:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            loop = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            touch = True
            pos = event.pos
        elif event.type == pygame.FINGERUP:
            touch = True
            pos = touch_xy(event.x, event.y)

    if TEST_MODE is False:
        # Read can bus message
        message = can_bus.recv(timeout=1)
        # Shutdown if there is no Can Bus communication
        if message is None:
            clear = True
            countdown -= 1
            SHUTDOWN_RECT = (calc(WIDTH, 38), calc(HEIGHT, 30))
            SHUTDOWN_RECT_XY = (CENTER_X - SHUTDOWN_RECT[0] / 2, CENTER_Y - SHUTDOWN_RECT[1] / 2)
            pygame.draw.rect(screen, BLACK, [SHUTDOWN_RECT_XY, SHUTDOWN_RECT], border_radius=10)
            screen.blit(NO_CAN_BUS_R, (CENTER_X - calc(WIDTH, 18), CENTER_Y - calc(HEIGHT, 5)))
            shutdown = FONT_1.render("Shutting down in: " + str(countdown) + " s", True, WHITE, BLACK)
            screen.blit(shutdown, (CENTER_X - calc(WIDTH, 18), CENTER_Y))
            pygame.display.flip()
            if countdown == 0:
                power_off = True
                break
            if loop:
                continue
        else:
            data = message.data
            message_id = message.arbitration_id
            dlc = message.dlc
    if TEST_MODE or message is None:
        data = None
        message_id = None
        dlc = None
    # Reset shutdown countdown
    countdown = 10

    # List of what to update on the screen
    display_update = []
    # Clearing screen
    if clear:
        screen.fill((60, 60, 60))
        values = {x : 0 for x in units}
        old_values = {x : None for x in units}
        pygame.display.flip()

    if message_id == 0x400 and dlc == 3:
        message = struct.unpack("<BBb", data)
        bit_list_3 = bitfield_3_return(message[0])
        # High beam input is inverted
        high_beam = not bit_list_3[0]
        right_blinker = bit_list_3[1]
        left_blinker = bit_list_3[2]
        raw_fuel_level = message[1]
        out_temp = message[2]
        # Fuel level averaging
        if raw_fuel_level > FUEL_MAX:
            raw_fuel_level = FUEL_MAX
        elif raw_fuel_level < FUEL_MIN:
            raw_fuel_level = FUEL_MIN
        if filter_counter < 199:
            filter_sum += raw_fuel_level
            filter_counter += 1
            filter_ready = False
        else:
            fuel_level = int(filter_sum / filter_counter)
            filter_sum = 0
            filter_counter = 0
            filter_ready = True
        # Scaling and reading stabilation
        if filter_ready or start_up:
            # If filtering not ready
            if start_up:
                fuel_level = raw_fuel_level
            fuel_level = int((fuel_level - FUEL_MIN) / FUEL_DIVIDER - 100)
            if fuel_level != 0:
                fuel_level = fuel_level * -1
            if start_up is False and fuel_level > old_fuel_level:
                fuel_level = old_fuel_level + 1
            elif start_up is False and fuel_level < old_fuel_level:
                fuel_level = old_fuel_level - 1
            old_fuel_level = fuel_level
            start_up = False
        if "fuel_level" in units:
            values["fuel_level"] = fuel_level

    if message_id == ECU_CAN_ID and dlc == 8:
        # Unpack message
        message = struct.unpack("<HBbHH", data)
        rpm = message[0]
        if "rpm" in units:
            values["rpm"] = rpm
        if "tps" in units:
            values["tps"] = int(message[1] * 0.5)
        if "iat" in units:
            values["iat"] = message[2]
        if "map" in units:
            values["map"] = message[3]
        if "inj_pw" in units:
            values["inj_pw"] = round(message[4] * 0.016129, 1)

    elif message_id == ECU_CAN_ID + 2 and dlc == 8:
        message = struct.unpack("<HBBBBh", data)
        speed = message[0]
        # Odometer
        speed_sum += speed
        speed_sum_counter += 1
        if speed_sum_counter >= 100:
            # Calculating travelled distance and save it
            odometer = odometer_save(speed_sum, speed_sum_counter, distance_timer, odometer, PATH)
            distance_timer = time.monotonic()
            speed_sum = 0
            speed_sum_counter = 0
        if "oil_t" in units:
            values["oil_t"] = message[2]
        if "oil_p" in units:
            values["oil_p"] = round(message[3] * 0.0625, 1)
        if "fuel_p" in units:
            values["fuel_p"] = round(message[4] * 0.0625, 1)
        if "clt_t" in units:
            values["clt_t"] = message[5]

    elif message_id == ECU_CAN_ID + 3 and dlc == 8:
        message = struct.unpack("<bBBBHH", data)
        if "ign_ang" in units:
            values["ign_ang"] = message[0] * 0.5
        if "dwell" in units:
            values["dwell"] = round(message[1] * 0.05, 1)
        if "lambda" in units:
            values["lambda"] = round(message[2] * 0.0078125, 2)
        if "lambda_corr" in units:
            values["lambda_corr"] = int(message[3] * 0.5)
        if "egt_1" in units:
            values["egt_1"] = message[4]
        if "egt_2" in units:
            values["egt_2"] = message[5]

    elif message_id == ECU_CAN_ID + 4 and dlc == 8:
        message = struct.unpack("<BbHHBB", data)
        gear = message[0]
        batt_v = round(message[2] * 0.027, 1)
        if "batt_v" in units:
            values["batt_v"] = batt_v
        # Error flags
        errors = message[3]
        if "ethanol_cont" in units:
            values["ethanol_cont"] = message[5]

    elif message_id == ECU_CAN_ID + 5 and dlc == 8:
        message = struct.unpack("<BBhHBB", data)
        if "dbw_pos" in units:
            values["dbw_pos"] = int(message[0] * 0.5)

    elif message_id == ECU_CAN_ID + 7 and dlc == 8:
        message = struct.unpack("<HBBBBH", data)
        if "boost_t" in units:
            values["boost_t"] = message[0]
        if "dsg_mode" in units:
            values["dsg_mode"] = dsg_mode_return[message[2]]
        if "lambda_t" in units:
            values["lambda_t"] = round(message[3] * 0.01, 2)
        fuel_used = message[5] * 0.01
        if "fuel_used" in units:
            values["fuel_used"] = round(fuel_used, 1)

    if clear or int(odometer) != int(old_odometer):
        trip = odometer - odometer_start
        if fuel_used != 0 and trip != 0:
            fuel_consum = round(fuel_used / ((trip) / 100), 1)
            if "fuel_consum" in units:
                values["fuel_consum"] = fuel_consum

    # Shift light
    if TEST_MODE is False:
        # Shift light
        if rpm > END - STEP * 5:
            shift_light_rpi5.action(rpm, STEP, END, led_br)
            shift_light_off = False
            # Make sure all leds are off
        else:
            if shift_light_off is False:
                shift_light_rpi5.leds_off()
                shift_light_off = True

        # Dimmer (10Hz update rate from ADC)
        if time.monotonic() > dimmer_timer_1:
            dimmer_timer_1 = time.monotonic() + .1
            dark = is_dark(old_dark)
            # If ambient light hasn't changed: reset timer
            if dark is old_dark:
                dimmer_timer_4 = time.monotonic() + 4
            # If timer hasn't been reseted in 4 seconds: change brightness
            if time.monotonic() > dimmer_timer_4:
                dimmer(dark)
                old_dark = dark

    # To make sure a unit button is pressed in menu
    if units_ok:
        # Update values, when needed
        # Top left value update
        if values[units[0]] != old_values[units[0]] or clear:
            pygame.draw.rect(screen, BLACK, TOP_LEFT, border_radius=10)
            value_0_r = FONT_3.render(str(values[units[0]]), True, WHITE, BLACK)
            screen.blit(units_r[0], (TOP_LEFT[0] + BOX_TEXT_X, TOP_LEFT[1] + UNIT_TEXT_Y))
            screen.blit(value_0_r, (TOP_LEFT[0] + BOX_TEXT_X, TOP_LEFT[1] + VALUE_TEXT_Y))
            display_update.append(TOP_LEFT)
        # Center left value update
        if values[units[1]] != old_values[units[1]] or clear:
            pygame.draw.rect(screen, BLACK, CENTER_LEFT, border_radius=10)
            value_1_r = FONT_3.render(str(values[units[1]]), True, WHITE, BLACK)
            screen.blit(units_r[1], (CENTER_LEFT[0] + BOX_TEXT_X, CENTER_LEFT[1] + UNIT_TEXT_Y))
            screen.blit(value_1_r, (CENTER_LEFT[0] + BOX_TEXT_X, CENTER_LEFT[1] + VALUE_TEXT_Y))
            display_update.append(CENTER_LEFT)
        # Bottom left value update
        if values[units[2]] != old_values[units[2]] or clear:
            pygame.draw.rect(screen, BLACK, BOTTOM_LEFT, border_radius=10)
            value_2_r = FONT_3.render(str(values[units[2]]), True, WHITE, BLACK)
            screen.blit(units_r[2], (BOTTOM_LEFT[0] + BOX_TEXT_X, BOTTOM_LEFT[1] + UNIT_TEXT_Y))
            screen.blit(value_2_r, (BOTTOM_LEFT[0] + BOX_TEXT_X, BOTTOM_LEFT[1] + VALUE_TEXT_Y))
            display_update.append(BOTTOM_LEFT)
        # Top right value update
        if values[units[3]] != old_values[units[3]] or clear:
            pygame.draw.rect(screen, BLACK, TOP_RIGHT, border_radius=10)
            value_3_r = FONT_3.render(str(values[units[3]]), True, WHITE, BLACK)
            screen.blit(units_r[3], (TOP_RIGHT[0] + BOX_TEXT_X, TOP_RIGHT[1] + UNIT_TEXT_Y))
            screen.blit(value_3_r, (TOP_RIGHT[0] + BOX_TEXT_X, TOP_RIGHT[1] + VALUE_TEXT_Y))
            display_update.append(TOP_RIGHT)
        # Center right value update
        if values[units[4]] != old_values[units[4]] or clear:
            pygame.draw.rect(screen, BLACK, CENTER_RIGHT, border_radius=10)
            value_4_r = FONT_3.render(str(values[units[4]]), True, WHITE, BLACK)
            screen.blit(units_r[4], (CENTER_RIGHT[0] + BOX_TEXT_X, CENTER_RIGHT[1] + UNIT_TEXT_Y))
            screen.blit(value_4_r, (CENTER_RIGHT[0] + BOX_TEXT_X, CENTER_RIGHT[1] + VALUE_TEXT_Y))
            display_update.append(CENTER_RIGHT)
        # Bottom right value update
        if values[units[5]] != old_values[units[5]] or clear:
            pygame.draw.rect(screen, BLACK, BOTTOM_RIGHT, border_radius=10)
            value_5_r = FONT_3.render(str(values[units[5]]), True, WHITE, BLACK)
            screen.blit(units_r[5], (BOTTOM_RIGHT[0] + BOX_TEXT_X, BOTTOM_RIGHT[1] + UNIT_TEXT_Y))
            screen.blit(value_5_r, (BOTTOM_RIGHT[0] + BOX_TEXT_X, BOTTOM_RIGHT[1] + VALUE_TEXT_Y))
            display_update.append(BOTTOM_RIGHT)
        # Save old values
        for x in range(6):
            if values[units[x]] != old_values[units[x]] or clear is True:
                old_values[units[x]] = values[units[x]]

    # Gear update
    if gear != old_gear or clear:
        pygame.draw.rect(screen, BLACK, CENTER_TOP, border_radius=10)
        old_gear = gear
        if gear == 0:
            gear = "N"
        gear_r = FONT_3.render(str(gear), True, WHITE, BLACK)
        if gear == "N":
            screen.blit(gear_r, (CENTER_X - ONE_LETTER_3[0] / 2, CENTER_TOP[1] + CENTER_TOP[2] / 2 - ONE_LETTER_3[1] / 2))
        else:
            screen.blit(gear_r, (CENTER_X - ONE_DIGIT_3[0] / 2,CENTER_TOP[1] + CENTER_TOP[2] / 2 - ONE_LETTER_3[1] / 2))
        display_update.append(CENTER_TOP)
    # Speed update
    if speed != old_speed or clear:
        old_speed = speed
        pygame.draw.rect(screen, BLACK, CENTER, border_radius=10)
        speed_r = FONT_4.render(str(speed), True, WHITE, BLACK)
        screen.blit(speed_r, (CENTER_X - DIGITS_4[len(str(speed)) - 1][0] / 2, CENTER_Y - DIGITS_4[0][1] / 2))
        screen.blit(KMH_TEXT, (CENTER_X - KMH_2[0] / 2, calc(HEIGHT, 59)))
        display_update.append(CENTER)

    clock = time.strftime("%H:%M")
    if clock != old_clock or out_temp != old_out_temp or int(odometer) != int(old_odometer) or clear:
        pygame.draw.rect(screen, BLACK, CENTER_BOTTOM, border_radius=10)
        screen.blit(CELSIUS_20, (CENTER_X + calc(WIDTH, 9), calc(HEIGHT, 73)))
        # Clock update
        old_clock = clock
        clock_r = FONT_2.render(clock, True, WHITE, BLACK)
        screen.blit(clock_r, (CENTER_X - calc(WIDTH, 12), calc(HEIGHT, 72)))
        # Out temp update
        old_out_temp = out_temp
        out_temp_r = FONT_2.render(str(out_temp), True, WHITE, BLACK)
        out_temp_location = CENTER_X + calc(WIDTH, 9) - DIGITS_2[len(str(out_temp)) - 1][0], calc(HEIGHT, 72)
        if out_temp < 0:
            out_temp_location = out_temp_location[0] + calc(WIDTH, 1),  calc(HEIGHT, 72)
        screen.blit(out_temp_r, out_temp_location)
        # Odometer update
        old_odometer = odometer
        odometer_r = FONT_2.render(str(int(odometer)) + " km", True, WHITE, BLACK)
        screen.blit(odometer_r, (CENTER_X - calc(WIDTH, 12), calc(HEIGHT, 80)))
        display_update.append(CENTER_BOTTOM)

    # RPM Bar
    if rpm != old_rpm or clear:
        rpm_bar = int(rpm * (WIDTH / 10000))
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, RPM_HEIGHT))
        pygame.draw.rect(screen, LIGHT_BLUE, (0, 0, rpm_bar, RPM_HEIGHT))
        for x in range(len(rpm_list)):
            screen.blit(rpm_list[x], (WIDTH / 10 * (x + 1) - ONE_DIGIT_3[0] / 2, RPM_HEIGHT / 2 - ONE_DIGIT_3[1] / 2))
        old_rpm = rpm
        display_update.append((0, 0, WIDTH, RPM_HEIGHT))

    if old_left_blinker != left_blinker or clear:
        if left_blinker:
            blinker_colour = GREEN
        else:
            blinker_colour = BLACK
        # X, Y, SIZE
        bl = (calc(WIDTH, 27), calc(HEIGHT, 31), calc(WIDTH, 2))
        pygame.draw.polygon(screen, blinker_colour, [[bl[0], bl[1]], [bl[0] + bl[2], bl[1] - bl[2]], [bl[0] + bl[2], bl[1] + bl[2]]])
        pygame.draw.rect(screen, blinker_colour, (bl[0] + bl[2], bl[1] - bl[2] / 2, bl[2], bl[2]))
        old_left_blinker = left_blinker
        display_update.append((bl[0] - 10, bl[1] - bl[2] - 10, bl[2] * 2 + 20, bl[2] * 2 + 20))

    if old_right_blinker != right_blinker or clear:
        if right_blinker:
            blinker_colour = GREEN
        else:
            blinker_colour = BLACK
        br = (calc(WIDTH, 73), calc(HEIGHT, 31), calc(WIDTH, 2))
        pygame.draw.polygon(screen, blinker_colour, [[br[0], br[1]], [br[0] - br[2], br[1] - br[2]], [br[0] - br[2], br[1] + br[2]]])
        pygame.draw.rect(screen, blinker_colour, (br[0] - br[2] * 2, br[1] - br[2] / 2, br[2], br[2]))
        old_right_blinker = right_blinker
        display_update.append((br[0] - br[2] * 2 - 10, bl[1] - br[2]- 10, br[2] * 2 + 20, br[2] * 2 + 20))

    if old_high_beam != high_beam or clear:
        pygame.draw.rect(screen, (60, 60, 60), HIGH_BEAM)
        if high_beam:
            screen.blit(HIGH_BEAM_BLUE, (HIGH_BEAM[0], HIGH_BEAM[1]))
        else:
            screen.blit(HIGH_BEAM_BLACK, (HIGH_BEAM[0], HIGH_BEAM[1]))
        old_high_beam = high_beam
        display_update.append(HIGH_BEAM)

    # Fuel level warning
    if fuel_level is not None and fuel_level < 6:
        refuel = True
    elif fuel_level is not None and fuel_level > 10:
        refuel = False

    if refuel != old_refuel or clear:
        pygame.draw.rect(screen, (60, 60, 60), FUEL_PUMP)
        if refuel is False:
            screen.blit(FUEL_PUMP_BLACK, (FUEL_PUMP[0], FUEL_PUMP[1]))
        else:
            screen.blit(FUEL_PUMP_YELLOW, (FUEL_PUMP[0], FUEL_PUMP[1]))
        old_refuel = refuel
        display_update.append(FUEL_PUMP)

    # Errors
    error_list = []
    if errors != 0:
        error_list = error_flags(errors)

    # Battery voltage low warning
    if batt_v < 11.3 or batt_v < 13 and rpm > 0:
        error_list.append("Battery " + str(batt_v) + "V")

    # Bottom bar
    if error_list != old_error_list or cpu_timer < time.monotonic() or clear:
        # 1Hz update rate on cpu statistics
        cpu_timer = time.monotonic() + 1
        if len(error_list) == 0:
            pygame.draw.rect(screen, LIGHT_BLUE, BOTTOM_BAR)
            cpu_temp = getCPUtemperature()
            cpu_load = str(psutil.cpu_percent())
            cpu_stats_text = FONT_2.render("Cpu: " + cpu_temp + ", " + cpu_load +
                                           " %", True, WHITE, LIGHT_BLUE)
            screen.blit(cpu_stats_text, (0, BOTTOM_BAR[1]))
        else:
            errors_text = str("Errors " + str(len(error_list)) + ": " + ", ".join(error_list))
            errors_r = FONT_2.render(errors_text, True, WHITE, RED)
            pygame.draw.rect(screen, RED, BOTTOM_BAR)
            screen.blit(errors_r, (0, BOTTOM_BAR[1]))
        old_error_list = error_list
        clear = False
        display_update.append(BOTTOM_BAR)

    if touch:
        # Pick a new unit from menu
        for x in range(6):
            if unit_change == x:
                units[x] = menu(pos)
                if units[x] is not None:
                    units_r[x] = FONT_1.render(title_text_units[units[x]], True, WHITE, BLACK)
                    unit_change = None
                    clear = True
                    units_ok = True
                else:
                    units_ok = False
        # Enable menu draw
        for x in range(6):
            if clear is False and pygame.Rect.collidepoint(unit_buttons[x], pos):
                draw_menu = True
                unit_change = x
        touch = False

        # Saving to memory
        if clear:
            units_memory = open(PATH + "units_memory.txt", "w")
            for x in range(len(units)):
                units_memory.write(str(units[x]) + "\n")
            units_memory.close()

    if draw_menu:
        screen.fill((60, 60, 60))

        def create_rect(x, y, text):
            pygame.draw.rect(screen, BLACK, [x, y, MENU_RECT[0], MENU_RECT[1]], border_radius=10)
            name = FONT_1.render(text, True, WHITE)
            screen.blit(name, (x + MENU_TEXT_XY[0], y + MENU_TEXT_XY[1]))
            return pygame.Rect(x, y, MENU_RECT[0], MENU_RECT[1])
        # Coordinates
        coordinates_x = []
        coordinates_y = []
        coordinate_x = MENU_SPACING[0]
        coordinate_y = MENU_SPACING[1]
        for x in range(4):
            coordinates_x.append(coordinate_x)
            coordinate_x += MENU_SPACING[0] + MENU_RECT[0]
        for x in range(6):
            coordinates_y.append(coordinate_y)
            coordinate_y += MENU_SPACING[1] + MENU_RECT[1]

        # Buttons
        rpm_button = create_rect(coordinates_x[0], coordinates_y[0], "RPM")
        tps_button = create_rect(coordinates_x[1], coordinates_y[0], "TPS")
        iat_button = create_rect(coordinates_x[2], coordinates_y[0], "IAT")
        map_button = create_rect(coordinates_x[3], coordinates_y[0], "MAP")
        inj_pw_button = create_rect(coordinates_x[0], coordinates_y[1], "Inj pw.")
        oil_t_button = create_rect(coordinates_x[1], coordinates_y[1], "Oil temp.")
        oil_p_button = create_rect(coordinates_x[2], coordinates_y[1], "Oil pressure")
        fuel_p_button = create_rect(coordinates_x[3], coordinates_y[1], "Fuel pressure")
        clt_t_button = create_rect(coordinates_x[0], coordinates_y[2], "Coolant temp.")
        ign_ang_button = create_rect(coordinates_x[1], coordinates_y[2], "Ignition angle")
        dwell_button = create_rect(coordinates_x[2], coordinates_y[2], "Dwell time")
        lambda_button = create_rect(coordinates_x[3], coordinates_y[2], "Lambda")
        lambda_corr_button = create_rect(coordinates_x[0], coordinates_y[3], "Lambda corr.")
        egt_1_button = create_rect(coordinates_x[1], coordinates_y[3], "EGT 1")
        egt_2_button = create_rect(coordinates_x[2], coordinates_y[3], "EGT 2")
        batt_v_button = create_rect(coordinates_x[3], coordinates_y[3], "Battery voltage")
        ethanol_cont_button = create_rect(coordinates_x[0], coordinates_y[4], "Ethanol content")
        dbw_pos_button = create_rect(coordinates_x[1], coordinates_y[4], "Dbw position")
        boost_t_button = create_rect(coordinates_x[2], coordinates_y[4], "Boost target")
        dsg_mode_button = create_rect(coordinates_x[3], coordinates_y[4], "DSG Mode")
        lambda_t_button = create_rect(coordinates_x[0], coordinates_y[5], "Lambda target")
        fuel_used_button = create_rect(coordinates_x[1], coordinates_y[5], "Fuel used")
        fuel_level_button = create_rect(coordinates_x[2], coordinates_y[5], "Fuel level")
        fuel_consumption_button = create_rect(coordinates_x[3], coordinates_y[5], "Fuel consum.")

        pygame.display.flip()
        draw_menu = False

    # Update screen
    if unit_change is None:
        pygame.display.update(display_update)

# Close the program
odometer = odometer_save(speed_sum, speed_sum_counter, distance_timer, odometer, PATH)
pygame.quit()
if TEST_MODE is False:
    close_io()
if power_off:
    print("Shutdown")
    os.system("sudo shutdown -h now")
