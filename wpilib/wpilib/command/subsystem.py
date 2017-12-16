# validated: 2017-10-03 EN 34c18ef00062 edu/wpi/first/wpilibj/command/Subsystem.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import logging

from .scheduler import Scheduler
from ..sendablebase import SendableBase

__all__ = ["Subsystem"]

class Subsystem(SendableBase):
    """This class defines a major component of the robot.

    A good example of a subsystem is the driveline, or a claw if the robot has
    one.

    All motors should be a part of a subsystem. For instance, all the wheel
    motors should be a part of some kind of "Driveline" subsystem.

    Subsystems are used within the command system as requirements for Command.
    Only one command which requires a subsystem can run at a time.  Also,
    subsystems can have default commands which are started if there is no
    command running which requires this subsystem.

    .. seealso:: :class:`.Command`
    """

    def __init__(self, name=None):
        """Creates a subsystem.

        :param name: the name of the subsystem; if None, it will be set to the
                     name to the name of the class.
        """
        super().__init__()
        # The name
        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name
        Scheduler.getInstance().registerSubsystem(self)
        self.logger = logging.getLogger(__name__)

        # Whether or not getDefaultCommand() was called
        self.initializedDefaultCommand = False
        # The current command
        self.currentCommand = None
        self.currentCommandChanged = True

        # The default command
        self.defaultCommand = None

        self.hasDefaultEntry = None
        self.defaultEntry = None
        self.hasCommandEntry = None
        self.commandEntry = None

    def initDefaultCommand(self):
        """Initialize the default command for a subsystem
        By default subsystems have no default command, but if they do, the
        default command is set with this method. It is called on all
        Subsystems by CommandBase in the users program after all the
        Subsystems are created.
        """
        pass

    def periodic(self):
        """When the run method of the scheduler is called this method will be called.
        """
        func = self.periodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info("Default Subsystem.periodic() method... Overload me!")
            func.firstRun = False

    def setDefaultCommand(self, command):
        """Sets the default command.  If this is not called or is called with
        None, then there will be no default command for the subsystem.

        :param command: the default command (or None if there should be none)
        
        .. warning:: This should NOT be called in a constructor if the subsystem
                     is a singleton.
        """
        if command is None:
            self.defaultCommand = None
        else:
            if self not in command.getRequirements():
                raise ValueError("A default command must require the subsystem")
            self.defaultCommand = command
        if self.hasDefaultEntry is not None and self.defaultEntry is not None:
            if self.defaultCommand is not None:
                self.hasDefaultEntry.setBoolean(True)
                self.defaultEntry.setString(self.defaultCommand.getName())
            else:
                self.hasDefaultEntry.setBoolean(False)

    def getDefaultCommand(self):
        """Returns the default command (or None if there is none).
        
        :returns: the default command
        """
        if not self.initializedDefaultCommand:
            self.initializedDefaultCommand = True
            self.initDefaultCommand()
        return self.defaultCommand

    def setCurrentCommand(self, command):
        """Sets the current command
        
        :param command: the new current command
        """
        self.currentCommand = command
        self.currentCommandChanged = True

    def confirmCommand(self):
        """Call this to alert Subsystem that the current command is actually
        the command.  Sometimes, the Subsystem is told that it has no command
        while the Scheduler is going through the loop, only to be soon after
        given a new one.  This will avoid that situation.
        """
        if self.currentCommandChanged:
            if self.hasCommandEntry is not None and self.commandEntry is not None:
                if self.currentCommand is not None:
                    self.hasCommandEntry.setBoolean(True)
                    self.commandEntry.setString(self.currentCommand.getName())
                else:
                    self.hasCommandEntry.setBoolean(False)
            self.currentCommandChanged = False

    def getCurrentCommand(self):
        """Returns the command which currently claims this subsystem.
        
        :returns: the command which currently claims this subsystem
        """
        return self.currentCommand

    def __str__(self):
        return self.getName()

    def getName(self):
        """Returns the name of this subsystem, which is by default the class
        name.
        
        :returns: the name of this subsystem
        """
        return self.name

    def getSmartDashboardType(self):
        return "Subsystem"

    def initTable(self, table):
        super().initTable(table)
        if table is not None:
            self.hasDefaultEntry = table.getEntry("hasDefault")
            self.defaultEntry = table.getEntry("default")
            self.hasCommandEntry = table.getEntry("hasCommand")
            self.commandEntry = table.getEntry("command")

            if self.defaultCommand is not None:
                self.hasDefaultEntry.setBoolean(True)
                self.defaultEntry.setString(self.defaultCommand.getName())
            else:
                self.hasDefaultEntry.setBoolean(False)

            if self.currentCommand is not None:
                self.hasCommandEntry.setBoolean(True)
                self.commandEntry.setString(self.currentCommand.getName())
            else:
                self.hasCommandEntry.setBoolean(False)
