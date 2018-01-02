#
# Test the various types of PWM motor controllers in very simple ways
#

import pytest


@pytest.mark.parametrize('clsname, ',
                         ['Jaguar', 'SD540', 'Spark', 'Talon',
                          'PWMTalonSRX', 'Victor', 'VictorSP',
                          'PWMVictorSPX', 'DMC60'])
def test_controller(wpilib, hal_data, clsname):
    
    # create object/helper function
    obj = getattr(wpilib, clsname)(2)
    
    # validate reporting is correct
    # TODO: remove the VictorSPX and DMC60 check once there is usage reporting
    assert clsname in ('PWMVictorSPX', 'DMC60') or hal_data['pwm'][2]['type'] == clsname.lower()
    
    # Assert starts with zero
    assert obj.get() == 0
        
    # call set
    for i in [-1, -.9, -.7, -.3, 0, .3, .7, .9, 1]:
        obj.setInverted(False)
        assert obj.getInverted() == False
        obj.set(i)
        
        # validate that get returns the correct value
        assert abs(obj.get() - i) < 0.01
        
        obj.pidWrite(i)
        assert abs(obj.get() - i) < 0.01
        
        # speed should be correct
        assert abs(hal_data['pwm'][2]['value'] - i) < 0.01
        
        # Make sure inversion works too
        obj.setInverted(True)
        assert obj.getInverted() == True
        
        obj.set(i)
        assert abs(obj.get() + i) < 0.01
