#! /usr/bin/env python3

"""
Leif Gregory <leif@devtek.org>
20230115
MIFARE Classic EV1 1K Access Rights Decoder
Tested to Python v3.10.7

Takes user input for bytes 6, 7 and 8 from block 3 of a Sector Trailer of a 
MiFare Classic 1K card and decodes the Sector Trailer and data block access 
rights.

Block 3 (Sector Trailer) showing byte positions for Key A, Key B and Access.
Position 9 is user defined and has nothing to do with Access Bits.
+-----------------------------+--------------+----+-----------------------------+
|  0 |  1 |  2 |  3 |  4 |  5 |  6 |  7 |  8 |  9 | 10 | 11 | 12 | 13 | 14 | 15 |
+-----------------------------+--------------+----+-----------------------------+
|            Key A            | Access Bits  | GP |            Key B            |
|          (6 bytes)          |  (3 bytes)   | B  |          (6 bytes)          |
+-----------------------------+--------------+----+-----------------------------+

Deriving C1, C2, C3. _# denotes block, "n" denotes compliment bit positions.
        +-------+-------+-------+-------+-------+-------+-------+-------+
        | Bit 7 | Bit 6 | Bit 5 | Bit 4 | Bit 3 | Bit 2 | Bit 1 | Bit 0 |
        +-------+-------+-------+-------+-------+-------+-------+-------+
Byte 6: | nC2_3 | nC2_2 | nC2_1 | nC2_0 | nC1_3 | nC1_2 | nC1_1 | nC1_0 |
        +-------+-------+-------+-------+-------+-------+-------+-------+
Byte 7: |  C1_3 |  C1_2 |  C1_1 |  C1_0 | nC3_3 | nC3_2 | nC3_1 | nC3_0 |
        +-------+-------+-------+-------+-------+-------+-------+-------+
Byte 8: |  C3_3 |  C3_2 |  C3_1 |  C3_0 |  C2_3 |  C2_2 |  C2_1 |  C2_0 |
        +-------+-------+-------+-------+-------+-------+-------+-------+

Changelog
20230115 -  Initial Code
20230116 -  Added regex sanity check
            Added commenting
"""

import re

def break_out_db_access(block, access_bits):
    """Prints out the data block access rights

    Parameters
    ----------
    block : str
        The Data Block we're showing access permissions for
    access_bits : str
        The C1, C2 and C3 bits as 3 bit binary string    

    Returns
    -------
    True
        As this function only prints, it just returns true
    """

    sector_trailer_access = {"000": "Never,Key A,Key A,Never,Key A,Key A,Key A is able to read Key B", \
                            "010": "Never,Never,Key A,Never,Key A,Never,Key A is able to read key B" , \
                            "100": "Never,Key B,Key A|B,Never,Never,Key B,", \
                            "110": "Never,Never,Key A|B,Never,Never,Never,", \
                            "001": "Never,Key A,Key A,Key A,Key A,Key A,Key A is able to read Key B", \
                            "011": "Never,Key B,Key A|B,Key B,Never,Key B,", \
                            "101": "Never,Never,Key A|B,Key B,Never,Never,", \
                            "111": "Never,Never,Key A|B,Never,Never,Never,"}

    data_block_access = {"000": "key A|B,key A|B,key A|B,key A|B,Transport", \
                        "010": "key A|B,never,never,never,Read/Write Block", \
                        "100": "key A|B,key B,never,never,Read/Write Block", \
                        "110": "key A|B,key B,key B,key A|B,Value Block", \
                        "001": "key A|B,never,never,key A|B,Value Block", \
                        "011": "key B,key B,never,never,Read/Write Block", \
                        "101": "key B,never,never,never,Read/Write Block", \
                        "111": "never,never,never,never,Read/Write Block"}

    if block == "3":  # Sector Trailer needs special handling
        # Break out the Sector Trailer access from the dictionary
        access = []
        for x in sector_trailer_access[access_bits].split(","):
            access.append(x)

        # Printing block 3 Sector Trailer access rights
        print(f"Read Key A:\t\t{access[0]}")
        print(f"Write Key A:\t\t{access[1]}")
        print(f"Read Data Block:\t{access[2]}")
        print(f"Write Data Block:\t{access[3]}")
        print(f"Read Key B:\t\t{access[4]}")
        print(f"Write Key B:\t\t{access[5]}")
        print(f"Warning:\t\t{access[6] if access[6] != '' else 'None'}")
    else:  # Blocks 0-2
        # Breaking out the block access rights from the dictionary into an array
        access = []
        for x in data_block_access[access_bits].split(","):
            access.append(x)
        
        # Printing the respective block access rights
        print(f"Read block:\t\t{access[0]}")
        print(f"Write block:\t\t{access[1]}")
        print(f"Increment block:\t{access[2]}")
        print(f"D/T/R block:\t\t{access[3]}")
        print(f"Application:\t\t{access[4]}")
    
    return 1


def hex2bin(hex_values):
    """Take 6 char hex and split into array of bytes, convert to bin and return 
    dict of binary string values indexed by the byte position in Sector Trailer.

    Parameters
    ----------
    hex_values : str
        User entered 6 char hex string (already validated by regex)

    Returns
    -------
    dict
        Key = byte placeholder (6, 7, or 8)
        Value = byte as binary string
    """

    bin_values = {}  # Dict to hold converted hex values
    ctr = 6  # Start with byte 6 and end with byte 8
    
    # Take 6 char hex and split into array of bytes
    for hex in re.findall('..', hex_values):
        bin_values[ctr] = (str("{0:08b}".format(int(hex, 16))))
        ctr += 1
    
    return bin_values


def validate_access_bits(bits):
    """Verify Compliment Checksums as follows:
    C1: Byte 7 bits 0-3 with compliment of byte 6 bits 4-7
    C2: Byte 8 bits 4-7 with compliment of byte 6 bits 0-3
    C3: Byte 8 bits 0-3 with compliment of byte 7 bits 4-7

    Parameters
    ----------
    bits : str
        Binary string of hex values converted by hex2bin

    Returns
    -------
    boolean
        True if all compliment checksums are correct
        False if there is a compliment checksum failure
    """

    # C1 - Checking if the last four bits of byte 6 are compliment to first four bits of byte 7
    if bits[7][:4] != ''.join('1' if x == '0' else '0' for x in bits[6][4:8]):
        print("Something incorrect in byte 7 or 6")
        return 0
    # C2 - Checking if the first four bits of byte 6 are compliment to last four bits of byte 8
    elif bits[8][4:8] != ''.join('1' if x == '0' else '0' for x in bits[6][:4]):
        print("Something incorrect in byte 8 or 6")
        return 0
    # C3 - Checking if the last four bits of byte 7 are compliment to first four bits of byte 8
    elif bits[8][:4] != ''.join('1' if x == '0' else '0' for x in bits[7][4:8]):
        print("Something incorrect in byte 8 or 7")
        return 0
    else:
        return 1


def main():
    # Get user input
    hex_rights = input("From byte positions 6, 7 and 8 of block 3\nHex rights (like FF0780): ")

    # Make sure we get three valid hex values (like FF0780)
    if re.search('^[A-Fa-f0-9]{6}$', hex_rights):
        # Convert user input hex values to binary strings with sanity checking
        bin_bytes = hex2bin(hex_rights)

        # Make sure checksums are right and we have a valid set of access bytes
        if validate_access_bits(bin_bytes):
            # Get C1, C2 and C3 for each data block access
            db0_access = bin_bytes[7][3] + bin_bytes[8][7] + bin_bytes[8][3]  # Block 0
            db1_access = bin_bytes[7][2] + bin_bytes[8][6] + bin_bytes[8][2]  # Block 1
            db2_access = bin_bytes[7][1] + bin_bytes[8][5] + bin_bytes[8][1]  # Block 2
            db3_access = bin_bytes[7][0] + bin_bytes[8][4] + bin_bytes[8][0]  # Sector Trailer

            # Show C1, C2 and C3 access bits for each block
            print("\n\nAccess Bits (C1,C2,C3):")
            print("---------------------------")
            print(f"Block 0:\t\t{db0_access}")
            print(f"Block 1:\t\t{db1_access}")
            print(f"Block 2:\t\t{db2_access}")
            print(f"Block 3:\t\t{db3_access} (Sector Trailer)")

            # Show the block access rights
            print("\nAccess Rights:")
            print("-------------------------------")
            print("Block 0")
            break_out_db_access("0", db0_access)
            print("\nBlock 1")
            break_out_db_access("1", db1_access)
            print("\nBlock 2")
            break_out_db_access("2", db2_access)
            print("\nBlock 3 (Sector Trailer)")
            break_out_db_access("3", db3_access)

    else:
        print("ERROR: Invalid. A valid entry would look like FF0780")

if __name__ == '__main__':
    main()
