#! /usr/bin/env python3

"""
Leif Gregory <leif@devtek.org>
NTAG-NFC Data Decoder
Tested to Python v3.10.7

Consumes .nfc files as written by Flipper Zero and converts the hex to ASCII 
for relevant data pages.

Changelog
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

def main():
    parser = argparse.ArgumentParser(description='NTAG NFC Decoder')
    parser.add_argument('-i', type=str, help='Input filename', dest='inputFile')
    parser.add_argument('-v', action='version', version='%(prog)s 0.1', dest='version')
    args = parser.parse_args()

    if args.inputFile:
        block_match = re.compile(r'^.*\:\s(.*)$')
        data = ''
        last_nibble = ''
        page = 0
        stop_collecting = 0

        with open(args.inputFile, 'r') as fh:
            for line in fh:
                if line.startswith('Page '):
                    if page > 6:  # The data we're after starts on page 6
                        match = re.match(block_match, line)
                        for nibble in match[1].split(' '):
                            if f'{last_nibble}{nibble}' == 'FE00':
                                stop_collecting = 1
                            if stop_collecting != 1:
                                try:
                                    data += bytes.fromhex(nibble).decode("ascii")
                                except:
                                    pass
                            last_nibble = nibble
                    page += 1
        print(data)
    else:
        print('Please specify a file to decode')


if __name__ == '__main__':
    main()
