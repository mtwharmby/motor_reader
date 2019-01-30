from mock import create_autospec, call

import PyTango
from readMotor import create_motor_tuple


def test_create_motor_tuple(mocker):
    mock_dp_oms = create_autospec(PyTango.DeviceProxy)
    mock_dp_zmx = create_autospec(PyTango.DeviceProxy)
    # mock_dp_ra = create_autospec(PyTango.DeviceProxy)

    assert mock_dp_oms is not mock_dp_zmx

    oms_calls = []
    zmx_calls = []
    for name in ['Acceleration', 'Conversion', 'BaseRate', 'SlewRate', 'SlewRateMax']:
        oms_calls.append(call(name))
    for name in ['AxisName', 'StopCurrent', 'RunCurrent']:
        zmx_calls.append(call(name))







#    attribs_oms = ['Acceleration', 'Conversion', 'BaseRate', 'SlewRate',
#                   'SlewRateMax']
    #attribs_oms = ['Acceleration', 'Conversion', 'BaseRate', 'SlewRate',
#                                  'SlewRateMax']
#    attribs_zmx = ['RunCurrent', 'StopCurrent', 'AxisName']
    attribs_zmx = ['AxisName', 'StopCurrent', 'RunCurrent']

    create_motor_tuple(mock_dp_oms, mock_dp_zmx, 'string')
    mock_dp_oms.read_attribute.assert_has_calls(oms_calls, any_order=True)
    mock_dp_zmx.read_attribute.assert_has_calls(zmx_calls, any_order=True)

#    for name in attribs_zmx:
#        mock_dp_zmx.read_attribute.assert_called_with(name)
