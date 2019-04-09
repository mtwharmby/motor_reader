import pytest
from mock import Mock, patch

from readMotor import read_parameters


@pytest.fixture
def patch_DevProxy(mocker):
    return mocker.patch("readMotor.DeviceProxy")


def test_write_readable_table(mocker):
    pass


def test_write_dat_file(mocker):
    pass


@patch('readMotor._parameters_list', {'zmx': ['ZMXParam1', 'ZMXParam2'],
                                      'oms': ['OMSParam3', 'OMSParam4']})
def test_read_motor_parameters(mocker):
    # Parameters table should have form:
    # { 'zmx': [zmx_params], 'oms': [oms_params] }
    # - zmx_params should be requested from ZMX Tango
    # - oms_params should be requested from OMSvme Tango
    zmx_dp_mock = Mock()
    oms_dp_mock = Mock()

    motor_dict = read_parameters(zmx_dp_mock, oms_dp_mock)

    zmx_dp_mock.read_attribute.assert_called_with('ZMXParam2')
    oms_dp_mock.read_attribute.assert_called_with('OMSParam4')
    assert list(motor_dict.keys()) == ['ZMXParam1:zmx', 'ZMXParam2:zmx',
                                       'OMSParam3:oms', 'OMSParam4:oms']
