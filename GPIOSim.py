#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
# GPIOSim
#
# Bob Vann - http://bobvann.noip.me
#
# https://github.com/bobvann/GPIOSim
# 
# Requires Python 3
#
#
# License https://raw.githubusercontent.com/bobvann/RPirrigate/master/LICENSE
#


from tkinter import Tk, Canvas, Frame, BOTH, Menu, Label, PhotoImage
from configparser import RawConfigParser
from PIL import Image,ImageTk
import os, tempfile, signal

#GPIO STATE:
# 0 = N.D (3v3, 5v, gnd)
# 1 = GPIO.IN
# 2 = GPIO.OUT
# 3 = GPIO.ND (when not chosen yet)



class GPIOSim(Frame):
    #********** Settings *******

    #             ND;     ND;      IN_LOW;    IN_HIGH;  OUT_LOW;   OUT_HIGH;  GPIO_ND;  GPIO_ND
    PIN_COLORS = ["black","black",   "#9ADA90", "green",  "#74C6BD", "blue",  "yellow", "yellow"]

    PIN_SIZE = 15
    PIN_DISTANCE = 10

    START_X = 140
    START_Y = 20


    GPIO_STATE_DEFAULT = [
            0, 0,  #3v3   , 5v
            3, 0,  #GPIO2 , 5V
            3, 0,  #GPIO3 , GND 
            3, 3,  #GPIO4 , GPIO14
            0, 3,  #GND   , GPIO15
            3, 3,  #GPIO17, GPIO18
            3, 0,  #GPIO27, GND
            3, 3,  #GPIO22, GPIO23
            0, 3,  #3V3   , GPIO24
            3, 0,  #GPIO10, GND
            3, 3,  #GPIO9 , GPIO25
            3, 3,  #GPIO11, GPIO8
            0, 3,  #GND   , GPIO7
            0, 0,  #I2C   , I2C     #FROM HERE
            3, 0,  #GPIO5 , GND     #RPI >= B+
            3, 3,  #GPIO6 , GPIO12
            3, 0,  #GPIO13, GND
            3, 3,  #GPIO19, GPIO16
            3, 3,  #GPIO26, GPIO20
            0, 3   #GND   , GPIO21
        ]

    GPIO_NAMES = [
            "3v3","5v",
            "GPIO2","5V",
            "GPIO3","GND",
            "GPIO4","GPIO14",
            "GND","GPIO15",
            "GPIO17","GPIO18",
            "GPIO27","GND",
            "GPIO22","GPIO23",
            "3V3","GPIO24",
            "GPIO10","GND",
            "GPIO9","GPIO25",
            "GPIO11","GPIO8",
            "GND","GPIO7",
            "I2C","I2C",
            "GPIO5","GND",
            "GPIO6","GPIO12",
            "GPIO13","GND",
            "GPIO19","GPIO16",
            "GPIO26","GPIO20",
            "GND","GPIO21"
        ]


    

    BG_COLOR = "white"
    TEXT_COLOR = "black"
    #******** End Settings ********

    WIN_WIDTH = 2*START_X + 2*PIN_SIZE + PIN_DISTANCE
    WIN_HEIGHT = 2*START_Y + 20*PIN_SIZE + 19*PIN_DISTANCE
    
    WIN_SIZE = str(WIN_WIDTH) + "x" + str(WIN_HEIGHT) + "+200+100"

    STATE_ND = 0
    STATE_GPIO_IN = 1
    STATE_GPIO_OUT = 2
    STATE_GPIO_ND = 3

    VALUE_HIGH = 1
    VALUE_LOW = 0

    WORK_DIR = os.path.join(tempfile.gettempdir(), "GPIOSim") #os.path.join(os.path.expanduser('~'), '.GPIOSim') 
    WORK_FILE = os.path.join(WORK_DIR, "pins.ini")

    currState = [None]*40
    currValue = [None]*40

    def __init__(self, parent):
        Frame.__init__(self, parent)   
         


        if not os.path.exists(self.WORK_FILE):
            os.makedirs(self.WORK_DIR)
            self.simulateReboot(True)




        self.parent = parent

        menu = Menu(self.parent)
        menu1 = Menu(menu,tearoff=0)
        menu1.add_command(label="Simulate Reboot",command=self.simulateReboot)
        menu1.add_separator()
        menu1.add_command(label="Quit!", command=self.parent.quit)
        menu.add_cascade(label="Menu",menu=menu1)

        # display the menu
        self.parent.config(menu=menu)

        self.parent.title("GPIOSim")        
        self.pack(fill=BOTH, expand=1)

        self.canvas = None
        self.canvas = Canvas(self, bg=self.BG_COLOR) 
        #self.canvas.bind("<Button-1>",self.click)


        #Images (gif base64 encoded)
        imgInLeft = "R0lGODlhHgASAOf7AAoMCAITBBcQCAYbAAsaEBUYEBEaCRMeCB0ZIREhGRkhFB0gEyMmGiIpFy8mNTQyNiROCCJZACxYCTlUKzpWGyleADBeBjRdGCxiCShlAEFcM0BeKDJmAzpmBCFwADxlIBt1BC9yBGpZW0NpMTtvDzttKkdqPid8AENxHD12DDh5AE9tPEZyJUV2Lzh/AF5rYD5+CEV+Fz+AGFxzT1h4LUx9NUaEAkCGA2dxYUqCEF91V1V8ME+AG0WHADuKCFl/RU+IIT2PG2l8XkqPAEuMJFmFREWTBVCRDzGcAHl6g2yBaEuWADybAEKZDkaaAHCHYnaCgneEeFCcA2WPR0ChB1qaA1ebFnuIbk2gCkSlAFCiAFegAF6fAFehD3ORXmueEXOWT26aQU+qBnCZV1inF3yUboCRhWWmBlmqCnuYa2OqAGGqDGOnJVevAF6tAEi0AG2sAF2vIYyXhomado2Ze1S2BmOyBHKpO1e3AGqxBVy1B1q0GXKwAG6sNEm9AH2tB3WrNYmfc22zAHumX2K4AH+maWO0NW61D2m4En60AHK4AGy6AHm3AIW0AHW2IYKsYoSrbnuzPW22S2u7JXS3NpKzBmDAG5CyGW66OI2ph3G7MIuyP4mteou5AHu/AIOzYXa7QpSpnKajqHu8M4O/AIG+EZy4AHe/K4m+AJytdZW8AIO4XnDCNp+ug429KaGrppG4YX+8dHzDUZnAHZ3CAJ/AJo7FK5O+c5+7cp7CP5jKJ5bIQpvAhqi8ia+6lYfLZ5PPHZrFbKHNDK/HVqnJcqHRPqDSTLvDq7TTN7jGubTLnMbRO8DTQ8TGw7DSjb/UVLDSmMTTZ7rYXbjWeMvVVNPSX8jZQbnfOMjYYcfbU7Xeb9XaTs/abt7XcMLjUMXhe8fficvbwdzV4czncNnb2NThwcnkztXlt+nr6OXy2Ozx9PLx6OP34vnv9e306fzx/vP35vL3+ff2/v/3/fj69//58v/76//6+PH/8/L///799P78//j/9Pb/+vn+//3//CH+EUNyZWF0ZWQgd2l0aCBHSU1QACwAAAAAHgASAAAI/gCJATpFKRIrTM5+YYpEadIoUNBkadLUJ5KhVfDe9cO3b58/doaodEGj5gwaYneQiDmzxgqmW0yy7LHjpgsmd/9y/rs37xwbNdeWIePSB1cXRtuY6VqyKlgVRtaWAXMSC96+fvb0+ZvnDMsfatmKSZF0a4iibNlqMRkEy4grsJua8Lq37x8/fzl5GXE0TtouJJA4IbHV7RmiJp8+MSlWzZuiI8o6/qs7790gJ666YbPVoxeYIbnGRUOUI1WYL7OE0UJDJNy+e/T2xe4HZMkwbtwsgYBGhIyxarXcBOEEBI0qU6SWhEnXzh8/ffvipduBZRq4b2tI+OKxJZEqT06m/hS6kQdVpUQ9xtDj19Gev33lUMTRFm2WlhqZYsAh1anRkDFp3IDHcYec8Mhk/8ADnTkpYHHJJYs4QUMgMnDRCCqL2OCFFzeo0UgnioQwh0f+6KOPOiMYIQiIYnDQCgtPNaJIE0WUQQIXiZRyiAtTrHOPP/nc888KMORBiiB2VBCKCUPkwYgnW5RgRgld8JFIHka0EE49WnWkRAiI5AEHGhnQoYMKbthxiBYdXPGDD3YgWQULydRFD3SvYIAGIWq4oYIQV2QQJx56cIBDGR4sogYhaJAgR0d40XOMBF3ogYYdPawQhQRouKGGHiHoYEYEe7iRRxsWPDFZR/uIs8EQY2KssYYTGkBxgRRdtFFHCjMkAUEbbVzqwQsK5nSPPBvAUMcbeFgRwQsfDFEHHnbkQAEOt77hRxspTICOTjmJIMACCSRgQAEPOAAAAQQEMMABDCAwbgEKHNCAKM2QQw469PwTEAA7"
        imgInRight = "R0lGODlhHgASAOf8ABcOChASDwkZDg8YBxcZCw8dDicUJhcdABkfCxgmBBApABwnDi4kLCsnJjJHICNUBCZUACxdBC5fAD5XKTFgEiRmATZeLUVcOTpiJDhnGStuADZrDzxpFEZlLjVvATxuASl0ADpyAEhpODtzGUxrQEpwHUlwJDp6AVFsXlVwLUp0Ll9rXTaACF5uSzOEADuCAFpzTFJ5LWprdEx+HEWEEkiGBVh3bkaGEzWNADyMClh/PD+NAEeMAESKJjiSEk2MG2GAWVGMLTmYAFqJOkOXAFmKQXCBXUqWAHd8fkmWC22EX1KWDk+aAE2aE0edFUqeBHuEf3iJfEmkAFCiAF6dE1ihAF+gAHmQXkynAGeaPEWqAn2OfHWSbmKfOH+Sc16nBViqCU2vAFCsG4STe2KqAGeoC1SuD2KnLnedVYCXfWynHF6uAFiwAHCpEIaXhWeuAHOrAHmhUmOtII6YdVS1BWavFVa2AIOea2mqQoGgZnCvBGSzB3mvAH+uAGyzC1O8AGuwOG+1AGm3AHGyKGS6AIOyAHm2AG26AHuwOo2jiWm2PHS6Ani3FXa1NYKsa3a3I4G4BX+3GJmjkm65N421BpCpeW69GnG6MIGxX3O7Jma/KJS1C3q+AHm4SG7DAIq7AI63I5W3IHO/QYS2aoO+IZW8AIG6Une9YH3DFnjCN4+6W6CvlpqxlqC/AJvBAJC7ZpbDDYvHDpK8cZe4jpq7a6DBIJ26dbK+JIvIN4vJLpzELprEN4jGd57EUbW4lZbGc6bJPpzIaJnJdpzLXaPMQL7KMqjJjJHVcKvOl7zIsLbNnrfUWsrOYbLQoMXWNMbUTsbVV8vWQNDTVLbZc7/aUcXaQdXOjbnfOMrMycHaWbfeaL/hZcfkNsffbdPfUd/bcMHld9XW4NnjdN/c4dHjxdzfz8ztf+Di38vvtvXm9enr6Oby3/Py6ev26vzz7Or63/b0+Pb2//f61e/76Pb49P/1++77/Pb7/vn/4Pf+8/X/+v/8+/78///+9fn///3/+yH+EUNyZWF0ZWQgd2l0aCBHSU1QACwAAAAAHgASAAAI/gD55fvH7969d50aTRp0yZKqZqIUZboE6FEwZJoUNWI46Vi/ffTu8ZOH6AmZOmDCOOGVSooaPV+0nPklpswaMmuedMGXr94/ffReHcnF7VkkJrRMVanlrNqiJsLOkCkW7VqZM+j+iYTXz1aOTNCi7eLxStURXNKqRUoiCw8WYNCktWnSbF8/fvT+KUvyaJs3YEJOYSJiiVo2UDgcYRKyC9o2Rkl43fP5k9yPKaVuwaKSZRSNMt3EEWuCxlYNUsy+4eIRJx+/ePfcvQvCJFarUmSCVPoBRhe0YVR6GHNRxxy4XkSKzOMHTx/zPDkMtfq0h8adLkcguaJkxYcvD3LA/lmbhmXGun/7/vX754iFn1Kl9rC4gmbHok2G1syoFAMLqmXa1PEBOesZxM8/c4DgSR+UrPECF1fwQEghlIDBQiIlMHFIKKA8McI5BxJ0YDpDuMBIH5xUMYIXOjwRCCWLPGHCLBJ8YUghhyTRgT30fESPa+WYsMQhehjChAppYPAFJ3r4sQMJrECwhiF8vHEECT3x048++eyTzAZMvBGIIDXoEEUGUwQCByEhAJHGB3vooUcYHijBj5b6/KOVGxx8cZMfGnixggdrBLLGGhVsscIJYfjhBxgcSJKXSAYascEea4BhhgRjwEDoGmyAEUEUIuQAxhtsNEFBMiL1E5I+ZOy0UAEddIBBxgNIwPBCSnUcEQEUFzTBxrA1TBDOnXqKxI4DKbBhBx1rPGCDBTXQEQYdS1iAAgRVhPEHGyxg0M6B6owTDjarKJBAAQIgAIABDBwwALsEAMBAAwsQcEACCwQgQ0AAOw=="

        imgOutLeft = "R0lGODlhHgASAOf7AAgiSgYlPA8nNQYrLRUnOhovUxwwRB0yNgA2eiIzPyoxQgA2jh46TR85Wik9Vz44TBM/jARElgdEnSI/gRFEihhEfipBcgBIrQBLpBBFtwBOmhZLkSlJeQBSnABUpQBWrghTxABWwyNPpCBTjRZXlxpWowdZvxRXtABetyVYjBdWzxdbpABgvwBd4ABd5wBg2wRjyhpevwRj0BpexSlawxtc2TFbpBtd0wBk5TFdnwplxQxk2QBn4ThfjxNk6ABtzABs2QBr5gBq9BNrtABr7RhozwFt4jlloU5kdB1o3kllhQpv3QBy3i9rnABz2QBy5Uxjohdwww5x2A9v6wB3zwB070NqjgF5xAB26gB34zRtrgB50QB1/wB74R504wZ76DBv7mVpjwB+6gp77yF16k1vp0NwwQB+/wCC7jx0ygCC9kd2pmJwoCt9w092og6D6lp2lx5/9R6A71N2tgSJ6CB//AiG/z961BaH4E940Fl6oACL/j994COH2j2Bz06AqiaG5gCQ9QCS4xiK+DOG0zaE30CA7gCS/1GBxW5/kwGW9R+O9R+P71GD222BpV6GoAeY8GaFmkmKvzOM7TKP4mCLsACh+TGV4Red74CGqVSQzUiT1TGX+EuS3nyLqlqS1nqOshOn6zOe6nCTqGGUzGWVwSel8EOe5XCVvGiV23GWt0yb/3OWy3WW4kqj62+frHyZyG+e3oaduiiz/nGj0o+bzoKe4Tiz8Uqt+3ai6UWx6mOq+6ehrGGx7IGp5DS+/Ea5/5Wo7pSsyl656kO//zrG4j/F6H2z5V27/DzG/VTB85uyw4G411HH/5a52KW5uH7A/2nN81HV/6jA0nTL/2fQ/2PU+X7P8ZjO4JTN+bzL36fQ7LjL8rDQ4MfNz9HUxNvX0sfj7tLo+N7m7+Tp7OTw5/Px9fL08dr7/vj07Pzy+fv14O73//H3+fr18+P+6P/19u387//2/Pj69/X88fD9/u3/+P/92v/6+fT++f/87f77//j9//j/7v7+9Pz/+yH+EUNyZWF0ZWQgd2l0aCBHSU1QACwAAAAAHgASAAAI/gDzpcM375+8d50GFbpD6dKmbX4MTWrDCE+uYIAA+QFEiRCzfPz87Ztnr1GRJ3WY8MDhyxARI1Kk4ACTa4oUKmdcvODD7hzIf/VouViU7NelGL0+oRCVjBidFrTaOPllbNaYNOL2/RPZz5mKQrqamTLRatOLU9KKyTFxLE+UW8qIXYnC7V7Ifeu6oYjTzBouE6lKgcA0TJooFbbm4MDUDFmdFs7a+VNXz1y5E0AghcKEIw8pHV+oVVsVQlOpF5eiUbsUopW+fPH08UOn5cUgS5CMFIE1REgoV8BmmImlow+0a51gSDo3st6+dH92iBmkKIsJVHNuLFKkCIgWWTGu/mTDtquFlnL89vXTSurEmEGHvnhQhSjEF0GQiNBANeQHp2HIZNGEOPKEhI859QizwBd0MDJGDGvAkkEdgtAxxQeVlFHDFm/Y8cMK4cDzDz3/8NOOOqx4sEUgYwBRghuasCBGF3ssUUItIkhhxxNo6NCEOfT4ww8/BrFjhQdYoPEFFiuM0sMOdnThxQ45vOIBEHiokUUISuTDXD5C+jPOESZ4oUYVMNiQyQZGvEGFGhc8kogEWXxRxRga6KHVOf/Y484+2pAAAxlfZAECFJ5Q8IQaTnCRQSSOXIBFFUt0cQEo6ezTjj377JPPMhTI8MUSQHzghioLtCCHEEJEkAgbdhegMQUQVUAwDZHp4ePPP6BIwIMQVTixQRiZaEDEFlm80EEkSnwgxBNAyFDBN/NoNY9I/CAxwQtGEIEDAnBw0MEORAghwwhKVMBCEEkAgUEK42hFDjjgePOMBQ0ckEABBOgbAAACDDAAAQ8owIABBDjQgAO8BAQAOw=="

        imgOutRight = "R0lGODlhHgASAOf7AAsjMAklQQYnOA8lNxAnPyAoOBosNRowPhUyRAoyfic1OgA4kRw3WCo3RABAmTA9SgNDoydAWRZBiABHnwBGsgtHjRtCkCxCYSREeQBJvgFOoAFNrRZIqQROpx5LeQ5OmgBQvSBQlwBWvRJVlQBWygRZuDBSfAVarAJX0wBbyB1YpQ5btQBd0Q1Z1SdYkwBhuQBhxwBf2xdcywBh4wJi1xhevjRcjBpexSRfnwhlxRtirgBnzB5e1DFfmx9itgBm7yhjnRFowSlmmgBr5hZl4gBs4ABr7SBpowBu1Bhn1Rhozxhn3EpkbUNjjhdsuABu6ABw4gBy0Ddolwpv3QBw8QBy3ght+FRjgCBp5gBx+Q5v5ABz7RBv7DxskgB36wB45RVz2gB64FJoqU1smAR82wB+1Rt21gB94T9wuWFqlAp69gB/6wCA5Td0vAB/+QCA80l1mRN960tytxN/3xZ98ih56DZ51TZ6zwCI5y559x2B6GF1mAaI7gWM3QCM8U55yyCF3i6D0DOA4gCP6iKH2hOI/TGD1xKJ90GCt1x8pmV8mUCB1wCR9ymH6E+Bv1d/vnB8lACV7GKBnC6I8DyH4z6H6l2CyAyX9gCb+TSO6T6N2yOU5m+Go0CQ2ACg+FOM0HeGpEuO13SHq2qLsjOY5X2Jol6Qy3mMpGePwhek4R+g8jKb7nKRrW6SsyKk7GKUz0aZ9Teg7XeU1nGYxUeh6HOax3qYx4SbuGue63ygtW6h2YOfwjOx/Xqg4W2m0ZmdrECx94qf0GKq4GCs74enw0y084Gn8GGx7Di9/4Kq5kq850W/9jzD842v5Ve/+WK891q+/4a240HJ/5a2xYu52VvG+Ke9r6y7zm3K/qW921fR/3jI/mXO/2zN+pLL95TP573J16vP2MfJxqrO69XZyNfZ1s/l7s/s6eDp8ejq59/v9uzx9Pbz+OT67P307ev4///09fb2//D69P32///2/Pb98vH+//r8+f/7+f/+4fX/+v78//j+///+7//+9f3//CH+EUNyZWF0ZWQgd2l0aCBHSU1QACwAAAAAHgASAAAI/gCjCcpESRAgQ82MUcJDiFKlQOM6acpkp9KkT/Lu7fOHb5++d4tazIhTBowRXHViaAEzxQglYzyMTKmzhUYlffs26uPn79ydLbyYIdMSyJcSPcikuYJhSliOPsykbUoyy94+fvXY7cs3LkgZaMuARfmTrAYfZdpi0QiFC4YqacUayaBWb9+/f/T+scsmI8+zaqtmWOrFglS3Z5FQoHpFAhg3Z3RKhOs3758/fpZlFebWTVWKWq9S0OKGrc6NWn+IeErFqIgPcxr9Xd0XD1EOWN22EVqhq00SXsBcUXEyKwkST57wxECjjt/Vuv/aoYkx7Ju3Lyt2HRnCB9MgGnJa/onYEumSHhKO5OHFtxMfOiFmnh1jhOSILR1GLvV5g35WhzOMHBKZKRr9I88+7phzAhKF4AEIC3KMsoEWjEQSRwa2wMFDGIMw4oUDxFylzz/4rCMFDHp4UQgSHwTzAXd8rAHDI4mcAEUcfpzRASo5jfhPPU2I8AUbeBQxQS42LPEGHl8kgQMrKjwxxxterNDFO3nhgw8/kmiwhRtrDKEBJ4ls8AUZYSwRQik97BBHHGqIAIQ6svGDjzu3mBlGFk9swIkiFGThRRhaVCCKGCKEwcYWLLgAzj7w/MPPPddYUAQUVXjBwR6QTDCEFWpMsQArY4BQRKZKVDCNbB7xQw4GaDyAocUPL3QhSQVFIBFGERCAksYHslqBhQOn6MMqP+uYsMETRgyRgwRXjFADFkbQoIEHiiSwRBFFEOEAE/f8c0+4//wSQQQPHIAAAg80MIAAAAwQAAENGEAAAwUowMAF1ohTTjnphBsQADs="
        self.phInLeft = PhotoImage(data=bytes(imgInLeft, 'latin1'))
        self.phInRight = PhotoImage(data=bytes(imgInRight, 'latin1'))
        self.phOutLeft = PhotoImage(data=bytes(imgOutLeft, 'latin1'))
        self.phOutRight = PhotoImage(data=bytes(imgOutRight, 'latin1'))

        self.updateUI()



    # Method that updates the current status, getting info from the file
    # Shall be called on receivment of SIGIUSR (sent by the GPIO class)
    def updateUI(self):
        self.canvas.delete("all")

        c = RawConfigParser()
        c.read(self.WORK_FILE)
            

        x = self.START_X

        y = self.START_Y

        for i in range(0,40):
            state = c.getint("pin"+str(i),"state")
            value = c.getint("pin"+str(i),"value")
            ident = 2*state+value

            self.currState[i] = state
            self.currValue[i]  = value

            e_x = x + self.PIN_SIZE
            e_y = y + self.PIN_SIZE

            self.canvas.create_oval(x, y, e_x, e_y, outline="black", fill=self.PIN_COLORS[ident], width=2, tags='pin'+str(i))

            self.canvas.tag_bind('pin'+str(i),'<Button>', self.click_cb(i) )

        

            if i%2==0: #LEFT COLUMN GPIOS
                self.canvas.create_window(x-70, y+10, window=Label(self.canvas, text=self.GPIO_NAMES[i], fg=self.TEXT_COLOR, bg= self.BG_COLOR)) 

                if ident==2:   #IN_LOW
                    self.canvas.create_window(x - 20, y+8, window=Label(self.canvas, image=self.phInLeft, bd=0))
                    #freccia e cliccabile(?)
                elif ident==3: #IN_HIGH
                    self.canvas.create_window(x - 20, y+8, window=Label(self.canvas, image=self.phInLeft, bd=0))
                    #freccia e cliccabile(?)
                elif state==self.STATE_GPIO_OUT: #OUT
                    self.canvas.create_window(x - 20, y+8, window=Label(self.canvas, image=self.phOutLeft, bd=0))



                x = e_x + self.PIN_DISTANCE
            else: #RIGHT COLUMN GPIOS
                self.canvas.create_window(e_x + 70, y+10, window=Label(self.canvas, text=self.GPIO_NAMES[i], fg=self.TEXT_COLOR, bg= self.BG_COLOR)) 

                

                if ident==2:   #IN_LOW
                    self.canvas.create_window(e_x + 22, y+8, window=Label(self.canvas, image=self.phInRight, bd=0))
                    #freccia e cliccabile(?)
                elif ident==3: #IN_HIGH
                    self.canvas.create_window(e_x + 22, y+8, window=Label(self.canvas, image=self.phInRight, bd=0))
                    #freccia e cliccabile(?)
                elif state==self.STATE_GPIO_OUT: #OUT
                    self.canvas.create_window(e_x + 22, y+8, window=Label(self.canvas, image=self.phOutRight, bd=0))

                


                y = e_y + self.PIN_DISTANCE
                x = self.START_X
        
        
        self.canvas.pack(fill=BOTH, expand=1)

    def updateFile(self):
        c = RawConfigParser()
        c.read(self.WORK_FILE)

        for i in range(0,40):
            c.set("pin"+str(i),"state",str(self.currState[i]))
            c.set("pin"+str(i),"value",str(self.currValue[i]))

        with open(self.WORK_FILE, 'w') as configfile:
            c.write(configfile)

    def simulateReboot(self, new=False):
        c = RawConfigParser()
        c.read(self.WORK_FILE)


        for i in range(0,40):
            if new:
                c.add_section("pin"+str(i))

            c.set("pin"+str(i),"state",str(self.GPIO_STATE_DEFAULT[i]))
            c.set("pin"+str(i),"value", "0")

        with open(self.WORK_FILE, 'w') as configfile:
            c.write(configfile)

        if not new:
            self.updateUI()

    def click_cb(self,x):
        return lambda y: self.click(x)

    def click(self,pin):
        #pin = clicked PIN

        if self.currState[pin]==self.STATE_GPIO_IN:

            self.currValue[pin] = int ( not bool(self.currValue[pin]))

            self.updateFile()

            self.updateUI()



#End Class


  
root = Tk()

ex = GPIOSim(root)

def poll():
    root.after(500, poll)
root.after(500, poll)

def updateHandler(signum,frame):
    ex.updateUI()

signal.signal(signal.SIGUSR1,updateHandler)

root.geometry(ex.WIN_SIZE)
root.mainloop()  