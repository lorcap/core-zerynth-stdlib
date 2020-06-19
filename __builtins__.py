"""
.. module:: builtins

**************
Zerynth Builtins
**************

This module contains builtins functions and constants. It is automatically loaded and you don't need to prefix the
module name to call its functions. For example it is not necessary to write ``__builtins__.print()`` but only ``print()`` will suffice.
The explicit name ``__builtins__`` must be used when there is a need to modify a builtin name. For example, to change the default stream it is necessary to write ``__builtins__.__default_stream=mystream``.

==================
Builtins Constants
==================

Zerynth VM defines the following Python builtin constants:

.. data:: False

   The false value of the :class:`bool` type. Assignments to ``False``
   are illegal and raise a :exc:`SyntaxError`.

.. data:: True

   The true value of the :class:`bool` type. Assignments to ``True``
   are illegal and raise a :exc:`SyntaxError`.


.. data:: None

   The sole value of the type ``NoneType``.  ``None`` is frequently used to
   represent the absence of a value, as when default arguments are not passed to a
   function. Assignments to ``None`` are illegal and raise a :exc:`SyntaxError`.


Zerynth VM recognizes a set of pre-defined uppercase names representing constants:

    * Pin Names:

      * ``D0`` to ``D127`` representing the names of digital pins.
      * ``A0`` to ``A127`` representing the names of analog pins.
      * ``LED0`` to ``LED32`` representing the names of the board leds.
      * ``BTN0`` to ``BTN32`` representing the names of the board buttons.
      
    * Pin Modes and Values:

      * ``INPUT, OUTPUT, INPUT_PULLUP, INPUT_PULLDOWN, OUTPUT_PUSHPULL, OUTPUT_OPENDRAIN, INPUT_ANALOG`` representing pin modes.
      * ``LOW, HIGH`` representing digital pin states.

    * Time Units:

      * ``MICROS`` to select microseconds
      * ``MILLIS`` to select milliseconds
      * ``SECONDS`` to select seconds

    * Peripherals Names:

      * ``SERIAL0`` to ``SERIAL7`` representing the name of the nth serial port of a board.
      * ``ADC0`` to ``ADC7`` representing the name of the nth analog to digital converter of a board.
    


==================
Builtin Exceptions
==================

Zerynth VM exceptions are different from Python exceptions. In Python, exceptions are very powerful because they are implemented as classes, contain error messages, and one can examine the full exceution stack when an exception is raised.
However, in the embedded world, resources are precious and keeping class definition in memory, creating a class instance everytime an exception is raised, can be very resource-consuming.

Zerynth VM exceptions are therefore implemented as error codes with optional static error messages organized as a tree::

    Exception
      +-- StopIteration
      +-- ArithmeticError
      |    +-- FloatingPointError
      |    +-- OverflowError
      |    +-- ZeroDivisionError
      +-- AttributeError
      +-- LookupError
      |    +-- IndexError
      |    +-- KeyError
      +-- MemoryError
      +-- NameError
      +-- PeripheralError
      |    +-- InvalidPinError
      |    +-- InvalidHardwareStatusError
      |    +-- HardwareInitializationError
      +-- IOError
      |    +-- ConnectionError
      |    |    +-- ConnectionAbortedError
      |    |    +-- ConnectionRefusedError
      |    |    +-- ConnectionResetError
      |    +-- TimeoutError
      +-- RuntimeError
      |    +-- NotImplementedError
      |    +-- UnsupportedError
      +-- TypeError
      +-- ValueError


This way, the inheritance mechanism of classes is mantained and trasposed to the exception matching mechanism transparently.
The following is valid Zerynth code: ::
    
    try:
        # raise ZeroDivisionError
        x = 1/0 
    except ArithmeticError as e:
        print(e)


The main difference between Zerynth exceptions and Python exceptions is in the way new exceptions are created and used.
To create a user defined exception in Zerynth you need to use the following code: ::

    new_exception(MyExceptionName, MyExceptionParent, MyErrorMessage)

The builtin function ``new_exception`` always needs 2 arguments and an optional message:

    * the first one is the user defined exception name
    * the second is the name of the parent exception in the exception tree
    * the third one is a static error message, where static in this context means both that it is not stored in ram as a Python string and that it can be defined only once and never changed later.

Behind the scenes ``MyExceptionName`` is created and placed under ``MyExceptionParent`` in the exception tree. An exception object is returned.
The exception object can only be compared to other exceptions, printed (as an error code plus message error) or raised again. 

When an exception is printed, the error message is concatenated with the error code and, if the exception has been raised, with the bytecode position where the error happened.

Zerynth exceptions are not garbage collected. They also are not scoped: this means that an exception defined in a module is not contained in that module, but it is moved at builtin scope, so that it can be accessible by all other modules simply by name.
This feature has a drawback: two modules defining an exception with the same name, can't be compiled in the same program. Exception names must be *manually* scoped by correctly choosing them (i.e. preprending the module name to the actual name).


.. _builtins-gpio-functions:

======================
Builtin GPIO Functions
======================

Zerynth VM extends Python with builtins functions to handle the General Purpose Input Output pins of the embedded device.
These functions resembles the ones used by Arduino, but are more flexible.


.. function:: pinMode(pin,mode)

    Sets the pin *pin* in mode *mode*. Allowed values for *mode* are ``INPUT, OUTPUT, INPUT_PULLUP, INPUT_PULLDOWN, OUTPUT_PUSHPULL, OUTPUT_OPENDRAIN, INPUT_ANALOG``
    
.. function:: digitalRead(pin)

    Returns the state of the pin *pin*. The state can be ``LOW`` or ``HIGH``

.. function:: digitalWrite(pin, val)

    Sets the pin *pin* to the value *val*. If val is zero, *pin* is set to ``LOW``, otherwise to ``HIGH``

.. function:: pinToggle(pin)

    Sets the pin *pin* to the value opposite to the current pin value. If value is zero, *pin* is set to ``HIGH``, otherwise to ``LOW``
    
.. function:: analogRead(pin, samples=1)

    Reads analog values from *pin* that must be one of the Ax pins. If *samples* is 1 or not given, returns the integer value read from *pin*.
    If *samples* is greater than 1, returns a tuple of integers of size *samples*.
    The maximum value returned by analogRead depends on the analog resolution of the board.

    analogRead works by calling the adc driver (Analog to Digital Converter) that must be imported and configured: ::

        # import the adc driver
        import adc

        # adc is now configured with default parameters, analogRead can be used as
        x = analogRead(A3)

    analogRead also accepts lists or tuples of pins and returns the corresponding tuple of tuples of samples: ::

        import adc

        x = analogRead([A4,A3,A5],6)

    this piece of code sets *x* to ((...),(...),(...)) where each inner tuple contains 6 samples taken from the corresponding channel.
    To used less memory, the inner tuples can be :class:`bytes`, or :class:`shorts` or normal tuples, depending on the hardware resolution of the adc unit.
    The number of sequentials pins that can be read in a single analogRead call depends on the specific board.

    The analogRead function is provided as a builtin to ease the passage from the Arduino Wiring to Zerynth. However the preferred way to read an analog pin in Zerynth is: ::

        # import the adc driver
        import adc

        x = adc.read(A3)


.. function:: analogWrite(pin, period, pulse, time_unit=MILLIS, npulses=0)

    Activate PWM (Pulse Width Modulation) on pin *pin* (must be one of the PWMx pins). The state of *pin* is periodically switched between ``LOW`` and ``HIGH`` according to parameters:

        * *period* is the duration of a pwm square wave
        * *pulse* is the time the pwm square wave stays in the ``HIGH`` state
        * *time_unit* is the unit of time *period* and *pulse* are expressed in *time_unit*
        
    A PWM wave can be depicted as a train of elements like this: ::

        HIGH  _________________          _________________ 
             |                 |        |                 |
             |                 |        |                 |
        _____|                 |________|                 |____ LOW

             <-----PULSE------>
             <-----PERIOD-------------->

    Here are some examples: ::

        #Remember to import the pwm module
        import pwm

        # A 1000 milliseconds wave that stays HIGH for 100 milliseconds and LOW for 900
        analogWrite(D5.PWM,1000,100)

        # A 500 microseconds wave that stays HIGH for 10 microseconds and LOW for 490
        analogWrite(D5.PWM,500,10,MICROS)

        # Disable pwm
        analogWrite(D5.PWM,0,0)


    Some boards have restrictions on how pwm pins can be used, refer to the single board documentation for details.

    The parameter *npulses* is used to specify a limited train of pulses. When *npulses* is zero or less, PWM is activated on
    the pin and the function returns. When *npulses* is more than zero, analogWrite becomes blocking and returns only after a number of pulses
    equal to *npulses* has been generated on the pin; PWM is disabled on return. For very small pulses in the range of a few ten microseconds,
    the actual number of pulses produced may be greater than *npulses* by one or two units.

    The analogWrite function is provided as a builtin to ease the passage from the Arduino Wiring to Zerynth. However the preferred way to use pwm in Zerynth is: ::

        # import the pwm driver
        import pwm

        pwm.write(D3.PWM,400,10,MICROS)


.. function:: onPinRise(pin, fun, *args, debounce=0, time_unit=MILLIS)

    Executes *fun* with arguments ``*args`` everytime *pin* goes from ``LOW`` to ``HIGH``.
    If *fun* is ``None`` the corresponding interrupt is disabled.
    Each Zerynth VM has its own maximum number of slots for pin interrupts: if they are all full, a ``RuntimeError`` is raised.
    
    Can be used together with :func:`onPinFall` on the same pin.

    *fun* is executed in a high priority thread that takes control of the mcu and puts to sleep every other thread. 
    Therefore *fun* should contains fast code.

    *debounce* and *time_unit* are used to define a timeout such that *fun* is called only if *pin* stays high for all the duration of the timeout.

.. function:: onPinFall(pin, fun, *args, debounce=0, time_unit=MILLIS)

    Executes *fun* with arguments ``*args`` everytime *pin* goes from ``HIGH`` to ``LOW``.
    If *fun* is ``None`` the corresponding interrupt is disabled.
    Each Zerynth VM has its own maximum number of slots for pin interrupts: if they are all full, a ``RuntimeError`` is raised.
    
    Can be used together with :func:`onPinRise` on the same pin.

    *fun* is executed in a high priority thread that takes control of the mcu and puts to sleep every other thread. Therefore *fun* should contains fast code.

    *debounce* and *time_unit* are used to define a timeout such that *fun* is called only if *pin* stays high for all the duration of the timeout.

=================
Builtin Functions
=================


.. function:: int(x=0,base=10)
                
   Return an integer object constructed from a number or string *x*, or return
   ``0`` if no arguments are given.  If *x* is a floating point number, it is
   truncated towards zero.

   If *x* is not a number or if *base* is given, then *x* must be a string,
   :class:`bytes`, or :class:`bytearray` instance representing an :integer
   in radix *base*.  Optionally, the literal can be
   preceded by ``+`` or ``-`` (with no space in between) and surrounded by
   whitespace.  A base-n literal consists of the digits 0 to n-1, with ``a``
   to ``z`` (or ``A`` to ``Z``) having
   values 10 to 35.  The default *base* is 10. The allowed values are 0 and 2-36.
   Base-2, -8, and -16 literals can be optionally prefixed with ``0b``/``0B``,
   ``0o``/``0O``, or ``0x``/``0X``, as with integer literals in code.  Base 0
   means to interpret exactly as a code literal, so that the actual base is 2,
   8, 10, or 16, and so that ``int('010', 0)`` is not legal, while
   ``int('010')`` is, as well as ``int('010', 8)``.

.. function:: type(x)

    Return an integer representing the type of x.
    The following are the builtin constants returned by type(): ::

        PSMALLINT, PINTEGER, PFLOAT, PBOOL, PSTRING, PBYTES, PBYTEARRAY, PSHORTS, PSHORTARRAY, PLIST, PTUPLE, PRANGE,
        PFROZENSET, PSET, PDICT, PFUNCTION, PMETHOD, PCLASS, PINSTANCE, PMODULE, PITERATOR,
        PNONE, PEXCEPTION, PNATIVE, PSYSOBJ, PDRIVER, PTHREAD

.. function:: thread(fun,*args,prio=PRIO_NORMAL,size=-1)

    Function *fun* is launched in a new thread using args as its parameters.
    *fun* must be a normal function or a methods, other callables are not supported yet.

    *prio* sets the thread priority and accepts one of ``PRIO_LOWEST``, ``PRIO_LOWER``, ``PRIO_LOW``, ``PRIO_NORMAL``, ``PRIO_HIGH``, ``PRIO_HIGHER``, ``PRIO_HIGHEST``.
    *size* is the memory in bytes , reserved for the thread inner workings. Negative values select the VM default size.

    Returns the created thread, already started. Raises :exc:`RuntimeError` if no more threads can be created.

.. function:: sleep(time,time_unit=MILLIS)

    Suspend the current thread for *time* expressed in *time_units*. All the other threads are free to continue their execution.
    If *time_unit* is MICROS, sleep does not suspend the current thread, but starts polling the cycles counter in a loop.

    For high precision sleep refer to :mod:`hwtimers

.. function:: random()
              random(a,b)  

    Returns a random integer. If *a* and *b* are given, the random integer is contained in the range [a,b]. If the board has a builtin Random Number Generator, it is used.

.. function:: range(stop)
              range(start, stop[, step])

   Creates a range object.

.. function:: bytearray([source])

   Return a new array of bytes. A bytearray is a mutable
   sequence of integers in the range 0 <= x < 256.  It has most of the usual
   methods of mutable sequences, described in :ref:`typesseq-mutable`, as well
   as most methods that the :class:`bytes` type has, see :ref:`bytes-methods`.

   The optional *source* parameter can be used to initialize the array in a few
   different ways:

   * If it is a *string*, :func:`bytearray` then converts the string to
     bytes.

   * If it is an *integer*, the array will have that size and will be
     initialized with null bytes.

   Without an argument, an array of size 0 is created.

.. function:: bytes([source])

   Return a new "bytes" object, which is an immutable sequence of integers in
   the range ``0 <= x < 256``.  :class:`bytes` is an immutable version of
   :class:`bytearray` -- it has the same non-mutating methods and the same
   indexing and slicing behavior.

   Accordingly, constructor arguments are interpreted as for :func:`bytearray`.


.. function:: shortarray([source])

   Return a new array of shorts. A shortarray is a mutable
   sequence of integers in the range 0 <= x < 65536.  It has most of the usual
   methods of mutable sequences, described in :ref:`typesseq-mutable`, as well
   as most methods that the :class:`shorts` type has, see :ref:`shorts-methods`.

   The optional *source* parameter can be used to initialize the array in a few
   different ways:

   * If it is an *integer*, the array will have that size and will be
     initialized with zeros.

   * If it is a sequence, the array will be a copy of *source* with its elements converted into shorts.
     If the conversion is not possible, an exception is raised.

   Without an argument, an array of size 0 is created.

.. function:: shorts([source])

   Return a new shorts object, which is an immutable sequence of integers in
   the range ``0 <= x < 65536``.  :class:`shorts` is an immutable version of
   :class:`shortarray` -- it has the same non-mutating methods and the same
   indexing and slicing behavior.

   Accordingly, constructor arguments are interpreted as for :func:`shortarray`.


.. function:: enumerate(iterable, start=0)

   Return an enumerate object. *iterable* must be a sequence, an
   :term:`iterator`, or some other object which supports iteration.
   The :meth:`~iterator.__next__` method of the iterator returned by
   :func:`enumerate` returns a tuple containing a count (from *start* which
   defaults to 0) and the values obtained from iterating over *iterable*.

   It is normally used in ``for`` loops: ::

        ints = [10,20,30]
        for idx, val in enumerate(ints):
            print(idx, val)

        # prints out the following:
        >>> 0 10
        >>> 1 20
        >>> 2 30

   In this version of the VM, enumerate works only for primitive iterable types, not yet for instances with ``__next__`` and ``__iter__`` methods.

.. function:: reversed(seq)

   Return a reverse :term:`iterator`.  *seq* must be an object which has
   a :meth:`__reversed__` method or supports the sequence protocol (the
   :meth:`__len__` method and the :meth:`__getitem__` method with integer
   arguments starting at ``0``).

   In this version of the VM, reversed works only for primitive iterable types, not yet for instances with ``__next__`` and ``__iter__`` methods.

.. function:: ord(c)

   Given a string representing one character, return an integer
   representing that character.  For example, ``ord('a')`` returns the integer ``97``.
   This is the inverse of :func:`chr`.

   When *c* is a literal string, the compiler macro __ORD(c) can be used to reduce code size.
   For example: ::

    x = ord(":")

   is valid Zerynth code. During its execution a string must be created containing ":" and *ord* must be called on it.
   After *ord* is executed the created string is probably immediately garbage collected.
   In the embedded world, this is time and resource consuming.
   The operation ``ord(":")`` can be executed during compilation because the result is known before the execution of
   the Zerynth program. To enable this feature use the following code: ::

    x = __ORD(":")

   Now, no string is created and no function is called, because the compiler knows that you want to assign to ``x``
   the result of ``ord(":")`` (which is 58). The compiler transforms our program to a faster and equivalent version: ::

    x = 58

.. function:: chr(i)

   Return the string representing a character whose byte representation is the integer
   *i*.  For example, ``chr(97)`` returns the string ``'a'``. This is the
   inverse of :func:`ord`. :exc:`ValueError` will be raised if *i* is
   outside the valid range.
   

.. function:: isinstance(object, class)

   Return true if the *object* argument is an instance of the *class*
   argument, or of a (direct, indirect) subclass thereof.  If *object* is not
   an object of the given type, the function always returns false.  If *class* is not a class,
   a :exc:`TypeError` exception is raised.

   In this version of the VM, isinstance is still not compliant with the Python one. 
   It is suggested to use isinstance to determine the hierarchy of instances and to use :func:`type` for primitive types.

"""

#BUILTIN CONSTANTS


##### TIMES
__define(NANOS,0)
__define(MICROS,1)
__define(MILLIS,2)
__define(SECONDS,3)


##### DRIVERS
__define(DRV_CMD_INIT,0)
__define(DRV_CMD_DONE,1)
__define(DRV_CMD_WRITE,2)
__define(DRV_CMD_READ,3)
__define(DRV_CMD_AVAILABLE,4)
__define(DRV_CMD_OPEN,7)
__define(DRV_CMD_CLOSE,8)
__define(DRV_CMD_STARTUP,9)
__define(DRV_CMD_SOCKET,10)
__define(DRV_CMD_BIND,11)
__define(DRV_CMD_LISTEN,12)
__define(DRV_CMD_ACCEPT,13)
__define(DRV_CMD_RESOLVE,14)
__define(DRV_CMD_INFO,15)
__define(DRV_CMD_SETOPTS,16)
__define(DRV_CMD_GETOPTS,17)
__define(DRV_CMD_START_PING,18)
__define(DRV_CMD_CHECK_PING,19)
__define(DRV_CMD_STOP_PING,20)
__define(DRV_CMD_WRITE_TO,21)
__define(DRV_CMD_READ_FROM,22)
__define(DRV_CMD_SCAN,23)



##### PIN MODES & VALUES
__define(INPUT,1)
__define(OUTPUT,4)
__define(INPUT_PULLUP,2)
__define(INPUT_PULLDOWN,3)
__define(INPUT_PULLNONE,1)
__define(OUTPUT_PUSHPULL,4)
__define(OUTPUT_OPENDRAIN,5)
__define(OUTPUT_HIGHDRIVE,6)
__define(INPUT_ANALOG,7)


__define(LOW,0)
__define(HIGH_TO_LOW,0)
__define(FALLING_EDGE,0)
__define(HIGH,1)
__define(LOW_TO_HIGH,1)
__define(RISING_EDGE,1)
__define(BOTH_EDGES,2)



##### WIFI & SOCKETS
#__define(WIFI_OPEN,0)
#__define(WIFI_WEP,1)
#__define(WIFI_WPA,2)
#__define(WIFI_WPA2,3)

#__define(SOCK_DGRAM,-1)
#__define(SOCK_STREAM,1)


##### THREADING
__define(TAKEN,1)
__define(NOT_TAKEN,0)


__define(PRIO_IDLE,0)
__define(PRIO_LOWEST,1)
__define(PRIO_LOWER,2)
__define(PRIO_LOW,3)
__define(PRIO_NORMAL,4)
__define(PRIO_HIGH,5)
__define(PRIO_HIGHER,6)
__define(PRIO_HIGHEST,7)



##### TYPES
__define(PSMALLINT,0)
__define(PINTEGER,1)
__define(PFLOAT,2)
__define(PNUMBER,2)
__define(PBOOL,3)
__define(PSTRING,4)
__define(PBYTES,5)
__define(PBYTEARRAY,6)
__define(PSHORTS,7)
__define(PSHORTARRAY,8)
__define(PLIST,9)
__define(PTUPLE,10)
__define(PRANGE,11)
__define(PSEQUENCE,11)
__define(PFSET,12)
__define(PSET,13)
__define(PDICT,14)
__define(PFUNCTION,15)
__define(PMETHOD,16)
__define(PCLASS,17)
__define(PINSTANCE,18)
__define(PMODULE,19)
__define(PBUFFER,20)
__define(PSLICE,21)
__define(PITERATOR,22)
__define(PFRAME,23)
__define(PBLOCK,24)
__define(PNONE,25)
__define(PEXCEPTION,26)
__define(PNATIVE,27)
__define(PSYSOBJ,28)
__define(PDRIVER,29)
__define(PTHREAD,30)



##### VARIOUS
__define(ADC_HI_RES,1)
__define(ADC_LOW_RES,0)


##### STRINGS
__define(STRIP_LEFT,1)
__define(STRIP_RIGHT,-1)
__define(STRIP_BOTH,0)


__define(GC_CMD_INFO,     0)
__define(GC_CMD_COLLECT,  1)
__define(GC_CMD_DISABLE,  2)
__define(GC_CMD_ENABLE,   3)


__define(VM_CMD_VERSION,  0)
__define(VM_CMD_INFO,     1)
__define(VM_CMD_BOARD,    2)




#BUILTIN EXCEPTIONS

new_exception(ArithmeticError,Exception)
new_exception(ZeroDivisionError,ArithmeticError)
new_exception(FloatingPointError,ArithmeticError)
new_exception(OverflowError,ArithmeticError)

new_exception(LookupError,Exception)
new_exception(IndexError,LookupError)
new_exception(KeyError,LookupError)

new_exception(NameError,Exception)
new_exception(RuntimeError,Exception)
new_exception(TypeError,Exception)
new_exception(ValueError,Exception)
new_exception(AttributeError,Exception)

new_exception(NotImplementedError,RuntimeError)
new_exception(UnsupportedError,RuntimeError)

new_exception(StopIteration,Exception)

new_exception(PeripheralError,Exception)
new_exception(InvalidPinError,PeripheralError)
new_exception(InvalidHardwareStatusError,PeripheralError)
new_exception(HardwareInitializationError,PeripheralError)

new_exception(IOError,Exception)
new_exception(ConnectionError,IOError)
new_exception(ConnectionAbortedError,ConnectionError)
new_exception(ConnectionRefusedError,ConnectionError)
new_exception(ConnectionResetError,ConnectionError)
new_exception(TimeoutError,IOError)

new_exception(OSError,Exception)


@builtin
def thread(fn,*args,prio = PRIO_NORMAL, size=-1):
    pth = __thread(fn,size,prio,args)
    pth.start()
    return pth



@builtin
def print(*objects,sep=" ",end="\n", stream=None):
    """
.. function:: print(*args,sep=" ",end="\\\\n", stream=None)

   Print *objects* to the stream *stream*, separated by *sep* and followed
   by *end*.  *sep*, *end* and *stream*, if present, must be given as keyword
   arguments.

   All non-keyword arguments are converted to strings like :func:`str` does and
   written to the stream, separated by *sep* and followed by *end*.  Both *sep*
   and *end* must be strings. If no *objects* are given, :func:`print` will just write
   *end*.

   The *stream* argument must be an object with a ``write(string)`` method; if it
   is not present or ``None``, :data:`__default_stream` will be used.

   Whether output is buffered is usually determined by *stream*.    
    """
    if not stream:
        if not __default_stream:
            return
        stream = __default_stream
    l = len(objects)
    for i in range(0,l-1):
        stream.write(str(objects[i]))
        stream.write(sep)
    if l:
        stream.write(str(objects[-1]))
    stream.write(end)

@builtin
def analogRead(pin,samples=1):
    if not __default_adc:
        return None
    return __default_adc.__ctl__(DRV_CMD_READ,0,pin,samples)

@builtin
def analogWrite(pin,period,pulse,time_unit=MILLIS,npulses=0):
    if not __default_pwm:
        return
    __default_pwm.__ctl__(DRV_CMD_WRITE,pin,period,pulse,time_unit,npulses)


@builtin
def abs(x):
    """
.. function:: abs(x)

   Return the absolute value of a number.  The argument may be an
   integer or a floating point number.
    """
    if x<=0:
        return -x
    else:
        return x

@builtin
def all(x):
    """
.. function:: all(iterable)

   Return ``True`` if all elements of the *iterable* are true (or if the iterable
   is empty).  Equivalent to::

      def all(iterable):
          for element in iterable:
              if not element:
                  return False
          return True

    """
    for element in x:
        if not element:
            return False
    return True

@builtin
def any(x):
    """
.. function:: any(iterable)

   Return ``True`` if any element of the *iterable* is true.  If the iterable
   is empty, return ``False``.  Equivalent to::

      def any(iterable):
          for element in iterable:
              if element:
                  return True
          return False
    """
    for element in x:
        if element:
            return True
    return False

@builtin
def sum(x,start=0):
    """
.. function:: sum(iterable[, start])

   Sums *start* and the items of an *iterable* from left to right and returns the
   total.  *start* defaults to ``0``. 

    """
    for element in x:
        start+=element
    return start

@builtin
def divmod(a,b):
    """
.. function:: divmod(a, b)

    Take two (non complex) numbers as arguments and return a pair of numbers
    consisting of their quotient and remainder when using integer division.
    When *a* and *b* are integers, the result is the same as ``(a // b, a % b)``.
    When any of them are floating point numbers, :exc:`TypeError` is raised.

    """
    if type(a) == PFLOAT or type(b) == PFLOAT:
        raise NotImplementedError
    return (a // b, a % b)

@builtin
def max(*args):
    """
.. function:: max(*args)

   Return the largest item in args.

    """
    if len(args)==1:
        args=args[0]
        if len(args)==0:
            raise ValueError
    tmp = args[0]
    for element in args:
        if element>tmp:
            tmp = element
    return tmp

@builtin
def min(*args):
    """
.. function:: min(*args)

   Return the smallest item in args.

    """
    if len(args)==1:
        args=args[0]
        if len(args)==0:
            raise ValueError
    tmp = args[0]
    for element in args:
        if element<tmp:
            tmp = element
    return tmp

@builtin
def round(number, ndigits=None):
    """
.. function:: round(number[, ndigits])

   Return *number* rounded to *ndigits* precision after the decimal point. If
   *ndigits* is omitted or is ``None``, it returns the nearest integer to its
   input.

   For the built-in types supporting :func:`round`, values are rounded to the
   closest multiple of 10 to the power minus *ndigits*; if two multiples are
   equally close, rounding is done toward the even choice (so, for example, both
   ``round(-1.5)`` and ``round(-0.5)`` are ``0``, and ``round(1.5)`` is ``2``).
   Any integer value is valid for *ndigits* (positive, zero, or negative). The
   return value is an integer if *ndigits* is omitted or ``None``. Otherwise
   the return value has the same type as number.

   For a general Python object *number*, :func:`round` is not implemented.

    """
    N = abs(number)
    if ndigits == None:
        s = 1 if number >= 0 else -1
        n = int(N)
        r = N - n
        if r > 0.5 or (r == 0.5 and n % 2 == 1):
            n += 1
        return s*n
    elif type(ndigits) in (PSMALLINT, PINTEGER):
        shift10 = 10**ndigits
        ret = round(N*shift10, None)/shift10
        return ret if type(N) == PFLOAT else int(ret)
    else:
        raise TypeError

@builtin
def len(x):
    """
.. function:: len(s)

   Return the length (the number of items) of an object.  The argument may be a
   sequence (such as a string, bytes, tuple, list, or range) or a collection
   (such as a dictionary, set, or frozen set), or any instance defining the method ``__len__``.

    """
    return x.__len__()

@builtin
def hex(x,prefix="0x"):
    """
.. function:: hex(x,prefix="0x")

   Convert an integer number to a lowercase hexadecimal string
   prefixed with *prefix* (if not given "0x" is used), for example:

      >>> hex(255)
      '0xff'
      >>> hex(-42)
      '-0x2a'

   See also :func:`int` for converting a hexadecimal string to an
   integer using a base of 16.
    """
    if x>=0:
        #positive
        if x<=255:
            l=2
            r=prefix+"00"
        elif x<=65535:
            l=4
            r=prefix+"0000"
        else:
            l=8
            r=prefix+"00000000"
    else:
        #negative
        if x>=-128:
            l=2
            r=prefix+"00"
        elif x>=-32768:
            l=4
            r=prefix+"0000"
        else:
            l=8
            r=prefix+"00000000"
    i=___len(prefix)
    for j in range(l*4-4,-1,-4):
        b = (x>>j)&0x0f
        if b>=0 and b<=9:
            c= __ORD('0')+b
        else:
            c= __ORD('A')+(b-10)
        __pack("B",r,0,i,c)
        i+=1
    return r
    

@builtin
def str(x=""):
    """
.. function:: str(x="")
  
   Return a string version of *x*.  If *x* is not
   provided, returns the empty string.  
   Returns the "informal" or nicely printable string representation of *object*.  For string objects, this is
   the string itself. For primitive types like list, tuples, dicts a standard representation is returned. For all other types, the method __str__ is called.
 
    """
    t = type(x)
    if t == PLIST or t==PSHORTARRAY:
        oc = "["
        ec = "]"
    elif t == PTUPLE or t==PSHORTS:
        oc = "("
        ec = ")"
    elif t == PDICT or t==PSET or t==PFSET:
        oc = "{"
        ec = "}"
    elif t== PINSTANCE or t==PCLASS:
        return x.__str__()
    else:
        return __str(x)
    res = ""
    if t == PDICT:
        for k,v in x.items():
            res+=" "+str(k)+":"+str(v)+","
    else:
        for y in x:
            res+=" "+str(y)+","
    if ___len(x):
        __byte_set(res,___len(res)-1,ord(ec))
        __byte_set(res,0,ord(oc))
    else:
        res+=oc+ec
    return res

@builtin
def dict(*args):
    """
.. function:: dict(*args)

   Return a new dictionary initialized from an optional *args.
  
   If no *args is given, an empty dictionary is created. If a single positional argument is given and it is a mapping object, a dictionary is created with the same key-value pairs as the mapping object. 
   Otherwise, if more than a positional argument is given, each pair of arguments is inserted in the dictionary with the first argument of the pair being the key and the second argument the value.
   If a key occurs more than once, the last value for that key becomes the corresponding value in the new dictionary.
   If the number of positional arguments is odd, the value for the last key is None.

    """
    l =___len(args)
    if l == 0:
      return __new_dict(0)
    elif l==1:
      x = args[0]
      if (hasattr(x,"__setitem__") and hasattr(x,"__getitem__") and hasattr(x,"items")) or type(x)==PDICT:
        res = __new_dict(len(x))
        for k,v in args[0].items():
          res[k]=v
        return res
      raise TypeError
    else:
      res = __new_dict((l+1)//2)
      for i,x in enumerate(args):
        if i%2==0:
          k=x
        else:
          res[k]=x
      if l%2:
        res[k]=None
      return res


@builtin
def set(*args):
  """
.. function:: set(*args)

   Return a new set initialized from an optional *args.
  
   If no *args is given, an empty set is created. If a single positional argument is given and it is an iterable object, a set is created and filled with the values of the iterable. 
   Otherwise, if more than a positional argument is given, each argument is inserted in the set.

  """
  l = ___len(args)
  if l==0:
    return __new_set(0,PSET)
  elif l==1:
    res =__new_set(len(args[0]),PSET)
    for x in args[0]:
      res.add(x)
    return res
  else:
    res =__new_set(l,PSET)
    for x in args:
      res.add(x)
    return res

@builtin
def frozenset(*args):
  """
.. function:: frozenset(*args)

   Return a new frozenset initialized from an optional *args.
  
   If no *args is given, an empty frozenset is created. If a single positional argument is given and it is an iterable object, a frozenset is created and filled with the values of the iterable. 
   Otherwise, if more than a positional argument is given, each argument is inserted in the frozenset.

  """
  return __change_type(set(args),PFSET);


@builtin
def open(file,mode="rb"):
  """
.. function:: open(file,mode="rb")

   Return an object similar to a stream with read and write methods. The object class depends on the type of file opened.

   If *file* starts with "resource://", open returns a ResourceStream of a flash saved resource.
   
  """
  if file.startswith("resource://"):
    return __default_stream_provider.ResourceStream(file[11:])
  else:
    return __default_stream_provider.FileStream(file[11:],mode)



### global hooks

__default_stream_provider = None

__default_stream = None

__default_adc = None

__default_pwm = None

__default_net = {
  # "sock" contains a socket provider for each AF_ class
  "sock":[None,None,None]
  # particular drivers will add other fields: "wifi","bluetooth", etc..
}

__default_fs = None



@builtin
def onPinRise(pin, fun, *args, debounce=0,time_unit=MILLIS):
  __onPinRiseOrFall(pin,fun,debounce,time_unit,1,args);


@builtin
def onPinFall(pin, fun, *args, debounce=0,time_unit=MILLIS):
  __onPinRiseOrFall(pin,fun,debounce,time_unit,-1,args);




### __STRFORMAT__ MUST ALWAYS BE THE LAST BUILTIN FUNCTION!!! (it is called as a mod delegation in vm.c)

@builtin
def __strformat__(self,arg):
  if type(arg)!=PTUPLE and type(arg)!=PLIST and type(arg)!=PDICT:
    arg=[arg]
  flds = self.split("%")
  res = ""
  curarg = 0
  thearg=None
  pempty=0
  for n,fld in enumerate(flds):
    # handle %%
    if not fld:
      if pempty%2==1:
        res+="%"
      pempty+=1
      continue
    if pempty and pempty%2==0:
      res+=fld
      pempty=0
      continue
    else:
      pempty=0
    if n==0:
      res+=fld
      continue
    # get arg
    if fld[0]=="(":
      # get arg name
      p = fld.find(")")
      thearg=arg[fld[1:p]]
      fld=fld[p+1:]
    else:
      thearg=arg[curarg]
      curarg+=1

    # get modifiers
    left=0
    pad0=0
    sign=0
    space=0
    p=0
    while __byte_get(fld,p) in " 0-+":
      if __byte_get(fld,p)==__ORD(" "):
        if not sign:
          space=1
      elif __byte_get(fld,p)==__ORD("0"):
        if not left:
          pad0=1
      elif __byte_get(fld,p)==__ORD("-"):
        pad0=0
        left=1
      elif __byte_get(fld,p)==__ORD("+"):
        space=0
        sign=1
      p+=1
      #fld=fld[1:]
    
    width=-1
    precision=-1
    # get width
    if __byte_get(fld,p)==__ORD("*"):
      width=int(thearg)
      thearg=arg[curarg]
      curarg+=1
      p+=1
      #fld=fld[1:]
    else:
      while __byte_get(fld,p) in "0123456789":
        if width<0:
            width=0
        width = width*10 + __byte_get(fld,p)-__ORD("0")
        p+=1
        #fld=fld[1:]
    # get .precision
    if __byte_get(fld,p)==__ORD("."):
      #fld=fld[1:]
      p+=1
      if __byte_get(fld,p)==__ORD("*"):
          precision=int(thearg)
          thearg=arg[curarg]
          curarg+=1
          p+=1
          #fld=fld[1:]
      else:
        while __byte_get(fld,p) in "0123456789":
          if precision<0:
            precision=0
          precision = precision*10 + __byte_get(fld,p)-__ORD("0")
          p+=1
          #fld=fld[1:]

    flags=left|(pad0<<1)|(space<<2)|(sign<<3)
    if __byte_get(fld,p) in "diuxX":
      num = int(thearg)
      flags=flags|0x10
      if num<0:
        flags=flags|0x20
      if __byte_get(fld,p)==__ORD("x"):
        thearg=hex(num,"").lower()
      elif __byte_get(fld,p)==__ORD("X"):
        thearg=hex(num,"")
      else:
        thearg=str(num)
    elif __byte_get(fld,p) in "fgeFGE":
      num = float(thearg)
      flags=flags|0x50
      if num<0:
        flags=flags|0x20
      thearg=str(num)
    elif __byte_get(fld,p)==__ORD("s"):
      thearg=str(thearg)
    else:
      raise ValueError
    p+=1
    fld=fld[p:]
    #print(thearg,flags,width,precision)
    thearg=__strpad(thearg,flags,width,precision)
    res+=thearg+fld
  return res
