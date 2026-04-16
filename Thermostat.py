#
# Functionality:
#
# The thermostat has three states: off, heat, cool
#
# The lights will represent the state that the thermostat is in.
#
# If the thermostat is set to off, the lights will both be off.
#
# If the thermostat is set to heat, the Red LED will be fading in 
# and out if the current temperature is blow the set temperature;
# otherwise, the Red LED will be on solid.
#
# If the thermostat is set to cool, the Blue LED will be fading in 
# and out if the current temperature is above the set temperature;
# otherwise, the Blue LED will be on solid.
#
# One button will cycle through the three states of the thermostat.
#
# One button will raise the setpoint by a degree.
#
# One button will lower the setpoint by a degree.
#
# The LCD display will display the date and time on one line and
# alternate the second line between the current temperature and 
# the state of the thermostat along with its set temperature.
#
# The Thermostat will send a status update to the Server
# over the serial port every 1 hour
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description             |   Date
#------------------------------------------------------------------
#    1          Initial Development
#------------------------------------------------------------------
#    2          Initial Enhancement         3/20/2026
#------------------------------------------------------------------
#
##
## Import necessary to provide timing in the main loop and for payload structure
##
from time import sleep
from datetime import datetime

##
## Imports required to allow us to build a fully functional state machine
##
from statemachine import StateMachine, State

##
## Imports necessary to provide connectivity to the 
## thermostat sensor and the I2C bus
##
import board
import adafruit_ahtx0

##
## These are the packages that we need to pull in so that we can work
## with the GPIO interface on the Raspberry Pi board and work with
## the 16x2 LCD display
##
# import board - already imported for I2C connectivity
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

## This imports the Python serial package to handle communications over the
## Raspberry Pi's serial port. 
import serial

##
## Imports required to handle our Button, and our PWMLED devices
##
from gpiozero import Button, PWMLED

##
## This package is necessary so that we can delegate the blinking
## lights to their own thread so that more work can be done at the
## same time
##
from threading import Thread

##
## This is needed to get coherent matching of temperatures.
##
from math import floor

##
## Import needed for PayloadGenerator class
##
from payload_generator import PayloadGenerator

##
## Import needed for serializing payload dict
##
import json

##
## Imports needed for HMAC signature
##
import hmac
import hashlib

## Import needed to send data to server endpoint via HTTP
import requests

##
## Import needed for env variable
##
import os
from dotenv import load_dotenv

load_dotenv()
secretKey = os.environ.get('SECRET_KEY')

##
## DEBUG flag - boolean value to indicate whether or not to print 
## status messages on the console of the program
## 
DEBUG = True

##
## I2C instance to communicate with
## devices on the I2C bus.
##
i2c = board.I2C()

##
## Initialize Temperature and Humidity sensor
##
thSensor = adafruit_ahtx0.AHTx0(i2c)

##
## Initialize our serial connection
##
ser = serial.Serial(
        port='/dev/ttyS0', # This would be /dev/ttyAM0 prior to Raspberry Pi 3
        baudrate = 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS, 
        timeout=1
)

##
## The two LEDs, utilizing GPIO 18, and GPIO 23
##
redLight = PWMLED(18)
blueLight = PWMLED(23)


##
## ManagedDisplay - Class intended to manage the 16x2 
## Display
##
class ManagedDisplay():
    def __init__(self):
        ##
        ## Setup the six GPIO lines to communicate with the display.
        ## This leverages the digitalio class to handle digital 
        ## outputs on the GPIO lines.
        ##
        ## Make sure that the port mappings match the
        ## physical wiring of the display interface to the 
        ## GPIO interface.
        ##
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        # Size of character LCD
        self.lcd_columns = 16
        self.lcd_rows = 2 

        self.lcd = characterlcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en, 
                    self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7, 
                    self.lcd_columns, self.lcd_rows)

        # wipe LCD screen before we start
        self.lcd.clear()

    def cleanupDisplay(self):
        # Clear the LCD first - otherwise we won't be abe to update it.
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()

    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.message = message 

##
## Initialize display
##
screen = ManagedDisplay()

##
## TemperatureMachine - This is the StateMachine implementation class.
## The purpose of this state machine is to manage the three states
## handled by the thermostat:
##
##  off
##  heat
##  cool
##
##
class TemperatureMachine(StateMachine):
    "A state machine designed to manage the thermostat"

    ##
    ## Define the three states for our machine.
    ##
    off = State(initial = True)
    heat = State()
    cool = State()

    ##
    ## Default temperature setPoint is 72 degrees Fahrenheit
    ##
    setPoint = 72

    ##
    ## arbitrary default device id
    ##
    deviceId = "pi4_4289"

    ##
    ## Event that provides the state machine behavior
    ## of transitioning between the three states of our 
    ## thermostat
    ##
    cycle = (
        off.to(heat) |
        heat.to(cool) |
        cool.to(off)
    )

    def on_enter_heat(self):
        ## use Temperature Machine's updateLights method to handle LEDs

        if(DEBUG):
            print("* Changing state to heat")
        self.updateLights()

    def on_exit_heat(self):
        ## ensure red light is off when exiting heat state
        redLight.off()

    def on_enter_cool(self):
        if(DEBUG):
            print("* Changing state to cool")
        self.updateLights()
    
    def on_exit_cool(self):
        blueLight.off()

    def on_enter_off(self):
        ## ensure both LEDs are off in off state

        if(DEBUG):
            print("* Changing state to off")
        blueLight.off()
        redLight.off()
    
    ##
    ## This is triggered by the button_pressed event
    ## handler for the first button
    ##
    def processTempStateButton(self):
        if(DEBUG):
            print("Cycling Temperature State")

        self.cycle()

    ##
    ## This is triggered by the button_pressed event
    ## handler for the second button
    ##
    def processTempIncButton(self):
        if(DEBUG):
            print("Increasing Set Point")

        self.setPoint += 1
        self.updateLights()

    ##
    ## This is triggered by the button_pressed event
    ## handler for the third button
    ##
    def processTempDecButton(self):
        if(DEBUG):
            print("Decreasing Set Point")

        self.setPoint -= 1
        self.updateLights()

    def updateLights(self):
        ## Make sure we are comparing temperatures in the correct scale
        temp = floor(self.getFahrenheit())
        redLight.off()
        blueLight.off()
    
        ## Verify values for debug purposes
        if(DEBUG):
            print(f"State: {self.current_state.id}")
            print(f"SetPoint: {self.setPoint}")
            print(f"Temp: {temp}")

        currState = self.current_state.id
        
        ## Match-case statements for readability
        match currState:
            case "heat":
                ## Ensure light is pulsing or on based on setpoint and current temp
                if temp >= self.setPoint:
                    redLight.on()
                else:
                    redLight.pulse()
            case "cool":
                if temp <= self.setPoint:
                    blueLight.on()
                else:
                    blueLight.pulse()
            ## In the event updateLights gets called in off state
            case "off":
                blueLight.off()
                redLight.off()
            ## In the event there is no match for currState, treat it as 'off' state 
            case _:
                blueLight.off()
                redLight.off()

    ##
    ## Kickoff the display management functionality of the thermostat
    ##
    def run(self):
        myThread = Thread(target=self.manageMyDisplay)
        myThread.start()

    def getFahrenheit(self):
        t = thSensor.temperature
        return (((9/5) * t) + 32)
    
    def create_packet(self):
        payloadText = self.setup_payload()
        payloadBytes = payloadText.encode("utf-8")
        signature = self.generate_HMAC(secretKey, payloadBytes)

        return {
            "payload": payloadText,
            "signature": signature
        }

    ##
    ##  Configure payload for the Server
    ##
    def setup_payload(self):

        # Verify function is called
        if(DEBUG):
            print("setup_payload called")

        ##
        ## instantiate PayloadGenerator object and create payload
        ##
        generator = PayloadGenerator()
        payload = generator.create_payload(self.deviceId, self.current_state.id, self.setPoint, floor(self.getFahrenheit()))

        ##
        ## serialize payload to send over serial port
        ##
        output = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        return output
    
    def generate_HMAC(self, secret, message):
        return hmac.new(secret, message, hashlib.sha256).hexdigest()
    
    ## Continue display output
    endDisplay = False

    ##
    ##  This function is designed to manage the LCD Display
    ##
    def manageMyDisplay(self):
        counter = 1
        altCounter = 1
        while not self.endDisplay:
            ## Only display if the DEBUG flag is set
            if(DEBUG):
                print("Processing Display Info...")
        
            current_time = datetime.now()
    
            ## Setup display line 1
            lcd_line_1 = current_time.strftime('%b %d  %H:%M:%S\n')
    
            ## Setup Display Line 2
            if(altCounter < 6):
                lcd_line_2 = f"Curr Temp: {floor(self.getFahrenheit())}F"
    
                altCounter = altCounter + 1
            else:
                lcd_line_2 = f"{self.current_state.id}, {self.setPoint}F"

                altCounter = altCounter + 1
                if(altCounter >= 11):
                    # Run the routine to update the lights every 10 seconds
                    # to keep operations smooth
                    self.updateLights()
                    altCounter = 1
    
            ## Update Display
            screen.updateScreen(lcd_line_1 + lcd_line_2)
    
            ## Update server every 30 seconds
            # FIXME: Change from every 30 sec to every hour
            if(DEBUG):
               print(f"Counter: {counter}")
            if((counter % 30) == 0):
                packet = self.create_packet()
                
                ## leverage setupSerialOutput method to send state info to server
                ##ser.write((json.dumps(packet) + "\n").encode("utf-8"))

                ## new method of sending state info to server endpoint over HTTP
                requests.post("http://127.0.0.1:8000/ingestion", packet)
                counter = 1
            else:
                counter = counter + 1
            sleep(1)

        screen.cleanupDisplay()


##
## Setup our State Machine
##
tsm = TemperatureMachine()
tsm.run()


##
## Configure the gray button to use GPIO 24
##
grayButton = Button(24)
## call processTempStateButton method when gray button is pressed
grayButton.when_pressed = tsm.processTempStateButton

##
## Configure the Red button to use GPIO 25
##
redButton = Button(25)
## call processTempIncButton when red button is pressed
redButton.when_pressed = tsm.processTempIncButton

##
## Configure our Blue button to use GPIO 12
##
blueButton = Button(12)
## call processTempDecButton when blue button is pressed
blueButton.when_pressed = tsm.processTempDecButton

repeat = True

##
## Repeat until the user creates a keyboard interrupt (CTRL-C)
##
while repeat:
    try:
        ## wait
        sleep(30)

    except KeyboardInterrupt:
        ## Catch the keyboard interrupt (CTRL-C) and exit cleanly
        ## we do not need to manually clean up the GPIO pins, the 
        ## gpiozero library handles that process.
        print("Cleaning up. Exiting...")

        ## Stop the loop
        repeat = False
        
        ## Close down the display
        tsm.endDisplay = True
        sleep(1)