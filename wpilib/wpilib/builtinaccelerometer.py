# validated: 2017-11-21 EN 34c18ef00062 edu/wpi/first/wpilibj/BuiltInAccelerometer.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2014-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in $(WIND_BASE)/WPILib.
#----------------------------------------------------------------------------

import hal

from .interfaces import Accelerometer
from .sensorbase import SensorBase
from .livewindow import LiveWindow

__all__ = ["BuiltInAccelerometer"]

class BuiltInAccelerometer(SensorBase):
    """Built-in accelerometer device

    This class allows access to the roboRIO's internal accelerometer.
    """

    Range = Accelerometer.Range

    def __init__(self, range=Accelerometer.Range.k8G):
        """Constructor.
        
        :param range: The range the accelerometer will measure.  Defaults to
            +/-8g if unspecified.
        :type  range: :class:`.Accelerometer.Range`
        """
        super().__init__()
        self.setRange(range)
        self.xEntry = None
        self.yEntry = None
        self.zEntry = None
        hal.report(hal.UsageReporting.kResourceType_Accelerometer, 0, 0,
                      "Built-in accelerometer")
        LiveWindow.addSensor("BuiltInAccel", 0, self)

    def setRange(self, range):
        """Set the measuring range of the accelerometer.

        :param range: The maximum acceleration, positive or negative, that
                      the accelerometer will measure.
        :type  range: :class:`BuiltInAccelerometer.Range`
        """
        
        hal.setAccelerometerActive(False)

        if range == self.Range.k2G:
            hal.setAccelerometerRange(hal.AccelerometerRange.kRange_2G)
        elif range == self.Range.k4G:
            hal.setAccelerometerRange(hal.AccelerometerRange.kRange_4G)
        elif range == self.Range.k8G:
            hal.setAccelerometerRange(hal.AccelerometerRange.kRange_8G)
        elif range == self.Range.k16G:
            raise ValueError("16G range not supported (use k2G, k4G, or k8G)")
        else:
            raise ValueError("Invalid range argument '%s'" % range)

        hal.setAccelerometerActive(True)

    def getX(self):
        """
           :returns: The acceleration of the roboRIO along the X axis in
                     g-forces
           :rtype: float
        """
        return hal.getAccelerometerX()

    def getY(self):
        """
           :returns: The acceleration of the roboRIO along the Y axis in
                     g-forces
           :rtype: float
        """
        return hal.getAccelerometerY()

    def getZ(self):
        """
           :returns: The acceleration of the roboRIO along the Z axis in
                     g-forces
           :rtype: float
        """
        return hal.getAccelerometerZ()

    def getSmartDashboardType(self):
        return "3AxisAccelerometer"

    def initTable(self, subtable):
        if subtable is not None:
            self.xEntry = subtable.getEntry("X")
            self.yEntry = subtable.getEntry("Y")
            self.zEntry = subtable.getEntry("Z")
            self.updateTable()
        else:
            self.xEntry = None
            self.yEntry = None
            self.zEntry = None

    def updateTable(self):
        if self.xEntry is not None:
            self.xEntry.setDouble(self.getX())
        if self.yEntry is not None:
            self.yEntry.setDouble(self.getY())
        if self.zEntry is not None:
            self.zEntry.setDouble(self.getZ())

    def startLiveWindowMode(self): # pragma: no cover
        pass

    def stopLiveWindowMode(self): # pragma: no cover
        pass
