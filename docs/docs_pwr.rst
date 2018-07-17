.. module:: pwr

****************
Power Management
****************

This module enables access to power management functionalities specific to the target microcontroller.
It can be safely imported in every program, however its functions will raise `UnsupportedError` if the target VM is not enabled
for power management features (**available for Pro users only**).


There exists two methods of reducing power consumption:

    * optimizing runtime behaviour of the VM task scheduler
    * writing programs that put the microcontroller in low consumption states

The first method is implemented internally by the VM using, when possibile, a tickless version of the underlying RTOS.
The second method rests on the programmer. 

.. note:: During a low power mode the VM stops taking into account the passing of time! Semaphores, locks, suspended threads and software timers will behave as if low power mode was never entered.

Power management is a very platform specific feature of each microcontroller, therefore each function of this module is subject to the mcu limitations.
For reference:

    * :ref:`STM32F families <pwr-stm32f>`
    * :ref:`NXP K64 families <pwr-nxpk64>`
    * :ref:`Microchip SAMD21 <pwr-samd21>`
    * :ref:`ESP8266 <pwr-esp8266>`



Power management model
----------------------

Zerynth tries to abstract the many different power management features of different microcontrollers with the following model:

    * There exist three low power modes: SLEEP, STOP and STANDBY mode
    * The programmer can enter a low power mode by calling the function :func:`go_to_sleep`
    * To exit a low power mode the programmer can setup either a timer or an external event (or both)
    * Once exited from a low power mode the programmer can query the VM with the function :func:`wakeup_reason` to retrieve the cause of exit
    * The programmer can, before entering a low power mode, save some data that is guaranteed to be preserved during low power mode

The following constants are defined:

    * :samp:`PWR_STANDBY`, for STANDBY mode. It is the mode with the lowest consumption because it removes power to RAM and Flash. Therefore, when exiting from STANDBY the VM restarts and executes the program from the beginning.
    * :samp:`PWR_STOP`, for STOP mode. It is the mode with low consumption that keeps RAM powered. On exit the VM restart the program from where it was suspended.
    * :samp:`PWR_SLEEP`, for SLEEP mode. It keeps RAM and most peripherals powered therefore obtaining 
    * :samp:`PWR_RESET`, to indicate power reset as the exit reason from a low power mode
    * :samp:`PWR_INTERRUPT`, to indicate an asynchronous interrupt as the exit reason from a low power mode
    * :samp:`PWR_TIMEOUT`, to indicate a reached timeout as the exit reason from a low power mode
    * :samp:`PWR_WATCHDOG`, to indicate watchdog triggered reset as the exit reason from a low power mode


.. function:: go_to_sleep(timeout, mode)
    
    Enter a low power mode specified by :samp:`mode` (one of :samp:`PWR_STANDBY`, :samp:`PWR_STOP` or :samp:`PWR_SLEEP`).
    :samp:`timeout` (in milliseconds) is used to exit the low power mode after the specified timeout. 
    If zero or negative, no timeout is enabled and the only way to exit low power mode is to configure an asynchronous interrupt.
    The time to enter (and exit) a low power mode is platform dependent and can be significative.
    Return the time in milliseconds spent in low power mode.
    

.. function:: wakeup_reason()

    Return the reason of exit from low power mode. It is useful to change the program behaviour based on low power mode exit reason.


.. function:: get_status_size()

    Return the size in bytes of the space available to safely store data before entering a very low power mode (STANDBY).
    If zero is returned, the target microcontroller doesn't have a special purpose memory for saving the program state between low power modes.

.. function:: set_status_byte(pos, val)

    Save :samp:`val` to the position :samp:`pos` in the special purpose memory. If :samp:`pos` is out of the memory boundaries, an exception is raised.

.. function:: get_status_byte(pos)

    Retrieve the byte at position :samp:`pos` in the special purpose memory. If :samp:`pos` is out of the memory boundaries, an exception is raised.



.. _pwr-stm32f:

Power management for STM32Fxx families
--------------------------------------

For this set of microcontrollers the following modes are enabled:

    * STANDBY mode is equivalent to the microcontroller standby mode (RAM is not preserved).  It can be exited by a rising edge on the MCU WakeUp pin or by a timeout
    * STOP mode is equivalent to the microcontroller stop mode. It can be exited by a rising edge on the MCU WakeUp pin or by any configured GPIO for interrupts (with :func:`OnPinRise` or :func:`OnPinFall`) or by a timeout
    * SLEEP mode is equivalent to the microcontroller sleep mode. It can be exited by any interrupt or timeout.

For low power modes timeouts: 
    * the Real Time Clock (RTC) of the microcontroller is started and configured at VM startup
    * It is driven by the internal 32kHz oscillator with a prescaler of 16; therefore the maximum timeout for a low power mode is 16 seconds.
    * The time spent in low power is returned by :func:`go_to_sleep` with a precision of 1 millisecond

The special purpose memory for low power mode status is the RTC backup domain (80 bytes).


.. _pwr-nxpk64:

Power management for NXP K64 families
-------------------------------------

For this set of microcontrollers the following modes are enabled:

    * STANDBY mode is equivalent to the microcontroller VLLS1 mode (RAM is not preserved).  It can be exited by a configured interrupt (with :func:`OnPinRise` or :func:`OnPinFall`) on any of the WakeUp pins or by a timeout.
    * STOP mode is equivalent to the microcontroller stop mode. It can be exited by any configured GPIO for interrupts (with :func:`OnPinRise` or :func:`OnPinFall`) or by a timeout
    * SLEEP mode is equivalent to the microcontroller sleep mode. It can be exited by any interrupt or timeout.

For low power modes timeouts: 
    * the Low Power Timer (LPTMR) of the microcontroller is started and configured at VM startup
    * It is driven by the internal 1kHz oscillator with a prescaler of 256; therefore the maximum timeout for a low power mode is 16776 milliseconds.
    * The time spent in low power is returned by :func:`go_to_sleep` with a precision of ~250 milliseconds

The special purpose memory for low power mode status is the VBAT register file (32 bytes).


.. _pwr-samd21:

Power management for Microchip SAMD21
-------------------------------------

For this set of microcontrollers the following modes are enabled:

    * STANDBY mode is not supported.
    * STOP mode is equivalent to the microcontroller standby mode (RAM is preserved). It can be exited by a timeout only
    * SLEEP mode is equivalent to the microcontroller IDLE2 mode. It can be exited by any interrupt or timeout.

For low power modes timeouts: 
    * the RTC of the microcontroller is started and configured at VM startup
    * It is driven by the internal 1kHz oscillator; therefore the maximum timeout for a low power mode is ~74 hours.
    * The time spent in low power is returned by :func:`go_to_sleep` with a precision of 1 millisecond.

No special purpose memory for low power mode status is present.

.. _pwr-esp8266:

Power management for Esp8266
----------------------------

For Esp8266 based devices, the only available mode is STANDBY (equivalent to deep sleep). RAM is not preserved. It can be exited by a timeout or
by a signal on the WakeUp pin (GPIO 16). For Esp8266 based boards that have a led attached to GPIO 16, the led is disabled during VM startup since it may cause a system reset.

For low power modes timeouts:
    * RTC is used. 
    * The maximum timeout is 1073 seconds
    * The time spent in STANDBY mode is not returned by :func:`go_to_sleep` (always return 0)

The special purpose memory for low power mode status is the RTC memory (400 bytes available).


    
