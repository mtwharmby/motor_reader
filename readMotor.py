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


def parse_args(args):
    pass


def generate_device_names(server, dev_ids=None):
    '''
    Determines the names of the motor Tango servers associated with a given 
    server
    '''
    if dev_ids:
        if not (isinstance(dev_ids, list) or isinstance(dev_ids, tuple)):
            dev_ids = [dev_ids]
    else:
        dev_ids = list(range(1, _servers[server] + 1))  # Is the +1 needed?

    server_devs = {server: []}
    for i in dev_ids:
        mot_name = '{}.{:02d}'.format(server, i)
        server_devs[server].append(mot_name)
    return server_devs


def read_parameters(oms_dp, zmx_dp):
    '''
    Reads the motor parameters listed in _parameters_list by querying the 
    specified zmx and oms Tango servers
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
    # Find out what we're supposed to be doing...
    args = None  # FIXME!
    config = parse_args()

    # Construct all the names of the motors we're interested in
    dev_names = generate_device_names(config['server'], config['dev_ids'])

    # For each motor in the list, make Tango servers and query them for information
    all_motor_params = {}
    for server in sorted(dev_names.keys()):
        for motor in dev_names[server]:
            oms_dp = DeviceProxy('{}/{}/motor/{}'.format(config['tango_host'], config['beamline'], motor))
            zmx_dp = DeviceProxy('{}/{}/ZMX/{}'.format(config['tango_host'], config['beamline'], motor))
            # all_motor_params[motor] = read_parameters(oms_dp, zmx_dp)

    # write_dat(all_motor_params)  # TODO

    # ForEach motor:
    # - Create DeviceProxies
    # - read_parameters
    # - write_dat
    # - write_readable_table
