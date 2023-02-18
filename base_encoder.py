#! /usr/bin/env python3

"""
Leif Gregory <leif@devtek.org>
Base Encoder
Tested to Python v3.10.7


Changelog
20230218 -  A little more handling of unprintable chars
20230208 -  Reworked all the code to support better column formatting and moved
            the printing outside of the function for importing as a module.
         -  Commented out BCD code. No good way to print that nicely.
20230201 -  Formatting of column data output
20230128 -  Sanity checking for inputs
20230127 -  Bug fixes with chars and inverted chars
20230125 -  Initial Code

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import re
import sys


def convert(tracking, encodings):
    """
    Summary:
    Takes decimal input via tracking["decimal"] and performs a number of 
    conversions to other bases and stores them in a nested array called 
    encodings.

    tracking (dict):
        - decimal      (int)    : The input in decimal to perform conversions
        - column_width (int)    : Running integer of len() of longest binary
        - counter      (int)    : Simple counter to track how many times this function is called

    encodings (nested dict):
        - decimal      (int)    : Copied from tracking['decimal']
        - decimal_inv  (int)    : Decimal conversion of binary_inv
        - binary       (str)    : Binary conversion of decimal
        - binary_inv   (str)    : Inverse of binary
        - hex          (str)    : Hexadecimal conversion of decimal
        - hex_inv      (str)    : Hexadecimal conversion of decimal_inv
        - oct          (str)    : Octal conversion of decimal
        - oct_inv      (str)    : Octal conversion of binary_inv
        - char         (str)    : ASCII character of decimal (with limitations)
        - char_inv     (str)    : ASCII character of decimal_inv (with limitations)
        - bcd          (str)    : BCD of decimal
        - bcd_inv      (str)    : BCD of decimal_inv

    Returns:
    dict: tracking
    dict: encodings
    """

    if tracking["decimal"] != '':
        ctr = tracking["counter"]  # Create a shorter variable for use below

        # We need to do this to create the nested dictionaries for each input
        encodings.setdefault(ctr, {})["decimal"] = tracking["decimal"]

        # Convert to binary and inverse
        encodings[ctr]["binary"] = format(encodings[ctr]["decimal"], '08b')
        encodings[ctr]["binary_inv"] = ''.join('1' if x == '0' else '0' for x in encodings[ctr]["binary"])

        # Convert to decimal inverse
        encodings[ctr]["decimal_inv"] = int(encodings[ctr]["binary_inv"], 2)

        # Convert to hexadecimal and inverse
        encodings[ctr]["hex"] = format(encodings[ctr]["decimal"],'02x').upper()
        encodings[ctr]["hex_inv"] = format(encodings[ctr]["decimal_inv"],'02x').upper()

        # Convert to octal and inverse
        encodings[ctr]["octal"] = format(encodings[ctr]["decimal"],'03o').upper()
        encodings[ctr]["octal_inv"] = format(encodings[ctr]["decimal_inv"],'03o').upper()
        
        # Convert to ASCII char and inverse and replace unprintable chars
        if encodings[ctr]["decimal"] in range(32, 128) or encodings[ctr]["decimal"] in range(161,256):
            # Take care of a few unprintables within ranges
            if encodings[ctr]["decimal"] == 32:
                encodings[ctr]["char"] = 'space'
            elif encodings[ctr]["decimal"] == 127:
                encodings[ctr]["char"] = 'delete'
            elif encodings[ctr]["decimal"] == 173:
                encodings[ctr]["char"] = 's.hyphen'  # soft hyphen
            else:
                encodings[ctr]["char"] = chr(encodings[ctr]["decimal"])
        else:
            encodings[ctr]["char"] = "xxx"  # Replace problem chars

        if encodings[ctr]["decimal_inv"] in range(32, 136) or encodings[ctr]["decimal_inv"] in range(160,256):
            encodings[ctr]["char_inv"] = chr(encodings[ctr]["decimal_inv"])
        else:
            encodings[ctr]["char_inv"] = "xxx"  # Replace problem chars
        
        # Leaving BCD stuff here as it works, but the printing of it is problematic
        # depending on user input affecting column widths.

        # # Convert to BCD and inverse
        # encodings["bcd"] = ""
        # encodings["bcd_inv"] = ""
        # for digit in str(encodings["decimal"]):
        #     encodings["bcd"] += f" {format(int(digit), '04b')}"
        # encodings["bcd"] = encodings["bcd"].strip()
        # for digit in str(encodings["decimal_inv"]):
        #     encodings["bcd_inv"] += f" {format(int(digit), '04b')}"
        # encodings["bcd_inv"] = encodings["bcd_inv"].strip()

        # Set dynamic column width based on length of binary
        if len(encodings[ctr]["binary"]) > tracking["column_width"]:
            tracking["column_width"] = len(encodings[ctr]["binary"])
    else:
        print("Whoops, no decimal was passed")
    
    return tracking, encodings


def main():
    parser = argparse.ArgumentParser(description='Base converter')
    parser.add_argument('-a', type=str, help='Input is BCD', dest='bcd')
    parser.add_argument('-b', type=str, help='Input is binary', dest='binary')
    parser.add_argument('-c', type=str, help='Input in character', dest='char')
    parser.add_argument('-d', type=str, help='Input is decimal', dest='decimal')
    parser.add_argument('-x', type=str, help='Input in hexidecimal', dest='hex')
    parser.add_argument('-o', type=str, help='Input in octal', dest='octal')
    parser.add_argument('-v', action='version', version='%(prog)s 1.0', dest='version')
    args = parser.parse_args()

    # Init dictionary for all encoding data and set up some tracking parameters
    # column_width is critical for proper printing of columns, counter is only
    # used to report how many conversions were done.
    tracking = {"counter": 1, "column_width": 1}
    encodings = {}

    # Sanity check input
    if args.binary:
        # Binary of any length with or without spaces
        if re.match('^[0-1 ]+$', args.binary):
            inputs = args.binary
        else:
            print('Invalid binary input')
            sys.exit()
    elif args.bcd:
        # Binary as four bits with or without spaces
        if re.match('^([0-1]{4}\s?)+$', args.bcd):
            # Checking to see if it's a four bit chunk, if not, make it so
            if len(args.bcd) > 4 and ' ' not in args.bcd:
                temp = ' '.join(re.findall('....', args.bcd))
                args.bcd = temp
            
            # All good now, let's convert to decimal
            inputs = ""
            for bincode in args.bcd.split(' '):
                # Make sure no four BCD bits converts to > 9
                if int(bincode, 2) <= 9:
                    inputs += str(int(bincode, 2))
                else:
                    print('Invalid bcd input')
                    sys.exit()
        else:
            print('Invalid bcd input')
            sys.exit()
    elif args.char:
        # Strip any spaces then separate each char with space
        temp = args.char.replace(' ', '')
        inputs = ' '.join(x for x in temp)
    elif args.decimal:
        if re.match('^[0-9 ]+$', args.decimal):
            inputs = args.decimal
        else:
            print('Invalid decimal input')
            sys.exit()
    elif args.hex:
        # One hex byte or multiple hex bytes separated by spaces
        if re.match('^([0-9a-fA-F]{1,2}\s?)+$', args.hex):
            inputs = args.hex 
        else:
            print('Invalid Hex input')
            sys.exit()                           
    elif args.octal:
        # Octal number with or without spaces
        if re.match('^[0-7 ]+$', args.octal):
            inputs = args.octal
        else:
            print('Invalid octal input')
            sys.exit()

    # Convert input(s) into decimal as a starting place for all encodings
    for element in inputs.split(" "):
        if args.binary:
            tracking["decimal"] = int(element, 2)
        elif args.bcd:
            tracking["decimal"] = int(element)
        elif args.char:
            tracking["decimal"] = ord(element)
        elif args.decimal:
            tracking["decimal"] = int(element)
        elif args.hex:
            tracking["decimal"] = int(element, 16)
        elif args.octal:
            tracking["decimal"] = int(element, 8)

        # Make the magic happen
        tracking, encodings = convert(tracking, encodings)
        tracking['counter'] += 1

    # Done with all inputs, let's print it out
    cw = tracking["column_width"] + 1  # shorter variable for use below
    
    print(f'{"Hex":<{cw}}{"Dec":<{cw}}{"Oct":<{cw}}{"Char":<{cw}}{"Bin":<{cw}}{"nBin":>{cw}}{"nChar":>{cw}}{"nOct":>{cw}}{"nDec":>{cw}}{"nHex":>{cw}}')
    
    for row in encodings:
        print(f'{encodings[row]["hex"] :<{cw}}', end='')
        print(f'{encodings[row]["decimal"] :<{cw}}', end='')
        print(f'{encodings[row]["octal"] :<{cw}}', end='')
        print(f'{encodings[row]["char"] :<{cw}}', end='')
        print(f'{encodings[row]["binary"] :<{cw}}', end='')
        print(f'{encodings[row]["binary_inv"] :>{cw}}', end='')
        print(f'{encodings[row]["char_inv"] :>{cw}}', end='')
        print(f'{encodings[row]["octal_inv"] :>{cw}}', end='')
        print(f'{encodings[row]["decimal_inv"] :>{cw}}', end='')
        print(f'{encodings[row]["hex_inv"] :>{cw}}')

        # Leaving BCD stuff here as it works, but the printing of it is problematic
        # depending on user input affecting column widths.
        # print(f'\nBCD: \t {encodings["bcd"]}')
        # print(f'BCD_Inv: {encodings["bcd_inv"]}\n')
    print(f'\n{(tracking["counter"] - 1) * 10} encodings completed.')


if __name__ == '__main__':
    main()
