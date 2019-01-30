from PyTango import *
import sys
import time


def create_motor_tuple(moto, motoZ, strG):
    attr1 = moto.read_attribute("Acceleration")  # Rename attrs
# print "moto, value ", attr1.value
    attr2 = moto.read_attribute("Conversion")

    attr3 = moto.read_attribute("BaseRate")
    # print "moto, value ", attr3.value
    attr4 = moto.read_attribute("SlewRate")
    attr5 = moto.read_attribute("SlewRateMax")
    attr6 = motoZ.read_attribute("RunCurrent")
    attr7 = motoZ.read_attribute("StopCurrent")
    attr8 = motoZ.read_attribute("AxisName")

    return (strG, attr1.value, attr2.value, attr3.value, attr4.value,
            attr5.value, attr6.value, attr7.value, attr8.value)


if __name__ == '__main__':
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
        motx = create_motor_tuple(moto, strG)

        out.write('%s\t\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t\t%.5f\t\t%s\n' % motX)

        # listX=[]
        listX.append(motX)

    # print listX
    # return [listX]
    out.close
