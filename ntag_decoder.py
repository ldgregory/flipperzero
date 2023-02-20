#! /usr/bin/env python3

"""
Leif Gregory <leif@devtek.org>
NTAG-213 Data Decoder
Tested to Python v3.10.7

Consumes .nfc files as written by Flipper Zero and converts the hex to ASCII 
for all pages.

Changelog
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
    parser = argparse.ArgumentParser(description='NTAG Decoder')
    parser.add_argument('-i', type=str, help='Input filename', dest='inputFile')
    parser.add_argument('-v', action='version', version='%(prog)s 0.1', dest='version')
    args = parser.parse_args()

    if args.inputFile:
        data = ''
        bad_nibbles = []
        block_match = re.compile(r'^.*\:\s(.*)$')
        for x in range(0, 32):
            bad_nibbles.append(format(x, '02x').upper())

        with open(args.inputFile, 'r') as fh:
            for line in fh:
                if line.startswith('Page '):
                    match = re.match(block_match, line)
                    try:
                        for nibble in match[1].split(' '):
                            if nibble.upper() not in bad_nibbles:
                                data += bytes.fromhex(nibble).decode("ASCII") 
                    except:
                        pass

        print(data)


if __name__ == '__main__':
    main()
