#! /usr/local/bin/python3

###############################################
#
#    script: eigenvalue.py
#    
#    Author: Paul Sanders (phs0007@auburn.edu)
#
#    Purpose: Find Density of States from Dynamical 
#             Matrix
#
#    Date: 1. PHS September 29, 2016
#
###############################################

import sys
import numpy
import scipy.linalg
import matplotlib.pyplot as plt

def main():
    length, array = get_array(sys.argv[1])
    eigenvalues = eigens(array)
    x = numpy.linspace(0,1,1000)
    sigma = 0.001
    y = rho(x, eigenvalues, sigma, length)
    plt.plot(x,y)
    plt.show()

    # If you want to plot...
    #output = open("fileout.out","w")
    #for i in eigenvalues:
    #    output.write(str(i)+"\n")
    #output.close()






###############################################

def get_array(file):
    data = open(file,"r")
    data = data.readlines()
    data = [i.split() for i in data]
    dynam_data = data[1:]
    length = int(data[0][0])

    for i, value in enumerate(dynam_data):
        for j, value2 in enumerate(value):
            if j < 2: 
                dynam_data[i][j] = int(dynam_data[i][j])
            else:
                dynam_data[i][j] = float(dynam_data[i][j])

    array = numpy.zeros((length,length))

    for i in dynam_data:
        x = int(i[0])
        y = int(i[1])
        val = i[2]
        array[x-1][y-1] = val
        array[y-1][x-1] = val
 
    return length, array
    

def eigens(array):
    eigens = scipy.linalg.eigvalsh(array)

    for i, value in enumerate(eigens):
        if value < 0:
             eigens[i] = 0
    
    eigens = numpy.sqrt(eigens)

    return eigens

def gaussian(x, lam, sigma, N):
    return numpy.exp(-(x - lam)**2/sigma**2)/(sigma*N*numpy.sqrt(2*numpy.pi))

def rho(x, eigenvalues, sigma, N):
    func = 0
    for lam in eigenvalues:
        func = func + gaussian(x, lam, sigma, N)
    return func

##############################################  

if __name__ == "__main__":
    main()


