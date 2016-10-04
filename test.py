#! /usr/local/bin/python3

###############################################
#
#    script: eigenvalue_vasp.py
#    
#    Author: Paul Sanders (phs0007@auburn.edu)
#
#    Purpose: Calculate Phonon Free Energy From
#             Density of States
#
#    Date: 1. PHS October 3, 2016
#
###############################################

import sys
import numpy

"""
density_of_states = import_data(sys.argv[1])
temp = numpy.linspace(0,1000,1001)
free_energy = get_free_energy(temp, density_of_states)
energy = get_energy(temp, density_of_states)
entropy = get_entropy(temp, free_energy, energy)
output_results(temp, free_energy, energy, entropy)
"""

###############################################

def import_data(file):
    data = open(file,"r")
    data = data.readlines()
    data = [i.split() for i in data]
    dosvalues = data[1:]
    dosvalues = numpy.array([[float(i) for i in j] for j in dosvalues])
    return dosvalues

def get_free_energy(temp, density_of_states):
    hbar = 1
    kb = 1
    free_energy = 0
    for i in density_of_states:
        omega = i[0]
        density = i[1]
        x = hbar * omega / ( kb * temp ) 
        log_arg = 1 - numpy.exp(-x)
        free_energy = free_energy + density * (hbar * omega * 0.5 + kb * temp * numpy.log(log_arg))
    return free_energy

def get_energy(temp, density_of_states):
    hbar = 1
    kb = 1
    energy = 0
    for i in density_of_states:
        omega = i[0]
        density = i[1]
        x = hbar * omega / ( kb * temp ) 
        if x > 1 * 10 ^ 30:
            n = 0
        else:
            n = 1 / (numpy.exp(x) - 1)
        energy = energy + density * (hbar * omega * 0.5 + n)
    return energy













