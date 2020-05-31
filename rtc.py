"""
.. module:: rtc

***************
Real-Time Clock
***************

This module loads the Real-Time Clock (rtc) driver of the embedded device when available (the chip family should be equipped with a rtc and a driver should have been developed, look at the bottom of this page for info about supported chip families).

When imported, automatically sets the system rtc driver to the default one.

.. function:: init(drvname)

    Loads the rtc driver identified by *drvname*

    Returns the previous driver without disabling it.
    
.. function:: set_utc(seconds, microseconds=0)

    :param seconds: integer Unix timestamp containing the total number of seconds from the 1st of January 1970 at UTC
    :param microseconds: integer number representing the microseconds part of the timestamp to reach sub-second precision

    Sets a Coordinated Universal Time (UTC) reference for the rtc.

.. class:: TimeInfo()

    Class containing useful time information to be filled by the :func:`get_utc` function.
    List of attributes:

        * :attr:`Timeinfo.tv_seconds`: Unix timestamp containing the total number of seconds from the 1st of January 1970 at UTC;
        * :attr:`Timeinfo.tv_microseconds`: number of microseconds to complete the timestamp with sub-second precision;

        * :attr:`Timeinfo.tm_year`: current year
        * :attr:`Timeinfo.tm_month`: months since January (0-11)
        * :attr:`Timeinfo.tm_mday`: day of the month (1-31)
        * :attr:`Timeinfo.tm_hour`: hours since midnight (0-23)
        * :attr:`Timeinfo.tm_min`: minutes after the hour (0-59)
        * :attr:`Timeinfo.tm_sec`: seconds after the minute (0-59)
        * :attr:`Timeinfo.tm_wday`: days since Sunday (0-6)
        * :attr:`Timeinfo.tm_yday`: days since January 1 (0-365)

.. function:: get_utc(verbosity=2)

    When called with verbosity parameter set to :samp:`2`, returns a :class:`TimeInfo` object filled with info derived from the rtc.
    Only :attr:`Timeinfo.tv_seconds` and :attr:`Timeinfo.tv_microseconds` are guaranteed to be filled correctly.
    The availability of the other fields depend on the underlying driver implementation.

    When called with verbosity parameter set to :samp:`1`, returns a tuple containing timestamp seconds and microseconds.

    When called with verbosity parameter set to :samp:`0`, returns a single integer representing the Unix timestamp.


.. _rtc-esp32:

Real-Time Clock for ESP32 devices
---------------------------

When synchronized, ESP32 will perform timekeeping using built-in timers:

    * RTC clock is used to maintain accurate time when chip is in deep sleep mode
    * FRC1 timer is used to provide time at microsecond accuracy when ESP32 is running.

    """

_rtc_drv = 0
_rtc_drvname = 0

@native_c("_vbl_rtc_init",["csrc/vbl/vbl_rtc.c"],["VHAL_RTC"])
def _vbl_rtc_init():
    pass


def init(drvname):
    global _rtc_drv, _rtc_drvname
    res = _rtc_drv
    _vbl_rtc_init()
    _rtc_drv = __driver(drvname)
    _rtc_drvname = drvname
    _rtc_drv.__ctl__(DRV_CMD_INIT,_rtc_drvname&0xff)
    return res

init(RTC0)


def set_utc(seconds, microseconds=0):
    if not _rtc_drv:
        return None
    if seconds < 0 or microseconds < 0:
        raise ValueError
    _rtc_drv.__ctl__(DRV_CMD_WRITE,_rtc_drvname&0xff,seconds,microseconds)


class TimeInfo:
    def __init__(self):
        self.tv_seconds = 0
        self.tv_microseconds = 0

        self.tm_sec = 0
        self.tm_min = 0
        self.tm_hour = 0
        self.tm_mday = 0
        self.tm_month = 0
        self.tm_year = 0
        self.tm_wday = 0
        self.tm_yday = 0
        self.tm_isdst = 0

def get_utc(verbosity=2):
    if not _rtc_drv:
        return None
    utc_result = _rtc_drv.__ctl__(DRV_CMD_READ,_rtc_drvname&0xff,verbosity)

    if verbosity == 2:
        time_info = TimeInfo()
        time_info.tv_seconds = utc_result[0]
        time_info.tv_microseconds = utc_result[1]

        time_info.tm_sec = utc_result[2]
        time_info.tm_min = utc_result[3]
        time_info.tm_hour = utc_result[4]
        time_info.tm_mday = utc_result[5]
        time_info.tm_month = utc_result[6]
        time_info.tm_year = utc_result[7]
        time_info.tm_wday = utc_result[8]
        time_info.tm_yday = utc_result[9]
        time_info.tm_isdst = utc_result[10]

        return time_info

    elif verbosity == 1:
        return (utc_result[0], utc_result[1])

    elif verbosity == 0:
        return utc_result[0]

    else:
        return None
