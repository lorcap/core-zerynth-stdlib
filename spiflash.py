"""
.. module:: spiflash

********
SpiFlash
********

This modules handles operations on a generic Spi Flash Memory.
The following operations are allowed:

    * read/write data;
    * check if flash is busy;
    * enable write operations;
    * erase sector;
    * erase chip.

    """

import spi

SERIAL_FLASH_CMD_RDID  = 0x9F
SERIAL_FLASH_CMD_READ  = 0x03
SERIAL_FLASH_CMD_WRITE = 0x02
SERIAL_FLASH_CMD_WREN  = 0x06
SERIAL_FLASH_CMD_RDSR  = 0x05
SERIAL_FLASH_CMD_ERASE = 0xC7
SERIAL_FLASH_CMD_EWSR  = 0x06
SERIAL_FLASH_CMD_WRSR  = 0x01
SERIAL_FLASH_CMD_SER   = 0xD8

def _parse_addr(addr,n):
    print('spiflash:_parse_addr:', addr, type(addr), n)
    if type(addr) == PBYTEARRAY:
        return addr
    res = bytearray(n)
    for i in range(n):
        res[n-i-1] = addr & 0xff
        addr = (addr >> 8)
    return res

def _to_addr(barray):
    res = 0
    for b in barray:
        res = ((res << 8) + b)
    return res

class SpiFlash(spi.Spi):
    """
==============
SpiFlash class
==============

.. class:: SpiFlash(drvname, cs, clock=1000000)

        Initialize an external Flash memory specifying its:

            * MCU SPI circuitry *drvname* (one of SPI0, SPI1, ... check pinmap for details);
            * chip select pin *cs*;
            * clock *clock*, default at 1MHz.

    """

    def __init__(self, drvname, cs, clock=1000000):
        spi.Spi.__init__(self, cs, drvname, clock=clock)

        self._cs = cs

        self._init_flash()

    def _init_flash(self):
        self.start()

        self.unselect()

        self.write_enable()

    def _write_and_wait(self, pkt):
        print('spiflash:_write_and_wait')
        self.select()
        self.write(pkt)
        self.unselect()

        cnt=0
        while self.is_write_busy() and cnt<1000:
            sleep(1)
            cnt+=1
        if cnt>=1000:
            raise TimeoutError

    def __getitem__(self, key):
        return self.read_data(key[0],key[1]-key[0])

    def __setitem__(self, addr, data):
        self.write_data(addr, data)

    def write_enable(self):
        """
.. method:: write_enable()

        Enable write operations.
        Automatically called by :meth:`write_data`, :meth:`erase_sector`, :meth:`chip_erase` methods.

        """
        print('spiflash:write_enable')
        pkt = bytearray(1)
        pkt[0] = SERIAL_FLASH_CMD_WREN
        self.select()
        self.write(pkt)
        self.unselect()

    def is_write_busy(self):
        """
.. method:: is_write_busy()

        Returns 1 or 0 depending on whether the Flash is busy or not.

        """
        pkt = bytearray(2)
        pkt[0] = SERIAL_FLASH_CMD_RDSR
        pkt[1] = 0xff
        self.select()
        res = self.exchange(pkt)
        #res = self.read(1)
        self.unselect()
        #print("BUSY",res[0],res[1])
        return res[1]&0x01

    def write_data(self,addr,data):
        """
.. method:: write_data(addr, data)

        Write data *data* starting from address *addr*.
        *data* can be a bytearray or a list of integers less than 256.

        :meth:`erase_sector` MUST be called before writing data in a sector.

        Writing is also allowed via bracket notation. The following is valid syntax: ::

            my_flash[addr] = data

        """
        print('spiflash:write_data', addr, len(data), type(data))
        self.write_enable()

        pkt = bytearray()
        pkt.append(SERIAL_FLASH_CMD_WRITE)
        pkt.extend(_parse_addr(addr,3))
        if type(data) == PBYTEARRAY:
            pkt.extend(data)
        elif type(data) == PLIST:
            for el in data:
                pkt.append(el)
        else:
            pkt.append(data)
        self._write_and_wait(pkt)

    def erase_sector(self,addr):
        """
.. method:: erase_sector(addr)

        Erase a whole sector passing the *addr* address of any byte contained in it.
        All sector bytes set to 0xff.

        """
        self.write_enable()

        pkt = bytearray()
        pkt.append(SERIAL_FLASH_CMD_SER)
        pkt.extend(_parse_addr(addr,3))
        self._write_and_wait(pkt)

    def read_data(self,addr,n=1):
        """
.. method:: read_data(addr, n=1)

        Read *n* bytes of data starting from address *addr*.

        Reading is also allowed via bracket notation. The following is valid syntax: ::

            my_data = my_flash[addr:addr+n]

        """
        print('spiflash:read_data:',addr,n)
        pkt = bytearray()
        pkt.append(SERIAL_FLASH_CMD_READ)
        pkt.extend(_parse_addr(addr,3))
        pkt.extend(b'\xff'*n)
        self.select()
        res = self.exchange(pkt)
        self.unselect()
        return res[4:]

    def chip_erase(self):
        """
.. method:: chip_erase()

        Erase the whole memory.
        All memory bytes set to 0xff.

        """
        self.write_enable()

        pkt = bytearray(1)
        pkt[0] = SERIAL_FLASH_CMD_ERASE
        self._write_and_wait(pkt)

    def chip_id(self,n):
        """
.. method:: chip_id(n)

        Returns the bytes representation of the flash chip unique identifier.
        The length in bytes of the chip id must be passed as argument *n*.

        """

        pkt = bytearray(n+1)
        pkt[0]=0x9f
        pkt[1:] = b'\xff'*n
        self.select()
        res = self.exchange(pkt)
        self.unselect()
        return res[1:]

    # def edit(self,addr,data):
    #     b_addr = _parse_addr(addr,3) # sector base addr
    #     se_addr = []
    #     se_addr.append(b_addr[0]) # start edit addr
    #     se_addr.append(b_addr[1])
    #     b_addr[2] = 0
    #     to_w = []
    #     for page in range(0xff):
    #         print("BACKUP: page ", page)
    #         to_w.append(bytearray())
    #         b_addr[1] = page
    #         for cp in self.read_data(b_addr,0xff):
    #             # print("CP: ", cp)
    #             to_w[page].append(cp)
    #     print("ERASE SECTOR")
    #     self.erase_sector(addr)
    #     print("UPDATING VALUES")
    #     for i,x in enumerate(data):
    #         to_w[se_addr[1]][se_addr[0]+i] = x
    #     # for y in to_w:
    #     #     print("to_w: ", y)
    #     for page in range(0xff):
    #         print("UPDATING: page ", page)
    #         b_addr[1] = page
    #         self.write_data(b_addr, to_w[page])
