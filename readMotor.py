import sys
import argparse
import math

from datetime import datetime

try:
    from PyTango import DeviceProxy, DevError
except ModuleNotFoundError:
    print("WARNING: No PyTango module imported!\n\nIgnore if testing")
    DeviceProxy = None


''' This is the list of parameters for ZMX and OMSvme respectively which will
 be read/written'''
_parameters_list = {'zmx': [],
                    'oms': []}
_beamline = 'p02'
_tango_host = 'haspp02oh1:10000'
_servers = {'EH1A': 64, 'EH1B': 16}


def parse_args(user_args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--beamline', '-b', default=_beamline)
    parser.add_argument('--tango-host', dest='tango_host', default=_tango_host)
    parser.add_argument('--server', '-s', required=True)
    # At somepoint we could make server not required, default to the all the 
    # keys in the _servers dict. But that needs more refactoring
    parser.add_argument('dev_ids', default=None, nargs='?')

    args = parser.parse_args(user_args)
    config = {'beamline': args.beamline,
              'tango_host': args.tango_host,
              'server': args.server}

    if args.dev_ids:
        try:
            dev_ids = list(map(lambda x: int(x), args.dev_ids.split(',')))
        except ValueError:
            print('Unexpected value for device IDs. Should be a comma separated list of integers')
            sys.exit(1)
    else:
        dev_ids = None

    config['dev_ids'] = dev_ids
    return config


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
    Returns a dictionary containing the values of all the attributes
    '''
    motor_params = {}

    for prefix, dev_proxy in {'oms': oms_dp, 'zmx': zmx_dp}.items():
        all_attributes = dev_proxy.get_attribute_list()
        for attrib in all_attributes:
            label = '{}:{}'.format(prefix, attrib)
            try:
                motor_params[label] = dev_proxy.read_attribute(attrib).value
            except DevError:
                motor_params[label] = math.nan

    return motor_params


def file_reader(filename):
    with open(filename, 'r') as in_file:
        return in_file.readlines()


def file_writer(input_lines, filename):
    with open(filename, 'w') as out_file:
        out_file.writelines(input_lines)
        out_file.flush()


def read_dat(filename):
    def string_to_numeric(string):
        try:
            return int(string)
        except ValueError:
            try:
                return float(string)
            except ValueError:
                print('String {} cannot be converted to int or float. Aborting!'.format(string))
                sys.exit(1)

    in_lines = file_reader(filename)

    all_params = {}
    for line in in_lines:
        line = line.rstrip().split(',')
        assert len(line) % 2 != 0  # There should be n k,v pairs + the device name (odd number of entries in list)

        attribs = {}
        attrib_list = line[1:]
        for i in range(int(len(attrib_list) / 2)):
            attribs[attrib_list[i*2]] = string_to_numeric(attrib_list[2*i+1])

        all_params[line[0]] = attribs

    return all_params


def write_dat(all_params):
    out_lines = []
    for device, attributes in sorted(all_params.items()):
        line = [device]
        for attr, value in sorted(attributes.items()):
            line.append('{},{}'.format(attr, value))

        joined_line = ','.join(line)
        out_lines.append(joined_line+'\n')

    now = datetime.today()
    print(now.year)
    params_filename = 'motors-{0:04d}{1:02d}{2:02d}_{3:02d}{4:02d}{5:02d}.params'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)

    file_writer(out_lines, params_filename)


def main():
    # Find out what we're supposed to be doing...
    config = parse_args(sys.argv[1:])

    # Construct all the names of the motors we're interested in
    dev_names = generate_device_names(config['server'], config['dev_ids'])

    # For each motor in the list, make Tango servers and query them for information
    all_motor_params = {}
    for server in sorted(dev_names.keys()):
        for motor in dev_names[server]:
            oms_dp = DeviceProxy('{}/{}/motor/{}'.format(config['tango_host'], config['beamline'], motor))
            zmx_dp = DeviceProxy('{}/{}/ZMX/{}'.format(config['tango_host'], config['beamline'], motor))
            all_motor_params[motor] = read_parameters(oms_dp, zmx_dp)

    write_dat(all_motor_params)

    # ForEach motor:
    # - Create DeviceProxies
    # - read_parameters
    # - write_dat
    # - write_readable_table

if __name__ == "__main__":
    main()