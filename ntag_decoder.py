#! /usr/bin/env python3

"""
Leif Gregory <leif@devtek.org>
NTAG-NFC Data Decoder
Tested to Python v3.10.7

Consumes .nfc files as written by Flipper Zero and converts the hex to ASCII 
for relevant data pages.

Changelog
20230223 -  Refactor code a bit
20230222 -  Clean up code
20230219 -  Initial Code

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
from sys import exit

def main():
    parser = argparse.ArgumentParser(description='NTAG NFC Decoder')
    parser.add_argument('-i', type=str, help='Input filename', dest='inputFile')
    parser.add_argument('-v', action='version', version='%(prog)s 0.1', dest='version')
    args = parser.parse_args()

    if args.inputFile:
        block_match = re.compile(r'^Page\s(\d{1,2}):\s(.*)$')
        data = ''

        with open(args.inputFile, 'r') as fh:
            for line in fh:
                if match := re.match(block_match, line):
                    if int(match[1]) > 6:  # Data starts on page 7
                        for nibble in match[2].split(' '):
                            if nibble != 'FE':  # End of data marked by FE
                                try:
                                    data += bytes.fromhex(nibble).decode("ascii")
                                except:
                                    pass  # Non-ASCII character, move on
                            else:
                                print(data)
                                exit()
    else:
        print('Please specify a file to decode')


if __name__ == '__main__':
    main()
