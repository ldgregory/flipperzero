#! /usr/bin/env python3

"""
Leif Gregory <leif@devtek.org>
MIFARE Classic EV1 1K Data Decoder
Tested to Python v3.10.7

Consumes .nfc files as written by Flipper Zero and does some base conversions
in the hopes that it produces something decipherable. I only had a couple
sample cards to work with. One where I didn't have all block data and another
where I did, but it didn't follow the nxp standard i.e. used data bytes for
data with no checksum inversions.

For more information on MIFARE Classic EV1 1K cards
https://www.nxp.com/docs/en/data-sheet/MF1S50YYX_V1.pdf

Changelog
20230121 -  Initial Code

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
from base_encoder import convert
from pprint import pprint

def main():
    parser = argparse.ArgumentParser(description='M1K Data Decoder')
    parser.add_argument('-i', type=str, help='Input filename', dest='inputFile')
    parser.add_argument('-o', type=str, help='Output filename', dest='outputFile')
    parser.add_argument('-d', help='Display all stored TOTP codes', action='store_true', dest='totpDecrypt')
    parser.add_argument('-v', action='version', version='%(prog)s 0.1', dest='version')
    args = parser.parse_args()

    # Init dictionary for all encoding data and set up some tracking parameters
    tracking = {"counter": 1, "column_width": 1}
    encodings = {}

    if args.inputFile:
        sector_ctr = 0  # Keep track of what sector we're on 0-15
        block_ctr = 0  # Keep track of what block we're on 0-3
        block_data = {}  # Collect block data as block_data[sector][block]
        block_match = re.compile(r'^.*\:\s(.*)$')

        # Build an array with only lines that start with Block
        with open(args.inputFile, 'r') as fh:
            for line in fh:
                if line.startswith('Block '):
                    match = re.match(block_match, line)
                    block_data.setdefault(sector_ctr, {})[block_ctr] = match[1]

                    if block_ctr == 3:
                        sector_ctr += 1
                        block_ctr = 0
                    else:
                        block_ctr += 1

    for sector in block_data:
        for block in block_data[sector]:
            # Get Manufacturer UID - Based on 7 byte right now
            if sector == 0 and block == 0:
                tracking["uid"] = block_data[sector][block][:11]
                tracking["bcc"] = block_data[sector][block][12:14]
                tracking["sak"] = block_data[sector][block][15:17]
                tracking["atqa"] = block_data[sector][block][18:23]
                tracking["manufacturer_data"] = block_data[sector][block][24:]

            if block != 3:
                # Grab the first four bytes including spaces (11 chars)
                data = block_data[sector][block][:11]

                # Only process first four if they aren't all zeros
                if not re.match('^(00\s?){4}$', data):
                    track_calc_checksum = ''

                    for element in data.split(' '):
                        ctr = tracking["counter"]  # Shorter variable for use below
                        tracking["decimal"] = int(element, 16)
                        tracking, encodings = convert(tracking, encodings)

                        encodings[ctr]["sb"] = f"{sector}:{block}"
                        encodings[ctr]["card_checksum"] = block_data[sector][block][12:23]
                        
                        # Keep track of inverted hex for checksum validation
                        track_calc_checksum += f'{encodings[ctr]["hex_inv"]} '

                        tracking["counter"] += 1
                    encodings[ctr]["calc_checksum"] = track_calc_checksum
    
    cw = tracking["column_width"]  # Shorter variable name for use below
    print(f'{"S:B":<{cw}}{"Hex":<{cw}}{"Dec":<{cw}}{"Oct":<{cw}}{"Char":<{cw}}{"Bin":<{cw}}{"nBin":>{cw}}{"nChar":>{cw}}{"nOct":>{cw}}{"nDec":>{cw}}{"nHex":>{cw}}')
    
    block_ctr = 1
    row_ctr = 1
    
    for row in encodings:
        if block_ctr <= 4:
            print(f'{encodings[row]["sb"] :<{cw}}', end='')
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
            if block_ctr == 4:
                print(f'Card Checksum: {encodings[row]["card_checksum"]}')
                print(f'Calc Checksum: {encodings[row]["calc_checksum"].strip()} {"MISMATCH" if encodings[row]["card_checksum"] != encodings[row]["calc_checksum"] else ""}\n')
                block_ctr = 1
                if row_ctr < len(encodings):
                    print(f'{"S:B":<{cw}}{"Hex":<{cw}}{"Dec":<{cw}}{"Oct":<{cw}}{"Char":<{cw}}{"Bin":<{cw}}{"nBin":>{cw}}{"nChar":>{cw}}{"nOct":>{cw}}{"nDec":>{cw}}{"nHex":>{cw}}')
            else:
                block_ctr += 1
        row_ctr += 1
            
    print(f'UID: {tracking["uid"]}')
    print(f'UID BCC: {tracking["bcc"]}')
    print(f'SAK: {tracking["sak"]}')
    print(f'ATQA: {tracking["atqa"]}')
    print(f'Manufacturer Data: {tracking["manufacturer_data"]}')


if __name__ == '__main__':
    main()
