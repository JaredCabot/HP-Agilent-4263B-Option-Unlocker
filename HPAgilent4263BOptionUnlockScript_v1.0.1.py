# HP / Agilent 4263B Option Unlocker Script
# Near Far Media - v1.0.1 20240516
# License: MIT - https://opensource.org/license/MIT

import pyvisa  # For GPIB
import sys     # For exit
import time    # For sleep

print("---------------------------------------------------")
print("|    HP / Agilent 4263B Option Unlocker Script    |")
print("|        Near Far Media - v1.0.1 20240516         |")
print("---------------------------------------------------\n")
print("This script will automatically enable options 001")
print("and 002 on your HP / Agilent 4263B LCR Meter.\n")
print("Ensure you have 'Keysight IO Libraries Suite' installed")
print("if using a 83257B USB-GPIB adapter, or the National")
print("Instruments 'NI-488.2' software package installed if")
print("using an NI GPIB-USB-HS adapter.")
print("Other GPIB adapters may work, but I didn't check.")
print("Python 3 and PyVISA must also be installed.")
print("Ensure the 4263B is powered on, connected to the PC")
print("and visible in the respective software package.\n")
input("Press ENTER to continue.\n")

rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print("Discovered {} devices".format(len(resources)))
print(f"{resources}")
print("Ignoring non-GPIB devices\n")

# Variables for our search loop:
target_device_id = '4263B'  # Instrument to search for
is_found = False            # Whether or not the instrument is found
target_interface = 'GPIB'   # Interface to search for
inst_id = None              # Instrument (if found)

# Loop through the list of GPIB devices
for name in resources:
    if target_interface in name:
        print(f"Opening device: {name} ...")
        try:
            inst = rm.open_resource(name)         # Create instrument variable 'inst'
            inst_id = inst.query("*IDN?").strip() # Send command to request instrument ID string

            # Query details of connected instrument to find a match
            if target_device_id in inst_id:
                is_found = True
                break  # Break out of loop (stop searching)

        except:
            print("Instrument not connected!\n")

# The search loop is complete. Did we find it?
if not is_found:
    print(f"Error: Device {target_device_id} not found")
#    inst.close()
    rm.close()
    input("Press ENTER to exit.")
    sys.exit(1)  # Exit app with an error code

inst.timeout = 20000  # Global timeout for GPIB interface comms

print(f"Device {target_device_id} found\n")
inst_serial = inst_id.split(",")[2]
print(f"Serial Number = {inst_serial}")
inst_firmware = inst_id.split(",")[3]
print(f"Firmware Revision = {inst_firmware}")

if float(inst_firmware) < 1.06:
    print("*** This is an outdated firmware, upgrade to 1.06 is recommended ***")
inst_version = inst.query(":SYST:VERS?")
print(f"SCPI Version = {inst_version}")

# Check if options are already enabled and exit if so
inst_options = inst.query("*OPT?").strip()

print(f"Currently installed options: {inst_options}")

if inst_options == "001,002":
    print("Hooray! All options are already enabled!\n")
    print("Nothing more to do. Goodbye!")
    inst.write(":syst:beep")
    time.sleep(0.1)
    inst.write(":syst:beep")
    inst.close()
    rm.close()
    input("Press ENTER to exit.")
    sys.exit(0)

elif inst_options == "001":
    print("Option 002 not enabled...")

elif inst_options == "002":
    print("Option 001 not enabled...")

else:
    print("No options are enabled...")

# Send *RST reset command
print("\nResetting instrument...")
inst.write("*RST")
time.sleep(2)

# Send *TST? self test command
print("Instrument performing self test...")
try:
    inst_test = inst.query("*TST?")
except pyvisa.errors.VisaIOError as e:
    print(f"VISA IO Error: {e}")
    print("Please check GPIB connection to instrument and try again.")
    inst.close()
    rm.close()
    input("Press ENTER to exit.")
    sys.exit(1)

inst_error = int(inst_test)

# Don't proceed if self-test bad
if inst_error != 0:
    print("SELF TEST FAILED!")

    if inst_error & 1:  # Bit 1 set: RAM error
        print(f"Error code 1 - RAM")

    if (inst_error >> 1) & 1:  # Bit 2 set: EPROM error
        print(f"Error code 2 - EPROM")

    if (inst_error >> 2) & 1:  # Bit 3 set: Calibration error
        print(f"Error code 4 - Calibration data (EEPROM)")

    if (inst_error >> 3) & 1:  # Bit 4 set: User error
        print(f"Error code 8 - User's data (EEPROM)")

    if (inst_error >> 4) & 1:  # Bit 5 set: A/D error
        print(f"Error code 16 - A/D converter")

    if (inst_error >> 5) & 1:  # Bit 6 set: Backup error
        print(f"Error code 32 - Backup RAM")

    print("\nPlease repair instrument before proceeding.")
    inst.write(":syst:beep")
    time.sleep(0.1)
    inst.write(":syst:beep")
    time.sleep(0.1)
    inst.write(":syst:beep")
    time.sleep(0.1)
    inst.write(":syst:beep")
    inst.close()
    rm.close()
    input("Press ENTER to exit.")
    sys.exit(1)

print("Self test OK!\n")
inst.write(":syst:beep")
input("Ready to write option codes.\nPress ENTER to continue.")

try:
    inst.write(":SYST:KLOC ON") # Lock keypad to prevent imperial entanglements

    # Query existing memory locations for backup snapshot and print to screen
    print("Reading instrument memory before write for backup:")
    print("Memory start address: 1966144".format(
        inst.write(":TEST:MEM:ADDR 1966144")))

    for x in range(7):
        print("Read word: {}".format(inst.query(
            ":TEST:MEM:WORD?").replace("+", "").strip()))

except pyvisa.errors.VisaIOError as e:
    print(f"VISA IO Error: {e}")
    print("Please check GPIB connection to instrument and try again.")
    inst.close()
    rm.close()
    input("Press ENTER to exit.")
    sys.exit(1)

# ----Start of checksum magic----
# Special thanks to user Miek on eevblog.com forums for figuring this out!
# https://www.eevblog.com/forum/testgear/i_ve-got-a-hacking-challenge-for-you-guys!/msg4393006/#msg4393006
sn = bytes(inst_serial, "ascii")
yhp = b"YHP Kobe-Instrument-Division HP4263A.   "

result = [0] * 8

for i, c in enumerate(sn):
    u1 = (c * i) % 0x28
    for j in range(len(result)):
        u2 = (u1 % 0x28)
        result[j] += yhp[u2]
        u1 += 1

result = [(x % 0x5f) + 0x20 for x in result]
# ----End of checksum magic----

# Insert fixed values
result.insert(0, 0x31)  # 1st byte Enable option 001 (ascii "1") (Preceeding two zeroes are already set, so are ignored here)
result.insert(1, 0x00)  # 2nd byte (ascii "Null")
result.append(0x30)     # Last 3 bytes (ascii "0") to enable option 002
result.append(0x30)     # Last 3 bytes (ascii "0") to enable option 002
result.append(0x32)     # Last 3 bytes (ascii "2") to enable option 002
result.append(0x00)     # Last null to round out the last word

# Assemble fixed values and checksum into correct order of unsigned integers and write to instrument
words = [
    (result[0] << 8) + result[1],  # 0x3100 - Option 001 with null terminator written from EPROM address 0x20
    (result[2] << 8) + result[3],  # checksum
    (result[4] << 8) + result[5],  # checksum
    (result[6] << 8) + result[7],  # checksum
    (result[8] << 8) + result[9],  # checksum
    (result[10] << 8) + result[11],  # 0x3030 - Option 002 Written from EPROM address 0x2A
    (result[12] << 8) + result[13],  # 0x3200 - Option 002 with null terminator
]

print("\nWriting option 001 and 002 unlock codes to instrument:")
print("Memory start address: 1966144")

try:
    inst.write(":TEST:MEM:ADDR 1966144")

    for i, value in enumerate(words):
        inst.write(f":TEST:MEM:WORD {value}")
        print(f"Written word: {value}")

except pyvisa.errors.VisaIOError as e:
    print(f"VISA IO Error: {e}")
    print("**Connection was lost during write to EEPROM!**")
    print("This is recoverable, please check power and")
    print("GPIB connections and run the script again.")
    inst.close()
    rm.close()
    input("Press ENTER to exit.")
    sys.exit(1)

# Verify written values, if ok instruct user to reboot instrument, if not inform user of failure.
print("\nReading instrument memory addresses for verification...")

try:
    # set the address to start reading from
    inst.write(":TEST:MEM:ADDR 1966144")
    read_words = []  # Initialise an empty list
    for x in range(7):
        read_words.append(int(inst.query(":TEST:MEM:WORD?")))

except pyvisa.errors.VisaIOError as e:
    print(f"VISA IO Error: {e}")
    print("Please check GPIB connection to instrument and try again.")
    inst.close()
    rm.close()
    input("Press ENTER to exit.")
    sys.exit(1)

if words != read_words:
    print("Boo, Write unsuccessful.")
    print("\nCheck for faults and try again.")
    inst.write(":syst:beep")
    time.sleep(0.1)
    inst.write(":syst:beep")
    time.sleep(0.1)
    inst.write(":syst:beep")
    time.sleep(0.1)
    inst.write(":syst:beep")
    inst.close()
    rm.close()
    input("Press ENTER to exit.")
    sys.exit(1)

print("Hooray, write successful!")
print("\nPlease manually reboot instrument to activate enabled options.")
inst.write(":syst:beep")
time.sleep(0.1)
inst.write(":syst:beep")
inst.close()
rm.close()
input("Press ENTER to exit.")
print("\nSo long and thanks for all the fish.")
time.sleep(2)
sys.exit(0)
