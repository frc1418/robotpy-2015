# validated: 2017-10-02 EN 34c18ef00062 edu/wpi/first/wpilibj/Solenoid.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import weakref
import warnings
from networktables.instance import NetworkTablesInstance

from .livewindow import LiveWindow
from .resource import Resource
from .sensorbase import SensorBase
from .solenoidbase import SolenoidBase

__all__ = ["Solenoid"]

def _freeSolenoid(solenoidHandle):
    hal.freeSolenoidPort(solenoidHandle)

class Solenoid(SolenoidBase):
    """Solenoid class for running high voltage Digital Output.

    The Solenoid class is typically used for pneumatic solenoids, but could
    be used for any device within the current spec of the PCM.
    
    .. not_implemented: initSolenoid
    """

    def __init__(self, *args, **kwargs):
        """Constructor.

        Arguments can be supplied as positional or keyword.  Acceptable
        positional argument combinations are:
        
        - channel
        - moduleNumber, channel

        Alternatively, the above names can be used as keyword arguments.

        :param moduleNumber: The CAN ID of the PCM the solenoid is attached to
        :type moduleNumber: int
        :param channel: The channel on the PCM to control (0..7)
        :type channel: int
        """
        # keyword arguments
        channel = kwargs.pop("channel", None)
        moduleNumber = kwargs.pop("moduleNumber", None)

        if kwargs:
            warnings.warn("unknown keyword arguments: %s" % kwargs.keys(),
                          RuntimeWarning)

        # positional arguments
        if len(args) == 1:
            channel = args[0]
        elif len(args) == 2:
            moduleNumber, channel = args
        elif len(args) != 0:
            raise ValueError("don't know how to handle %d positional arguments" % len(args))

        if moduleNumber is None:
            moduleNumber = SensorBase.getDefaultSolenoidModule()
        if channel is None:
            raise ValueError("must specify channel")

        super().__init__(moduleNumber)
        self.channel = channel
        self.valueEntry = None

        SensorBase.checkSolenoidModule(moduleNumber)
        SensorBase.checkSolenoidChannel(channel)
        
        portHandle = hal.getPortWithModule(moduleNumber, channel)
        self._solenoidHandle = hal.initializeSolenoidPort(portHandle)

        LiveWindow.addActuatorModuleChannel("Solenoid", moduleNumber, channel,
                                            self)
        hal.report(hal.UsageReporting.kResourceType_Solenoid, channel,
                   moduleNumber)
        
        self.__finalizer = weakref.finalize(self, _freeSolenoid, self._solenoidHandle)
        
        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)
        
    @property
    def solenoidHandle(self):
        if not self.__finalizer.alive:
            raise ValueError("Cannot use channel after free() has been called")
        return self._solenoidHandle

    def free(self):
        """Mark the solenoid as freed."""
        LiveWindow.removeComponent(self)

        if self.valueEntry is not None:
            self.valueEntry.removeListener(self.valueListener)
        
        self.__finalizer()
        self._solenoidHandle = None
        
        super().free()

    def set(self, on):
        """Set the value of a solenoid.

        :param on: True will turn the solenoid output on. False will turn the solenoid output off.
        :type on: bool
        """
        hal.setSolenoid(self.solenoidHandle, on)

    def get(self):
        """Read the current value of the solenoid.

        :returns: True if the solenoid output is on or false if the solenoid output is off.
        :rtype: bool
        """
        return hal.getSolenoid(self.solenoidHandle)

    def isBlackListed(self):
        """
        Check if the solenoid is blacklisted.
            If a solenoid is shorted, it is added to the blacklist and disabled until power cycle, or until faults are
            cleared. See :meth:`clearAllPCMStickyFaults`

        :returns: If solenoid is disabled due to short.
        """
        value = self.getPCMSolenoidBlackList() & (1 << self.channel)
        return value != 0

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Solenoid"

    def initTable(self, subtable):
        if subtable is not None:
            self.valueEntry = subtable.getEntry("Value")
            self.updateTable()
        else:
            self.valueEntry = None

    def updateTable(self):
        if self.valueEntry is not None:
            self.valueEntry.setBoolean("Value", self.get())

    def valueChanged(self, entry, key, value, param):
        self.set(True if value else False)

    def startLiveWindowMode(self):
        self.set(False) # Stop for safety
        super().startLiveWindowMode()

    def stopLiveWindowMode(self):
        super().stopLiveWindowMode()
        self.set(False) # Stop for safety
