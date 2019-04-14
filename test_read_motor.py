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
    dev_names = generate_device_names('EH1A', [5, 15, 19])
    assert dev_names == {'EH1A': ['EH1A.05', 'EH1A.15', 'EH1A.19']}

    dev_names = generate_device_names('EH1B')
    assert len(dev_names['EH1B']) == 16
    assert dev_names['EH1B'][6] == 'EH1B.07'


def test_read_motor_parameters():
    oms_dp_mock = Mock()
    zmx_dp_mock = Mock()

    for dp in [oms_dp_mock, zmx_dp_mock]:
        dp.get_all_attributes.return_value = ['attr1', 'attr2']
        dp.read_attribute().value = 4
    
    motor_dict = read_parameters(oms_dp_mock, zmx_dp_mock)

    assert motor_dict == {'oms:attr1': 4, 'oms:attr2': 4,
                          'zmx:attr1': 4, 'zmx:attr2': 4}


@patch('readMotor.DeviceProxy')
@patch('readMotor.parse_args')
def test_main(args_p, dp_mock):
    args_p.return_value = {'beamline': 'p02',
                           'tango_host': 'haspp02oh1:10000',
                           'server': 'EH1A',
                           'dev_ids': 1}

    main()
    dp_mock.assert_has_calls([call('haspp02oh1:10000/p02/motor/EH1A.01'),
                              call('haspp02oh1:10000/p02/ZMX/EH1A.01')])
    

