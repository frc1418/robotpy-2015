
import pytest

def test_smartdashboard_basic(networktables, wpilib):
    
    ntsd = networktables.NetworkTables.getTable("SmartDashboard")
    
    sd = wpilib.SmartDashboard
    
    ntsd.putBoolean('bool', True)
    assert sd.getBoolean('bool', None) == True
    
    sd.putNumber('number', 1)
    assert ntsd.getNumber('number', None) == 1
    
    assert sd.getString("string", None) == None
        
    ntsd.putString("string", "s")
    assert sd.getString("string", None) == "s"
    
def test_smartdashboard_chooser(networktables, wpilib):
    
    ntsd = networktables.NetworkTables.getTable("SmartDashboard")
    
    o1 = object()
    o2 = object()
    o3 = object()
    
    chooser = wpilib.SendableChooser()
    chooser.addObject('o1', o1)
    chooser.addObject('o2', o2)
    chooser.addDefault('o3', o3)
    
    
    
    # Default should work
    assert chooser.getSelected() == o3
    
    wpilib.SmartDashboard.putData('Autonomous Mode', chooser)
    
    # Default should still work
    assert chooser.getSelected() == o3
    
    # switch it up
    ct = ntsd.getSubTable('Autonomous Mode')
    ct.putString(chooser.SELECTED, "o1")
    
    # New choice should now be returned
    assert chooser.getSelected() == o1
    
