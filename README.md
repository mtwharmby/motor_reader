# motor_reader

[![Build Status](https://travis-ci.com/mtwharmby/motor_reader.svg?branch=master)](https://travis-ci.com/mtwharmby/motor_reader)

motor_reader reads the current values of a set of attributes of the ZMX and OMSvme Tango servers. These values are then
written to two files:
- a human readable table
- a computer readable dat file

motor_reader can also read the content of a properly structured dat file and write it's contents to the ZMX and OMSvme Tango servers of a given motor.

The current set of parameters which are read are:
- Acceleration
- Conversion
- BaseRate
- SlewRate
- SlewRateMax
- RunCurrent
- StopCurrent
- AxisName'

> This project is in an early stage of development and should be used with caution


## Usage

For example

```
$ cd motor_reader
$ python3 motor_reader.py ARG1 ARG2
Some output
```


## Installation

motor_reader requires

* python >= 3.5
* some_dependency

Download the latest release and extract it. Optionally run

```
$ cd motor_reader
$ pip3 install .
```


## Contribution

Please feel free to open issues or pull requests.
