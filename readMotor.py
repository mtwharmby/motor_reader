try:
    from PyTango import DeviceProxy
except ModuleNotFoundError:
    print("WARNING: No PyTango module imported!\n\nIgnore if testing")
    PyTango = None


''' This is the list of parameters for ZMX and OMSvme respectively which will be read/written'''
_parameters_list = {'zmx': [],
                    'oms': []}
_beamline = 'p021'
_servers = {'EH1A': 64, 'EH1B': 16}


def generate_device_names(server, dev_ids=None, beamline=None):
    if not beamline:
        beamline = _beamline

    if dev_ids:
        if not isinstance(dev_ids, list):
            dev_ids = [dev_ids]
    else:
        dev_ids = list(range(_servers[server]))

    dev_names = {}
    for i in dev_ids:
        mot_name = '{}.{:02d}'.format(server, i)
        oms_zmx_names = {'oms': '{}/motor/{}'.format(beamline, mot_name),
                         'zmx': '{}/ZMX/{}'.format(beamline, mot_name)}
        dev_names[mot_name] = oms_zmx_names
    return dev_names
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
