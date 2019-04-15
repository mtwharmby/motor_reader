import pytest
from mock import call, Mock, patch

from readMotor import (parse_args, read_parameters, generate_device_names, 
                       read_dat, write_dat, main)


def test_parse_args():
    # parse_args needs to return a dictionary, something like:
    eg_conf1 = {'beamline': 'p02',
                'tango_host': 'haspp02oh1:10000',
                'server': 'EH1A',
                'dev_ids': [1],
                'write_params': False}
    # An example sys.argv to encode this lot:
    eg_argv1 = ['-b', 'p02', '--tango-host', 'haspp02oh1:10000',
                '-s', 'EH1A', '1']
    assert parse_args(eg_argv1) == eg_conf1

    # An example requiring more defaulting
    eg_conf2 = {'beamline': 'p02',
                'tango_host': 'haspp02oh1:10000',
                'server': 'EH1A',
                'dev_ids': [12, 15, 32],
                'write_params': False}
    eg_argv2 = ['-s', 'EH1A', '12,15,32']
    assert parse_args(eg_argv2) == eg_conf2

    # Requires even more defaulting!
    eg_conf3 = {'beamline': 'p02',
                'tango_host': 'haspp02oh1:10000',
                'server': 'EH1A',
                'dev_ids': None,
                'write_params': False}
    eg_argv3 = ['-s', 'EH1A']
    assert parse_args(eg_argv3) == eg_conf3

    # Test writing back of values
    eg_conf4 = {'beamline': 'p02',
                'tango_host': 'haspp02oh1:10000',
                'server': 'EH1A',
                'dev_ids': None,
                'write_params': True,
                'input_file': 'new-motors.param'}
    eg_argv4 = ['-s', 'EH1A', '--write', 'new-motors.param']
    assert parse_args(eg_argv4) == eg_conf4


# @pytest.fixture
# def patch_DevProxy(mocker):
#     return mocker.patch(readMotor, DeviceProxy")


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
        dp.get_attribute_list.return_value = ['attr1', 'attr2']
        dp.read_attribute().value = 4

    motor_dict = read_parameters(oms_dp_mock, zmx_dp_mock)

    assert motor_dict == {'oms:attr1': 4, 'oms:attr2': 4,
                          'zmx:attr1': 4, 'zmx:attr2': 4}


def test_write_motor_parameters():
    oms_dp_mock = Mock()
    zmx_dp_mock = Mock()

    motor_params = {'oms:attr1': 2, 'oms:attr2': 6,
                    'zmx:attra': 24, 'zmx:attrb': 10, 'Deactivation': 0}

    write_parameters(oms_dp_mock, zmx_dp_mock, motor_params)

    oms_calls = [call('attr1', 2), call('attr2', 6)]
    zmx_calls = [call('attra', 24), call('attrb', 10)]
    oms_dp_mock.write_attribute.assert_has_calls(oms_calls)
    zmx_dp_mock.write_attribute.assert_has_calls(zmx_calls)


@patch('readMotor.file_reader')
def test_read_dat_file(file_read_mock):
    file_read_mock.return_value = ['EH1A.01,oms:attr1,4.3,oms:attr2,7,zmx:attr1,12,zmx:attr2,756\n',
                                   'EH1A.03,oms:attr1,1.0,oms:attr2,43,zmx:attr1,6,zmx:attr2,793\n'
                                   ]

    all_params = read_dat('motor_date.params')
    file_read_mock.assert_called_with('motor_date.params')
    assert all_params == {'EH1A.01': {'oms:attr1': 4.3, 'oms:attr2': 7,
                                      'zmx:attr1': 12, 'zmx:attr2': 756},
                          'EH1A.03': {'oms:attr1': 1.0, 'oms:attr2': 43,
                                      'zmx:attr1': 6, 'zmx:attr2': 793}
                          }


@patch('readMotor.datetime')
@patch('readMotor.file_writer')
def test_write_dat_file(file_write_mock, date_mock):
    now = Mock()
    now.year = 2019
    now.month = 4
    now.day = 14
    now.hour = 23
    now.minute = 52
    now.second = 5
    date_mock.today.return_value = now

    reduced_attr = ['oms:attr1', 'zmx:attr2']

    write_dat({'EH1A.01': {'oms:attr1': 4, 'oms:attr2': 7,
                           'zmx:attr1': 12, 'zmx:attr2': 756},
               'EH1A.03': {'oms:attr1': 1, 'oms:attr2': 43,
                           'zmx:attr1': 6, 'zmx:attr2': 793}
               }, reduced_attr)

    file_writer_calls = [call(['EH1A.01,oms:attr1,4,oms:attr2,7,zmx:attr1,12,zmx:attr2,756\n',
                               'EH1A.03,oms:attr1,1,oms:attr2,43,zmx:attr1,6,zmx:attr2,793\n'
                               ], 'motors-20190414_235205.params'),
                         call(['EH1A.01,oms:attr1,4,zmx:attr2,756\n',
                               'EH1A.03,oms:attr1,1,zmx:attr2,793\n'
                               ], 'motors-20190414_235205_reduced.params')]
    file_write_mock.assert_has_calls(file_writer_calls)


@patch('readMotor.write_dat')
@patch('readMotor.read_parameters')
@patch('readMotor.DeviceProxy')
@patch('readMotor.parse_args')
def test_main(args_p_mock, dp_mock, read_params_mock, writer_mock):
    args_p_mock.return_value = {'beamline': 'p02',
                                'tango_host': 'haspp02oh1:10000',
                                'server': 'EH1A',
                                'dev_ids': [1,3]}
    read_params_mock.return_value = {'oms:attr1': 4, 'oms:attr2': 4,
                                     'zmx:attr1': 4, 'zmx:attr2': 4}

    main()
    dp_mock.assert_has_calls([call('haspp02oh1:10000/p02/motor/EH1A.01'),
                              call('haspp02oh1:10000/p02/ZMX/EH1A.01')])
    writer_mock.assert_called_with({'EH1A.01': {'oms:attr1': 4, 'oms:attr2': 4,
                                                'zmx:attr1': 4, 'zmx:attr2': 4},
                                    'EH1A.03': {'oms:attr1': 4, 'oms:attr2': 4,
                                                'zmx:attr1': 4, 'zmx:attr2': 4}
                                    })
