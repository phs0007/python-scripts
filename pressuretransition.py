
####################################################################################################
#                                                                                                  #
#    Script Name:  pressuretransition.py                                                           #
#                                                                                                  #
#    Author(s):  Paul H. Sanders and Jianjun Dong                                                  #
#                Auburn University Physics Department                                              #
#                                                                                                  #
#    What the heck does this do?                                                                   #
#       This script takes two materials and finds the transition pressure                          #
#                                                                                                  #
#    Input: 1. VPEH***.out_*** data for two materials                                              #
#                                                                                                  #
#    Output: 1. Transition Pressure between two materials                                          #
#                                                                                                  #
#    Dates: 1. PHS September 17, 2016                                                              #
#                                                                                                  #
####################################################################################################

import os
import fnmatch
import numpy
import textwrap
#import matplotlib.pyplot as plt
from scipy import interpolate, optimize

def main():
    eos, material1, material2 = display1()
    solutions = findprestransition(material1, material2, eos)
    output(solutions, eos)

######################################################

def getcolumn(data,a,b):
    data1 = numpy.array([[i[a],i[b]] for i in data])
    data1 = data1[numpy.argsort(data1[:,0])]
    xval = numpy.array([i[0] for i in data1])
    yval = numpy.array([i[1] for i in data1])
    return xval,yval

def findprestransition(material1,material2,eoschoice):
    sol = numpy.zeros((len(eoschoice)))
    for i, eos in enumerate(eoschoice):
        # get data
        data1 = numpy.genfromtxt("VPEH{}.out_{}".format(eos, material1))
        data2 = numpy.genfromtxt("VPEH{}.out_{}".format(eos, material2))
        xval1,yval1 = getcolumn(data1,1,3)
        xval2,yval2 = getcolumn(data2,1,3)

        # find pressure range
        totalxval = numpy.concatenate((xval1,xval2))
        min = numpy.amin(totalxval)
        max = numpy.amax(totalxval)
        xnew = numpy.linspace(min,max,1000)

        # create interpolating functions to match incoming data for both materials
        f1 = interpolate.UnivariateSpline(xval1, yval1, s=0)
        f2 = interpolate.UnivariateSpline(xval2, yval2, s=0)

        # solve for intersection point
        def fcombine(v):
            return f1(v) - f2(v)
        sol[i] = optimize.root(fcombine,0).x[0]
    return sol

def deleteduplicates(array):
    barray = [array[0]]    
    for i in array:
       k = 0
       for j in barray:
          if i == j:
              k+=1
       if k == 0:
           barray.append(i)
    return barray

def display1():
    workingdir = os.getcwd()
    files = [i for i in os.listdir(workingdir) if fnmatch.fnmatch(i,"VPEH*.out_*")]
    eoschoices = deleteduplicates([i[4:7] for i in files])
    choiceofmaterial = deleteduplicates([i.rsplit("_")[-1] for i in files])
    text = "It looks like we found minerals to compare. Please select which mineral you would like to use: (A number will suffice)"
    for i in textwrap.wrap(text, width=70, initial_indent="     ", subsequent_indent="   "):
        print (i)
    for i, value in enumerate(choiceofmaterial):
        print("\n  {}.  {}".format(i+1, value))
    print ("") 
    print (40 * '-')
    mineral1 = int(input("3. Which choice will you select? (Enter a number):\n Desired Choice: "))
    material1 = choiceofmaterial[mineral1-1]
    del choiceofmaterial[mineral1-1]
    text = "Now selected the second material to compare: (A number will suffice)"
    for i in textwrap.wrap(text, width=70, initial_indent="     ", subsequent_indent="   "):
        print (i)
    for i, value in enumerate(choiceofmaterial):
        print("\n  {}.  {}".format(i+1, value))
    print ("")
    print (40 * '-')
    mineral2 = int(input("4. Which choice will you select? (Enter a number):\n Desired Choice: "))
    material2 = choiceofmaterial[mineral2-1]
    print ("")
    print (40 * '-')
    print ("")
    text = "Which eos would you like to use?: (A number will suffice)"
    print("\n  0.  all".format(i+1, value))
    for i, value in enumerate(eoschoices):
        print("\n  {}.  {}".format(i+1, value))
    print ("")
    print (40 * '-')
    eos = input("3. Which choice will you select? (Enter a number):\n Desired Choice: ")
    if eos == "0":
        eos = [i for i in eoschoices]
    else:
        eos = eos.rsplit()
        eos = [int(i) for i in eos]
        eos = [eoschoices[i-1] for i in eos]
    return eos, material1, material2

def output(solutions,eos):
    for i, solution in enumerate(solutions):
        print("The indicated pressure transition point is : {} for {} ".format(round(solution,3), eos[i]))

#############################################

if __name__ == '__main__':
    main()
    




        