from PyTango import *
import sys
import time

listX = []
n = 0
server = 'EH2B'  # Arg
out = open('motorDAT.txt', 'w')  # Filename as arg?
out.write('DeviceName\t\t\tAcceleration\tConversion\tBaseRate\tSlewRate\tSlewRateMax\tRunCurrent\tStopCurrent\tAxisName\n')


for n in range(1, 48):
    if n >= 10:
        str1 = 'p022/motor/'+server+'.'  # OMSVME
    else:
        str1 = 'p022/motor/'+server+'.0'
    if n >= 10:
        str2 = 'p022/ZMX/'+server+'.'  # ZMX
    else:
        str2 = 'p022/ZMX/'+server+'.0'

    strG = '%s%i' % (str1, n)  # Change to python3 style format string
    strH = '%s%i' % (str2, n)
    moto = DeviceProxy(strG)
    motoZ = DeviceProxy(strH)
    attribs = ['Acceleration', 'Conversion', 'BaseRate', 'SlewRate',
               'SlewRateMax', 'RunCurrent', 'StopCurrent', 'AxisName']
    for attr_name in attribs:
        line = line + moto.read_attribute(attr_name)
#     motor_attrs['accel'] = moto.read_attribute("Acceleration")  # Rename attrs
# # print "moto, value ", attr1.value
#     motor_attrs['conv'] = moto.read_attribute("Conversion")
#
#     motor_attrs['BaseRate'] = moto.read_attribute("BaseRate")
#     # print "moto, value ", attr3.value
#     motor_attrs['SlewRate'] = moto.read_attribute("SlewRate")
#     motor_attrs['SlewRateMax'] = moto.read_attribute("SlewRateMax")
#     motor_attrs['RunCurr'] = motoZ.read_attribute("RunCurrent")
#     motor_attrs['StopCurr'] = motoZ.read_attribute("StopCurrent")
#     motor_attrs['alias'] = motoZ.read_attribute("AxisName")


    motX = strG, attr1.value, attr2.value, attr3.value, attr4.value,
        attr5.value, attr6.value, attr7.value, attr8.value
    out.write('%s\t\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t\t%.5f\t\t%s\n' % motX)

    # listX=[]
    listX.append(motX)

# print listX
# return [listX]
out.close
