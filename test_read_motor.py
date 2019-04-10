import pytest
from mock import Mock, patch

from readMotor import read_parameters, generate_device_names


@pytest.fixture
def patch_DevProxy(mocker):
    PyTango = pytest.importorskip('PyTango')
    return mocker.patch("readMotor.DeviceProxy")
#
#
# def test
#
#
# def test_write_readable_table(mocker):
#     pass
#
#
def test_write_dat_file():
    pass


def test_generate_device_names():
    # Name pattern for ZMX: {beamline}/ZMX/{server}.{nn}
    # Name pattern for OMS: {beamline}/motor/{server}.{nn}
    # When provided with b/l & server, return dictionary of names of devices
    dev_names = generate_device_names('EH1A', [12], 'bl00')
    assert dev_names == {'EH1A.12': {'oms': 'bl00/motor/EH1A.12',
                                     'zmx': 'bl00/ZMX/EH1A.12'}}

    dev_names = generate_device_names('EH1B', beamline='bl00')
    assert len(dev_names) == 16
    assert dev_names['EH1B.07'] == {'oms': 'bl00/motor/EH1B.07',
                                    'zmx': 'bl00/ZMX/EH1B.07'}


@patch('readMotor._parameters_list', {'zmx': ['ZMXParam1', 'ZMXParam2'],
                                      'oms': ['OMSParam3', 'OMSParam4']})
def test_read_motor_parameters(mocker):
    # monkeypatch.setattr(PyTango, 'DeviceProxy', Mock())
    # Parameters table should have form:
    # { 'zmx': [zmx_params], 'oms': [oms_params] }
    # - zmx_params should be requested from ZMX Tango
    # - oms_params should be requested from OMSvme Tango
    zmx_dp_mock = Mock()
    oms_dp_mock = Mock()

    motor_dict = read_parameters(oms_dp_mock, zmx_dp_mock)

    zmx_dp_mock.read_attribute.assert_called_with('ZMXParam2')
    oms_dp_mock.read_attribute.assert_called_with('OMSParam4')
    assert list(motor_dict.keys()) == ['ZMXParam1:zmx', 'ZMXParam2:zmx',
                                       'OMSParam3:oms', 'OMSParam4:oms']
