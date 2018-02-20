.. module:: flash

*****
Flash
*****

This module contains class definitions to read and write the MCU internal flash


    
=========================
The FlashFileStream class
=========================

.. class:: FlashFileStream(start_address,size)

        This class creates an in memory buffer of size *size* bytes that is filled with the content
        of the internal flash starting from address *start_address*
        
        Subsequent operations of read and write are performed on the memory buffer. To actually write the memory buffer
        to the internal flash a call to flush() is needed.

        The memory buffer can also be accessed via bracket notation. The following is valid syntax: ::

            f = flash.FlashFileStream(0x0800000,512)
            f[0] = 1
            x = f[10:20]

    
.. method:: write(buf)
        
        Writes the content of *buf* at the current file position, checking for overflow.
        
        
.. method:: read_int()
        
        Read 4 bytes at the current position and return the corresponding 32 bit integer.
        
        
.. method:: flush()
        
        Write the memory buffer to flash. It can be VERY slow because the sector(s) of flash interested by the write operation must be erased first.
        
        
.. method:: close()

        Free memory buffer

        
