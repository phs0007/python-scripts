####################################################################################################
#                                                                                                  #
#    Script Name:  poscar_gen.py                                                                   #
#                                                                                                  #
#    Author(s):  Paul Sanders                                                                      #
#                Auburn University Physics Department                                              #
#                                                                                                  #
#    What the heck does this do?                                                                   #
#       This script Supercell-rizes a POSCAR file in the direct format                             #
#                                                                                                  #
#    Input: 1. System Arguments (this includes POSCAR file)                                        #
#                                                                                                  #
#    Output: 1. New Supercell Poscar file                                                          #
#                                                                                                  #
#    Dates:                                                                                        #
#    	Created on August 24, 2016                                                                 #
#       Updated by PS on August 26                                                                 #
#       Updated by JJD on August 26                                                                #
#       Updated by PS on August 26                                                                 #
#       Updated by PS on August 29                                                                 #
#                                                                                                  #
####################################################################################################

import sys
import numpy

def main():

    # get things from POSCAR
    welcome()
    pos = getcasesandT()[0]
    icase = getcasesandT()[1]
    T = getcasesandT()[2]
    data = getinfofromfile()[0]
    datasplit = getinfofromfile()[1]
    latconstant = getinfofromfile()[2]
    unit_lattice = getinfofromfile()[3]
    volume = getinfofromfile()[4]
    inverse_lattice = getinfofromfile()[5]
    line_at = checkstyle(datasplit)[0]
    istyle = checkstyle(datasplit)[1]
    iformat = checkformat(line_at,datasplit)

    # case 0: print volume
    if icase == 0:
        icase0(volume)

    # case 1: covert between direct and cartesian
    if icase == 1:
        icase1(iformat, data, datasplit, line_at, unit_lattice, inverse_lattice)

    # case 2: determine the new volume size
    if icase == 2:
        icase2(pos, volume, latconstant, data)

    # case 3-6: get supercell from T matrix
    if icase > 2:
        icasegt2(T, line_at, datasplit, data)

##################################

def welcome():
    print ("Welcome to poscar_gen.py, a python code to analyze"
           " and/or transform POSCAR file in the DIRECT format")
    return 1

def getcasesandT():
    pos = [float(i) for i in sys.argv[2:]]
    dimT = len(pos)
    if dimT == 0:
        icase = 0
        T = 0
    elif dimT == 1:
        if pos[0] == 0:
            icase = 1
            T = 0
        elif pos[0] < 0:
            icase = 2
            T = 0
        else:
            icase = 3
            T = pos1toT(pos)
    elif dimT == 3:
        icase = 4
        T = pos3toT(pos)
    elif dimT == 9:
        icase = 5
        T = pos9toT(pos)
    else:
        sys.exit("I don't understand the request for the supercell size.")
    return pos, icase, T

def getinfofromfile():
    data = open(sys.argv[1], "r").readlines()
    datasplit = [i.rsplit() for i in data]
    latconstant = float(datasplit[1][0])
    unit_lattice = numpy.array([[float(j) for j in datasplit[i]] for i in range(2, 5)])
    volume = numpy.cross(unit_lattice[0], unit_lattice[1]).dot(unit_lattice[2])
    volume = volume * latconstant ** 3
    inverse_lattice = numpy.transpose(T2R(unit_lattice))
    inverse_lattice = inverse_lattice / volume
    return data,datasplit,latconstant,unit_lattice,volume,inverse_lattice

def checkstyle(datasplit):
    try:
        num_atoms = numpy.array([int(x) for x in datasplit[5]])
        line_at = 6
        istyle = 1
    except ValueError:
        symbols = [x for x in datasplit[6]]
        num_atoms = numpy.array([int(x) for x in datasplit[6]])
        line_at = 7
        istyle = 2
    return line_at, istyle

def checkformat(line_at,datasplit):
    if "d" in datasplit[line_at][0].lower():
        iformat = 1
        print('We think the POSCAR is using DIRECT format.')
    elif "c" in datasplit[line_at][0].lower():
        iformat = 2
        print('We think the POSCAR is using CARTESIAN format.')
    else:
        sys.exit("I cannot tell the form, either Direct or Cartesian.")
    return iformat

def T2R(T):
    R1 = numpy.cross(T[1],T[2])
    R2 = numpy.cross(T[2],T[0])
    R3 = numpy.cross(T[0],T[1])
    return numpy.concatenate(([R1],[R2],[R3]))

def pos1toT(pos):
    T = numpy.array([[pos[0],0,0],[0,pos[0],0],[0,0,pos[0]]])
    return T

def pos3toT(pos):
    T = numpy.array([[pos[0],0,0],[0,pos[1],0],[0,0,pos[2]]])
    return T

def pos9toT(pos):
    T = numpy.array([[pos[0],pos[1],pos[2]],[pos[3],pos[4],pos[5]],[pos[6],pos[7],pos[8]]])
    return T

def V2A(lattice,u,v,w):
    x = u * lattice[0][0] + v * lattice[1][0] + w * lattice[2][0]
    y = u * lattice[0][1] + v * lattice[1][1] + w * lattice[2][1]
    z = u * lattice[0][2] + v * lattice[1][2] + w * lattice[2][2]
    return numpy.array([x ,y ,z])

def icase0(volume):
    print ("")
    print (40 * "-")
    print ("Volume = {}".format(volume))
    print ("\n  Program Finished ...  \n")
    print (40 * "-")
    sys.exit()

def icase1(iformat,data,datasplit,line_at,unit_lattice,inverse_lattice):
    if iformat == 1:
        dir_output = open("supercell_direct.dat", "w")
        for i in data:
            dir_output.write(i)
        dir_output.close()
        car_output = open("supercell_cartesian.dat", "w")
        for i in range(line_at):
            car_output.write(data[i])
        car_output.write("Cartesian\n")
        atom_pos = numpy.array([[float(j) for j in i] for i in datasplit[line_at + 1:] if len(i) == 3])
        for i in atom_pos:
            cart_atom_pos = V2A(unit_lattice, *i)
            car_output.write("   {:16.15f}   {:16.15f}   {:16.15f}\n".format(*cart_atom_pos))
        car_output.close()
        print ("\n  Program Finished ...  \n")
        print (40 * "-")
        sys.exit()

    if iformat == 2:
        car_output = open("supercell_cartesian.dat", "w")
        for i in data:
            car_output.write(i)
        car_output.close()
        dir_output = open("supercell_direct.dat", "w")
        for i in range(line_at):
            dir_output.write(data[i])
        dir_output.write("Direct\n")
        atom_pos = numpy.array([[float(j) for j in i] for i in datasplit[line_at + 1:] if len(i) == 3])
        for i in atom_pos:
            dir_atom_pos = V2A(inverse_lattice, *i)
            dir_output.write("   {:16.15f}   {:16.15f}   {:16.15f}\n".format(*dir_atom_pos))
        dir_output.close()
        print ("\n  Program Finished ...  \n")
        print (40 * "-")
        sys.exit()

def icase2(pos,volume,latconstant,data):
    newvolume = -1 * pos[0]
    ratio = (newvolume / volume) ** (1 / 3)
    newlatconstant = ratio * latconstant
    output = open("supercell.dat", "w")
    for i, value in enumerate(data):
        if i == 0:
            output.write("Modified POSCAR. Volume = {}\n".format(newvolume))
        elif i == 1:
            output.write("  " + str(newlatconstant) + "\n")
        else:
            output.write(value)
    print ("\n  Program Finished ...  \n")
    print (40 * "-")
    sys.exit()

def icasegt2(T,line_at,datasplit,data):
    R = T2R(T)
    nsuper = getnsuper(T)
    outputtopoffile(line_at, datasplit, nsuper, data, T)
    lattice = getnewunitvectors(nsuper, R)
    outputbottomoffile(data, line_at, nsuper, lattice, R)
    sys.exit()

def getnsuper(T):
    nsuper = int(numpy.linalg.det(T))
    if nsuper < 1:
        print ("")
        print ("  " + str(T))
        print ("\n  Determinant = {}".format(nsuper))
        print ("\n  Wrong T matrix!  \n")
        print (40 * "-")
        sys.exit()
    return nsuper

def outputtopoffile(line_at,datasplit,nsuper,data,T):
    output = open("supercell.dat", "w")
    for i in range(line_at):
        if i < 2:
            output.write(data[i])
        elif 2 <= i < 5:
            unit_vector = numpy.array([float(j) for j in datasplit[i]])
            superlattice = unit_vector.dot(T)
            output.write("   {:.15f}  {:.15f}  {:.15f}\n".format(*superlattice))
        elif i < line_at - 1:
            output.write(data[i])
        else:
            row = [str(int(int(j) * nsuper)) for j in datasplit[i]]
            output.write("   " + " ".join(row) + "\n")
    output.write(data[line_at])
    output.close()
    return 1

def outputbottomoffile(data,line_at,nsuper,lattice,R):
    output = open("supercell.dat","a")
    unitvec = numpy.array([[float(j) for j in i.rsplit()] for i in data[line_at + 1:]])
    for i in unitvec:
        vec = i.dot(R) / nsuper
        for j in lattice:
            newunitvec = vec + j
            output.write("   {:16.15f}   {:16.15f}   {:16.15f}\n".format(*newunitvec))
    output.close()
    print ("\n  Program Finished ...  \n")
    print (40 * "-")

def getnewunitvectors(nsuper,R):
    nfind = 0
    lattice = []
    for i in range(-50, 50):
        for j in range(-50, 50):
            for k in range(-50, 50):
                vec = numpy.array([k, j, i]).dot(R)
                if vec[0] >= 0 and vec[0] < nsuper and vec[1] >= 0 and vec[1] < nsuper and vec[2] >= 0 and vec[2] < nsuper:
                    nfind += 1
                    vec = vec / nsuper
                    lattice.append(vec)
    lattice = numpy.array(lattice)
    return lattice

##################################

if __name__ == '__main__':
    main()
