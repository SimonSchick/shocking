from binascii import unhexlify, hexlify
from datetime import datetime, timedelta
from rflib import RfCat, MOD_2FSK, SYNCM_CARRIER_16_of_16

def crc8(hex_data):
    msg = bytearray(hex_data)
    check = 0xFF
    for i in msg:
        check = _add_crc8(i, check)
    return check

def _add_crc8(b, crc):
    if (b < 0):
        b += 256
    for i in range(8):
        odd = ((b^crc) & 1) == 1
        crc >>= 1
        b >>= 1
        if (odd):
            crc ^= 0x8C # this means crc ^= 140
    return crc

PREAMBLE = unhexlify('5464d2')

CMD_SHOCK = 0b11
CMD_BEEP  = 0b01
CMD_BUZZ  = 0b10

TARGET_A  = 0b00
TARGET_B  = 0b01
TARGET_AB = 0b10

class ShockController:
        def __init__(self):
                d = RfCat()

                d.setFreq(915000000)
                d.setPktPQT(100)
                d.makePktFLEN(9)
                d.setMdmDRate(2400)
                d.setMdmSyncWord(0b1010101000110011) # 0xAA33
                d.setMdmModulation(MOD_2FSK)
                d.setMdmSyncMode(SYNCM_CARRIER_16_of_16)
                d.setMaxPower()
                self.d = d
                self.cmdCounter = 0

        def buildPkt(self, device, cmd, level=0, target=TARGET_A):
                self.cmdCounter += 1
                if cmdCounter > 0xFF:
                        CMD_ID = 0

                cmd = int(cmd)
                target = int(target)
                level = int(level)

                if cmd == CMD_BEEP:
                        level = 0

                if cmd > 0b11 or cmd < 0b00:
                        raise ValueError('CMD invalid')

                if target > 0b11 or target < 0b00:
                        raise ValueError('TARGET invalid')

                if level < 0 or level > 100:
                        raise ValueError('LEVEL invalid')

                pkt = device + chr(level) + chr(cmd << 4 | target << 2) + chr(CMD_ID)
                return PREAMBLE + pkt + chr(crc8(pkt))

        def sendFor(self, device, mode, duration, level, target=TARGET_A):
                endTime = datetime.now() + timedelta(milliseconds=duration)
                pkt = self.buildPkt(mode, device, level, target)
                while datetime.now() <= endTime:
                        d.RFxmit(pkt)