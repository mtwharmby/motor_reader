#from PyTango import DeviceProxy


''' This is the list of parameters for ZMX and OMSvme respectively which will be read/written'''
_parameters_list = {'zmx': [],
                    'oms': []}


def read_parameters(zmx_dp, oms_dp):
    '''
    Reads the motor parameters listed in _parameters_list by querying the specified zmx and oms Tango servers
    '''
    motor_params = {}

    for param in _parameters_list['zmx']:
        param_name = '{0}:{1}'.format(param, 'zmx')
        motor_params[param_name] = zmx_dp.read_attribute(param)

    for param in _parameters_list['oms']:
        param_name = '{0}:{1}'.format(param, 'oms')
        motor_params[param_name] = oms_dp.read_attribute(param)

    return motor_params


def main():
    pass
    # ForEach motor:
    # - Create DeviceProxies
    # - read_parameters
    # - write_dat
    # - write_readable_table
