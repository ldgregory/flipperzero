# flipperzero
Random stuff for F0



## Base_Encoder
Convert to and from multiple bases

I started this as part of a project to decode Mifare Classic 1K EV1 card data and decided to rip it out and make it standalone code that can be imported as a module.

### Encodings:
```
Binary Coded Decimal (BCD) - base_encoder.py -a '0110'
Binary                     - base_encoder.py -b '10110011'
Character                  - base_encoder.py -c 'G'
Decimal                    - base_encoder.py -d '12345'
Hexadecimal                - base_encoder.py -x 'DEADBEEF'
Octal                      - base_encoder.py -o '734'
```

Each input can have multiple inputs, such as '0110 0011 0101' or 'Cattle' or 'FF 07 80'. With exception to BCD, anything separated by a space will be treated as a different input than the one before or after it.

It will also negate the input encodings as well. e.g. 11110000 negated is 00001111.

### Some sample inputs/outputs:
```
python3 ./base_encoder.py -a '0100 0111 0110'
Hex       Dec       Oct       Char      Bin             nBin     nChar      nOct      nDec      nHex
1DC       476       734       xxx       111011100  000100011         #        43        35        23

BCD:     0100 0111 0110
BCD_Inv: 0011 0101

11 encodings completed.
```

```
python3 ./base_encoder.py -b '01000111 0110111'
Hex      Dec      Oct      Char     Bin           nBin    nChar     nOct     nDec     nHex
47       71       107      G        01000111  10111000        ¸      270      184       B8
37       55       67       7        00110111  11001000        È      310      200       C8

BCD:     0101 0101
BCD_Inv: 0010 0000 0000

22 encodings completed.
```

```
python3 ./base_encoder.py -c 'Face'
Hex      Dec      Oct      Char     Bin           nBin    nChar     nOct     nDec     nHex
46       70       106      F        01000110  10111001        ¹      271      185       B9
61       97       141      a        01100001  10011110      xxx      236      158       9E
63       99       143      c        01100011  10011100      xxx      234      156       9C
65       101      145      e        01100101  10011010      xxx      232      154       9A

BCD:     0001 0000 0001
BCD_Inv: 0001 0101 0100

44 encodings completed.
```

```
python3 ./base_encoder.py -d '42'
Hex      Dec      Oct      Char     Bin           nBin    nChar     nOct     nDec     nHex
2A       42       52       *        00101010  11010101        Õ      325      213       D5

BCD:     0100 0010
BCD_Inv: 0010 0001 0011

11 encodings completed.
```

```
python3 ./base_encoder.py -x 'FF 07 80'
Hex      Dec      Oct      Char     Bin           nBin    nChar     nOct     nDec     nHex
FF       255      377      ÿ        11111111  00000000      xxx        0        0        0
7        7        7        xxx      00000111  11111000        ø      370      248       F8
80       128      200               10000000  01111111               177      127       7F

BCD:     0001 0010 1000
BCD_Inv: 0001 0010 0111

33 encodings completed.
```

```
python3 ./base_encoder.py -o '775'
Hex       Dec       Oct       Char      Bin             nBin     nChar      nOct      nDec      nHex
1FD       509       775       xxx       111111101  000000010       xxx         2         2         2

BCD:     0101 0000 1001
BCD_Inv: 0010

11 encodings completed.
```


## M1K_Access_Decoder
Simple script to decode the block access rights of a MIFARE 1K RFID card. You can read up on the specification here:
https://www.nxp.com/docs/en/data-sheet/MF1S50YYX_V1.pdf

Takes user input for bytes 6, 7 and 8 from block 3 of a Sector Trailer of a MiFare Classic 1K EV1 card and decodes the Sector Trailer and Data Block access 
rights.

Input
```
From byte positions 6, 7 and 8 of block 3
Hex rights (like FF0780): FF0780
```

Output
```
Access Bits (C1,C2,C3):
---------------------------
Block 0:                000
Block 1:                000
Block 2:                000
Block 3:                001 (Sector Trailer)

Access Rights:
-------------------------------
Block 0
Read block:             key A|B
Write block:            key A|B
Increment block:        key A|B
D/T/R block:            key A|B
Application:            Transport

Block 1
Read block:             key A|B
Write block:            key A|B
Increment block:        key A|B
D/T/R block:            key A|B
Application:            Transport

Block 2
Read block:             key A|B
Write block:            key A|B
Increment block:        key A|B
D/T/R block:            key A|B
Application:            Transport

Block 3 (Sector Trailer)
Read Key A:             Never
Write Key A:            Key A
Read Data Block:        Key A
Write Data Block:       Key A
Read Key B:             Key A
Write Key B:            Key A
Warning:                Key A is able to read Key B

```
