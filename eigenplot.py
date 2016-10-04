#! /usr/local/bin/python3

import sys
import numpy
import time
import scipy.linalg
import matplotlib.pyplot as plt

data = open(sys.argv[1],"r")
data = data.readlines()
data = [i.split() for i in data]
data = [[float(j) for j in i][0] for i in data]
x = numpy.linspace(1,4096,4096)
plt.plot(x,data)
plt.show()

