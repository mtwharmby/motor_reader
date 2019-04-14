import pytest
from mock import call, Mock, patch

from readMotor import (parse_args, read_parameters, generate_device_names, 
                       read_dat, write_dat, file_writer, main)


def test_parse_args():
    # parse_args needs to return a dictionary, something like:
    eg_conf1 = {'beamline': 'p02',
                'tango_host': 'haspp02oh1:10000',
                'server': 'EH1A',
                'dev_ids': [1]}

    # An example aya.argv to encode this lot:
    eg_argv1 = ['-b', 'p02', '--tango-host', 'haspp02oh1:10000',
                '-s', 'EH1A', '1']
    assert parse_args(eg_argv1) == eg_conf1

    # An example requiring more defaulting
    eg_conf2 = {'beamline': 'p02',
                'tango_host': 'haspp02oh1:10000',
                'server': 'EH1A',
                'dev_ids': [12, 15, 32]}
    eg_argv2 = ['-s', 'EH1A', '12,15,32']
    assert parse_args(eg_argv2) == eg_conf2

    # Requires even more defaulting!
    eg_conf3 = {'beamline': 'p02',
                'tango_host': 'haspp02oh1:10000',
                'server': 'EH1A',
                'dev_ids': None}
    eg_argv3 = ['-s', 'EH1A']
    assert parse_args(eg_argv3) == eg_conf3


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
        dp.get_all_attributes.return_value = ['attr1', 'attr2']
        dp.read_attribute().value = 4

    motor_dict = read_parameters(oms_dp_mock, zmx_dp_mock)

    assert motor_dict == {'oms:attr1': 4, 'oms:attr2': 4,
                          'zmx:attr1': 4, 'zmx:attr2': 4}


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

    write_dat({'EH1A.01': {'oms:attr1': 4, 'oms:attr2': 7,
                           'zmx:attr1': 12, 'zmx:attr2': 756},
               'EH1A.03': {'oms:attr1': 1, 'oms:attr2': 43,
                           'zmx:attr1': 6, 'zmx:attr2': 793}
               })

    file_write_mock.assert_called_with(['EH1A.01,oms:attr1,4,oms:attr2,7,zmx:attr1,12,zmx:attr2,756\n',
                                        'EH1A.03,oms:attr1,1,oms:attr2,43,zmx:attr1,6,zmx:attr2,793\n'
                                        ], 'motors-20190414_235205.params')


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
