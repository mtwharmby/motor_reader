import sys
import argparse
import math
import itertools

from datetime import datetime

try:
    from PyTango import DeviceProxy, DevFailed
except ModuleNotFoundError:
    print("WARNING: No PyTango module imported!\n\nIgnore if testing")
    DeviceProxy = None


# Need python 3.5 to use math.nan
if sys.version_info <= (3, 5):
    print('readMotor.py requires python version 3.5 (or higher)')
    sys.exit(1)


''' This is the list of parameters for ZMX and OMSvme respectively which will
 be read/written'''
_parameters_list = {'zmx': ['StopCurrent', 'RunCurrent',
                            'PreferentialDirection', 'StepWidth', 'DelayTime',
                            'AxisName', 'InputLogicLevel','Deactivation',
                            'Overdrive', 'PathOutputFiles'],
                    'oms': ['Acceleration', 'BaseRate', 'Conversion',
                            'SettleTime', 'SlewRate', 'SlewRateMax',
                            'SlewRateMin', 'StepBacklash', 'StepCalibration',
                            'StepCalibrationUser', 'StepLimitMax',
                            'StepLimitMin', 'StepPositionInternal',
                            'StepPositionController', 'UnitBacklash',
                            'UnitCalibration', 'UnitCalibrationUser',
                            'UnitLimitMax', 'UnitLimitMin', 'DerivativeGain',
                            'IntegralGain', 'ProportionalGain',
                            'FlagProtected', 'Position', 'FlagEncoderHomed',
                            'ConversionEncoder', 'HomePosition',
                            'FlagUseEncoderPosition', 'FlagClosedLoop',
                            'SlewRateCorrection', 'StepDeadBand',
                            'CorrectionGain', 'SlipTolerance', 'CutOrMap',
                            'FlagInvertEncoderDirection',
                            'FlagCheckZMXActivated']}                 
_beamline = 'p02'
_tango_host = 'haspp02oh1:10000'
_servers = {'EH1A': 64, 'EH1B': 16}

_reduced_attr = []


def make_reduced_attribs():
    # TODO FIXME Needs a test!
    for dev_proxy, attribute_list in _parameters_list.items():
        for attr in attribute_list:
            _reduced_attr.append('{}:{}'.format(dev_proxy, attr))


def parse_args(user_args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--beamline', '-b', default=_beamline)
    parser.add_argument('--tango-host', dest='tango_host', default=_tango_host)
    parser.add_argument('--server', '-s', required=True)
    # At somepoint we could make server not required, default to the all the 
    # keys in the _servers dict. But that needs more refactoring
    parser.add_argument('--write', default=False)
    parser.add_argument('dev_ids', default=None, nargs='?')

    args = parser.parse_args(user_args)
    config = {'beamline': args.beamline,
              'tango_host': args.tango_host,
              'server': args.server}

    if args.write:
        config['write_params'] = True
        config['input_file'] = args.write
    else:
        config['write_params'] = False

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
        dev_ids = list(range(1, _servers[server] + 1))

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
            except DevFailed:
                print('INFO: Value of {} ({}) is undefined. Saved as nan.'.format(attrib, dev_proxy.dev_name()))
                motor_params[label] = math.nan
            except UnicodeDecodeError:
                print('WARNING: Cannot read value of {} ({}). Saved as nan.'.format(attrib, dev_proxy.dev_name()))
                motor_params[label] = math.nan

    return motor_params


def write_parameters(oms_dp, zmx_dp, attribs_to_write, reduced_params_list=_reduced_attr, retry=False, raise_errors=False, written_attribs=None):
    old_attribs = {}
    # This ensures that written_attribs is an empty list if the function is
    # called without arguments a second time. Otherwise test doesn't pass.
    if not written_attribs:
        written_attribs = []
    # Taken from jive. DelayTime value reported cannot be written back
    # directly. Needs to be mapped.
    DelayTime_map = {1: 0, 2: 1, 4: 2, 6: 3, 8: 4, 10: 5, 12: 6, 14: 7, 16: 8,
                     20: 9, 40: 10, 60: 11, 100: 12, 200: 13, 500: 14,
                     1000: 15}
    dev_proxy = None

    try:  # TODO Move this inside the for-loop. That way we can retry a single attribute and then continue with the rest of the list.
        for attrib in attribs_to_write.keys():
            # Only write the parameter if it's in the reduced_params_list...
            if attrib not in reduced_params_list:
                continue

            attr_class, attr_name = attrib.split(':')
            # ...and it's previously been written and not called 'Deactivation'
            if (attr_name in written_attribs) or attr_name == 'Deactivation':
                continue

            # Create a device proxy depending whether this is an OMS of ZMX attribute
            if attr_class == 'oms':
                dev_proxy = oms_dp
            elif attr_class == 'zmx':
                dev_proxy = zmx_dp
            else:
                print('ERROR: Unrecognised device class {}'.format(attr_class))
                raise Exception('Unrecognised device class')  # FIXME Should be a specific error

            # Read and store the initial value of the parameter...
            old_attribs[attrib] = dev_proxy.read_attribute(attr_name)
            # ...then write the new value
            # For DelayTime we have to map from 4-bit or something...
            if attr_name == 'DelayTime':  # FIXME Add to test!
                attribs_to_write[attrib] = DelayTime_map[attribs_to_write[attrib]]
            dev_proxy.write_attribute(attr_name, attribs_to_write[attrib])
            written_attribs.append(attr_name)

        eprom_write = zmx_dp.WriteEPROM()
        if eprom_write != 1:
            print('ERROR: Failed writing EPROM for {}. Aborting'.format(zmx_dp.name()))
            raise Exception('Writing to EPROM failed')  # FIXME Should be a specific error

    except Exception as ex:  # FIXME This ought to be a specific error
        # FIXME This bit doesn't get tested
        if raise_errors:
            # We have been told to push the error up, so do so!
            raise ex
        if retry:
            # This is already the second time... we should abandon this and give up.
            # We try to undo what we did.
            print('ERROR: Could not write to {}:\n{}\n\n. Attempting to revert changes...'.format(dev_proxy.name(), str(ex)))
            write_parameters(oms_dp, zmx_dp, old_attribs, raise_errors=True)
            # As things have gone wrong, stop any further execution
            print('Reverted successfully. Aborting due to previous error.')
            sys.exit(1)
        else:
            # This is the first attempt. We try a second time (in case this was a transient corba error)
            print('WARNING: An error occurred while writing to {}. Retrying...'.format(dev_proxy.name()))
            write_parameters(oms_dp, zmx_dp, attribs_to_write, retry=True, written_attribs=written_attribs)


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
            if string == 'nan':
                return math.nan
            return int(string)
        except ValueError:
            # Maybe it wasn't an int. Try a string.
            # If we error this time, it gets raised
            return float(string)

    in_lines = file_reader(filename)

    all_params = {}
    for line in in_lines:
        line = line.rstrip().rstrip(',').split(',')
        assert len(line) % 2 != 0  # There should be n k,v pairs + the device name (odd number of entries in list)

        attribs = {}
        attrib_list = line[1:]
        for i in range(int(len(attrib_list) / 2)):

            if attrib_list[2*i] == 'zmx:AxisName':
                # AxisName is a string. Don't try to conver to number
                attribs[attrib_list[i*2]] = attrib_list[2*i+1]
            else:
                attrib_val = None
                try:
                    attrib_val = string_to_numeric(attrib_list[2*i+1])
                except ValueError:
                    print('Motor{} ({}): String {} cannot be converted to int or float. Aborting!'.format(line[0], attrib_list[i*2], attrib_list[2*i+1]))
                    sys.exit(1)

                if attrib_val == math.nan:
                    # We don't want to try writing NaNs...
                    continue
                attribs[attrib_list[i*2]] = attrib_val

        all_params[line[0]] = attribs

    return all_params


def write_dat(all_params, reduced_params_list=_reduced_attr):
    def merge_line_list(line):
        joined_line = ','.join(line)
        return joined_line+'\n'

    out_lines_full = []
    out_lines_red = []
    for device, attributes in sorted(all_params.items()):
        line_full = [device]
        line_red = [device]
        for attr, value in sorted(attributes.items()):
            line_full.append('{},{}'.format(attr, value))
            if attr in reduced_params_list:
                line_red.append('{},{}'.format(attr, value))

        out_lines_full.append(merge_line_list(line_full))
        out_lines_red.append(merge_line_list(line_red))

    now = datetime.today()

    params_filename = 'motors-{0:04d}{1:02d}{2:02d}_{3:02d}{4:02d}{5:02d}.params'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    file_writer(out_lines_full, params_filename)

    reduced_params_filename = 'motors-{0:04d}{1:02d}{2:02d}_{3:02d}{4:02d}{5:02d}_reduced.params'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    file_writer(out_lines_red, reduced_params_filename)


def main():
    # Find out what we're supposed to be doing...
    config = parse_args(sys.argv[1:])
    # ...and set up the reduced set of parameters we're interested in.
    make_reduced_attribs()

    # Construct all the names of the motors we're interested in
    dev_names = generate_device_names(config['server'], config['dev_ids'])

    if config['write_params']:
        input_motor_params = read_dat(config['input_file'])

        # We check that all of the motors we are interested in have an entry in our input file
        all_motors = set(itertools.chain.from_iterable(dev_names.values()))
        motors_with_params = set(input_motor_params.keys())
        motors_to_update = list(all_motors & motors_with_params)
        # The input file should contain only motors which are on the given
        # server or, the input file should contain parameters for all motors
        # when device IDs have been specified.
        if set(motors_with_params).issubset(all_motors) or (bool(config['dev_ids']) and all_motors.issubset(motors_with_params)):
            for motor in sorted(motors_to_update):
                oms_dp = DeviceProxy('{}/{}/motor/{}'.format(config['tango_host'], config['beamline'], motor))
                zmx_dp = DeviceProxy('{}/{}/ZMX/{}'.format(config['tango_host'], config['beamline'], motor))
                print('Writing config to motor {}'.format(motor))
                write_parameters(oms_dp, zmx_dp, input_motor_params[motor])
                print('{}: DONE'.format(motor))
            print('\nSuccessfully updated configuration for motors:\n{}'.format(', '.join(sorted(motors_to_update))))
        else:
            print('ERROR: Configuration for one or more of the requested motors is not in the input file.\nAborting...')
            sys.exit(1)
    else:
        all_motor_params = {}
        # For each motor in the list, make Tango servers and query them for information
        for server in sorted(dev_names.keys()):
            for motor in dev_names[server]:
                oms_dp = DeviceProxy('{}/{}/motor/{}'.format(config['tango_host'], config['beamline'], motor))
                zmx_dp = DeviceProxy('{}/{}/ZMX/{}'.format(config['tango_host'], config['beamline'], motor))
                print('Reading parameters for motor {}...'.format(motor))
                all_motor_params[motor] = read_parameters(oms_dp, zmx_dp)
                print('{}: DONE'.format(motor))
            print('\nSuccessfully read configurations for motors:\n{}'.format(', '.join(dev_names[server])))

        write_dat(all_motor_params)


if __name__ == "__main__":
    main()
