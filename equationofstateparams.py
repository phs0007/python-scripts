####################################################################################################
#                                                                                                  #
#    Script Name:  equationofstateparams.py                                                        #
#                                                                                                  #
#    Author(s):  Paul H. Sanders and Jianjun Dong                                                  #
#                Auburn University Physics Department                                              #
#                                                                                                  #
#    What the heck does this do?                                                                   #
#       This script takes a list of energy/volume values and calculates the fitting parameters.    #
#                                                                                                  #
#    Input: 1. Must have eos.in_****** data from the working directory                             #
#    *The data needs to be in the form (V,E/P)*                                                    #
#                                                                                                  #
#    Output: 1. Parameters to equation of state file ***eos.out_**** for each equation of state.   #
#                                                                                                  #
#    Dates: 1. PHS August 22, 2016                                                                 #
#           2. PHS revision August 30, 2016                                                        #
#           3. PHS revision September 1, 2016                                                      #
#           4. JJD revision September 5, 2016                                                      #
#           5. PHS revision September 6, 2016                                                      #
#           6. PHS revision September 12, 2016                                                     #
#                                                                                                  #
####################################################################################################

import sys
import numpy
import scipy.optimize as optimization
import heapq
import textwrap
import os
import fnmatch

def main():

    # get information from user questions
    sourcemode = initial_configuration()
    path, process, typePorE, Vo, material = display1(sourcemode)

    # get information about the incoming data
    Eoi, Voi, vol, yval, lenvol = getdata(path, typePorE)

    # fit parameters
    param1, Koi = getparams("2nd", typePorE, Vo, vol, yval, Eoi, Voi, 1.5)
    param2, Koi, Kpoi = getparams("3rd", typePorE, Vo, vol, yval, Eoi, Voi, Koi, 4.0)
    param3 = getparams("vin", typePorE, Vo, vol, yval, Eoi, Voi, Koi, Kpoi)
    param4, alpha = getparams("alp", typePorE, Vo, vol, yval, Eoi, Voi, Koi, 7/3)
    param5 = getparams("abe", typePorE, Vo, vol, yval, Eoi, Voi, Koi, alpha, 0.5 * (alpha + 1))
    param6 = getparams("meo", typePorE, Vo, vol, yval, Eoi, Voi, Koi, Kpoi)
    param7 = getparams("kea", typePorE, Vo, vol, yval, Eoi, Voi, Koi, Kpoi, Kpoi)

    # output results
    output_screen_results(param1, param2, param3, param4, param5, param6, param7, typePorE)
    yfit = list(output_results(material, lenvol, vol, yval, Vo, param1, param2, param3, param4, param5, param6, param7, typePorE))
    #plotting(typePorE, vol, yval, yfit, material)

######################################################

def initial_configuration():
    par = sys.argv
    if len(par) >= 4:
        sourcemode = 1
    else:
        sourcemode = 0
    return sourcemode

def display1(sourcemode):
    if sourcemode == 1:
        path = sys.argv[1]
        material = path.rsplit("_")[-1]
        process = sys.argv[2]
        typePorE = sys.argv[3]
        try:
            Vo = float(sys.argv[4])
        except IndexError:
            Vo = 0
        print("")
    else:
        print (40 * '-')
        print ("   EQUATION OF STATE MODELS")
        print ("   Paul H. Sanders and Jianjun Dong")
        print ("   Auburn University")
        print (40 * '-')
        print ("   STEP 1: SELECT EOS DATA TYPE AND MATERIAL")
        print (40 * '-')
        print (40 * '-')
        print ("    1.1: Preliminary Questions")
        print (40 * '-')
        print ("")

        text = "Welcome to the EOS Fitting Model. " \
               "Now this model can serve two purposes. " \
               "The first purpose is fitting and plotting equations of state, " \
               "which is the standard use of this program. " \
               "The second purpose is to use already fitted parameters to derive and plot other related data."
        for i in textwrap.wrap(text, width=70, initial_indent = "     ", subsequent_indent = "   "):
            print (i)

        print ("\n   Different Purposes:   1. Fitting and Plotting Raw Equations of State Data")
        print ("\n                         2. Deriving and Plotting Already Fitted Data\n")
        print (40 * '-')

        process = str(input("1. For which purpose would you like to use this EOS Fitting Model? (Choose a number 1 or 2)\n   Desired Choice: ")) # This asks the user to select how they want to use the program
        while process != "1" and process != "2":
            # This tests whether the input is valid or not
            print ("\n     Please enter a valid choice, either '1' or '2'.....\n")
            process = str(input("1. For which purpose would you like to use this EOS Fitting Model? (Choose a number 1 or 2)\n   Desired Choice: ")) # This asks the user to select how they want to use the program
    if process == "1":
        typePorE, path, material, Vo = process1()
    else:
        process2()
    return path, process, typePorE, Vo, material

def process1():
    print ("")
    print (40 * '-')
    print ("")
    text = "When we do the fitting for the equations of state, this requires a set of data as an input to be fitted. " \
               "Now the data needs to be a file in the form of two columns, where the first column is a list of volume values. " \
               "The second column is a list of either pressure or energy values, which is your choice. " \
               "The question below seeks to ask you which set of data it should treat the second column, either as pressure or as energy data. " \
               "The volume is assumed to be in A^3, the pressure is assumed to be in GPa, and the energy is assumed to be in eV. " \
               "It is not necessary to provide a header for the data, start the first line of the file as the data."
    for i in textwrap.wrap(text, width=70, initial_indent="     ", subsequent_indent="   "):
        print (i)
    print ("\n     Eg.   V   (E/P)\n           -     -\n           -     -\n           -     -\n")
    print (40 * '-')
    typePorE = input("1. What is the Form of the Incoming EOS Data? (P or E)\n   V vs. ")  # User-Selected Data typePorE
    while typePorE != "P" and typePorE != "E":
        # This tests whether the input is valid or not
        print ("\n     Please enter a valid value, either 'P' or 'E'.....\n")
        typePorE = str(
        input("1. What is the Form of the Incoming EOS Data? (P or E)\n   V vs. "))  # User-Selected Data typePorE
    if typePorE == "P":
        # This helps for the text below if the user selects P
        name = "Pressure"
    if typePorE == "E":
        # This helps for the text below if the user selects E
        name = "Energy"
    print ("")
    print (40 * '-')
    print ("")
    text = "Now after looking at your choice of {} values to be fitted, " \
           "please give the file name path in which you want the program to look for the file. " \
           "It is assumed the file is contained in the working directory, " \
           "and the only thing you need to input is the name of the file. " \
           "Now the name of the file needs to look like eos.in{}_******, " \
           "where the stars represent the name of the material you want analyzed.".format(name, typePorE)
    for i in textwrap.wrap(text, width=70, initial_indent="     ", subsequent_indent="   "):
        print (i)
    print ("\n     Eg.   eos.in{}_Diamond\n".format(typePorE))
    print (40 * '-')
    material = str(
        input("2. Complete the file name for the EOS Data (of the form eos.in{0}_******):\n   eos.in{0}_".format(
            typePorE)))  # User-Selected Material
    print ("")
    path = "eos.in{}_{}".format(typePorE, material)  # File Path
    while not os.path.isfile(path):
        print("It looks like the file doesn't exist in the directory...\n"
              "Please enter a valid file name.")
        print ("")
        print (40 * '-')
        print ("")
        text = "Now after looking at your choice of {} values to be fitted, " \
               "please give the file name path in which you want the program to look for the file. " \
               "It is assumed the file is contained in the working directory, " \
               "and the only thing you need to input is the name of the file. " \
               "Now the name of the file needs to look like eos.in{}_******, " \
               "where the stars represent the name of the material you want analyzed.".format(name, typePorE)
        for i in textwrap.wrap(text, width=70, initial_indent="     ", subsequent_indent="   "):
            print (i)
        print ("\n     Eg.   eos.in{}_Diamond\n".format(typePorE))
        print (40 * '-')
        material = str(
            input(
                "2. Complete the file name for the EOS Data (of the form eos.in{0}_******):\n   eos.in{0}_".format(
                    typePorE)))  # User-Selected Material
        print ("")
        path = "eos.in{}_{}".format(typePorE, material)  # File Path
    print (40 * '-')
    print ("    1.2: Method for Determining Parameters")
    print (40 * '-')
    print (40 * '-')
    text = "Now it is important to determine if there are any input parameters you want to fix. " \
           "Essentially the fitting parameters are Eo,Vo,Ko, and Kpo, where Eo is the zero pressure " \
           "value of the energy (in eV), Vo is the zero pressure value of the volume (in A^3), " \
           "Ko is the zero pressure value of the bulk modulus (in GPa), and Kpo is the zero pressure " \
           "value of the derivative of the bulk modulus. Below are two methods to choose from: "
    print("")
    for i in textwrap.wrap(text, width=70, initial_indent="     ", subsequent_indent="   "):
        print (i)
    print ("\n     Enter any negative value or zero for no fixing.\n"
           "     Enter any positive value to fix Vo and use Eo, Ko, and Kpo as fitting parameters\n")
    print (40 * '-')
    Vo = float(input("3. Please enter a value (Input value)\n   Value: "))  # User-Selected Material
    print ("")
    print (40 * '-')
    print ("   STEP 2: EOS FITTING")
    print (40 * '-')
    print ("")
    return typePorE, path, material, Vo

def process2():
    eVA3toGPa = 160.2176487
    workingdir = os.getcwd()
    print ("")
    print (40 * '-')
    print ("")
    text = "When we derive and plot the already fitted data, it helps to know where to look, whether you would like to focus on Pressure or Energy data."
    for i in textwrap.wrap(text, width=70, initial_indent="     ", subsequent_indent="   "):
        print (i)
    print ("\n     Eg.  E2ndeos.out_*** or P2ndeos.out_***\n")
    print (40 * '-')
    typePorE = input("2. Which type of data do you want to look for? (P or E)\n   Desired Choice: ")  # User-Selected Data typePorE
    while typePorE != "P" and typePorE != "E":
        # This tests whether the input is valid or not
        print ("\n     Please enter a valid value, either 'P' or 'E'.....\n")
        typePorE = str(
        input("1. What is the Form of the Incoming EOS Data? (P or E)\n   V vs. "))  # User-Selected Data typePorE
    if typePorE == "E":
        choice = "Energy"
    else:
        choice = "Pressure"
    files = [i for i in os.listdir(workingdir) if fnmatch.fnmatch(i,"{}*.out_*".format(typePorE))]
    materials = [i.rsplit("_")[-1] for i in files]
    choiceofmaterial = [materials[0]]
    for i in materials:
       k = 0
       for j in choiceofmaterial:
          if i == j:
              k+=1
       if k == 0:
           choiceofmaterial.append(i)
    print ("")
    print (40 * '-')
    print ("")
    text = "It looks like we found minerals to use. Please select which mineral you would like to use: (A number will suffice)"
    for i in textwrap.wrap(text, width=70, initial_indent="     ", subsequent_indent="   "):
        print (i)
    for i, value in enumerate(choiceofmaterial):
        print("\n  {}.  {}".format(i+1, value))
    print ("")
    print (40 * '-')
    mineral = int(input("3. Which choice will you select? (Enter a number):\n Desired Choice: "))
    material = choiceofmaterial[mineral-1]
    print ("")
    print (40 * '-')
    print ("")
    text ="Now would you like to use Pressure or Volume values for the x axis?"
    for i in textwrap.wrap(text, width=70, initial_indent="     ", subsequent_indent="   "):
        print (i)
    print("\n  1.  Pressure")
    print("\n  2.  Volume")
    print ("")
    print (40 * '-')
    presorvol = int(input("4. Which choice will you select? (Enter a number):\n Desired Choice: "))
    if presorvol == 1:
        choice = "Pressure"
    else:
        choice = "Volume"
    print ("")
    print (40 * '-')
    print ("")
    text ="Now to effectively plot the {} values, it is helpful to determine a {} range.".format(choice,choice)
    for i in textwrap.wrap(text, width=70, initial_indent="     ", subsequent_indent="   "):
        print (i)
    print ("")
    print (40 * '-')
    print ("")
    min = float(input("5.a. Please enter a minimum {} value. (Input value)\n   Value: ".format(choice)))
    max = float(input("5.b. Please enter a maximum {} value. (Input value)\n   Value: ".format(choice)))
    step = float(input("5.c. Please enter a valid step size. (Input value)\n   Value: "))
    xrange = numpy.linspace(min,max,num = (max - min)/step + 1)
    print ("")
    print (40 * '-')
    print ("")
    print ("     Your {} values look like:\n \n         {} {} {} … {}".format(choice, xrange[0], round(xrange[1],2), round(xrange[2],2), xrange[-1]))
    files = [i for i in os.listdir(workingdir) if fnmatch.fnmatch(i,"{}*.out_{}".format(typePorE,material))]
    if len(files) == 0:
        sys.exit("We found no files to use!")
    for i in files: 
        if presorvol == 1:
            eoschoice = i[1:4]
            data = open(i,"r")
            data = data.readline()
            data = data.rsplit(":")[0]
            params = [float(i) for i in data.rsplit()]
            params2 = list(params)
            params[2] = params[2]/eVA3toGPa #Convert Vo from GPa to eVA3
            params2[2] = params2[2]/eVA3toGPa #Convert Vo from GPa to eVA3
            presparams = list(params)
            if eoschoice == "2nd":
                del params[-1]
                del params2[-1]
            if eoschoice == "alp":
                del params[-2]
                del params2[-2]
            if eoschoice == "abe":
                del params[-3]
                del params2[-2]
            del params[0]
            xrange = numpy.linspace(0,100,101)
            Pval = xrange/eVA3toGPa

            out = open("VPEH"+eoschoice+".out_{}".format(material),"w")
            for i, value in enumerate(Pval):
                voli = presparams[1]*(1+presparams[3]/presparams[2]*value)**(-1/presparams[3])
                def f(V):
                    return geteos(eoschoice,0)[1](V,*params) - value
                vol = optimization.newton(f, voli, tol=1.0*10**-9)
                Eval = geteos(eoschoice,0)[0](vol, *params2)
                out.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol,value*eVA3toGPa,Eval,Eval+value*vol))

        else:
            vol = xrange
            eoschoice = i[1:4]
            data = open(i,"r")
            data = data.readline()
            data = data.rsplit(":")[0]
            params = [float(i) for i in data.rsplit()]
            if eoschoice == "2nd":
                del params[-1]
            if eoschoice == "alp":
                del params[-2]
            if eoschoice == "abe":
                del params[-3]
            if typePorE == "E":
                params[2] = params[2]/eVA3toGPa #Convert Vo from GPa to eVA3
                presparams = list(params)
                del presparams[0]
                Pval = geteos(eoschoice,0)[1](vol, *presparams)
                Eval = geteos(eoschoice,0)[0](vol, *params)
                out = open("VPEH"+eoschoice+".out_{}".format(material),"w")
                for i, value in enumerate(vol):
                    out.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i],Pval[i]*eVA3toGPa,Eval[i],Eval[i]+Pval[i]*vol[i]))
                out.close()
            else:
                Pval = geteos(eoschoice,0)[1](vol, *params)  #No need to convert, incoming parameters already in GPa
                out = open("VP"+eoschoice+".out_{}".format(material),"w")
                for i, value in enumerate(vol):
                    out.write("{0:>6}  {1:<20}\n".format(vol[i],Pval[i]))
                out.close()
    print ("\n   Fitting Finished...... \n")
    print (40 * '-')
    sys.exit()
    return True

def getdata(path, typePorE):
    values = numpy.genfromtxt(path)
    vol = values[:, 0]
    lenvol = len(vol)
    yval = values[:, 1]
    Eoi = min(yval)
    Voi = heapq.nsmallest(1, values, key=lambda values: values[1])[0][0]
    return Eoi, Voi, vol, yval, lenvol

def geteos(eoschoice, Vo):
    if Vo <= 0:
        if eoschoice == "2nd":
            def E(V, Eo, Vo, Ko):
                return Eo + ((9 * Vo * Ko) / 8) * ((Vo / V) ** (2 / 3) - 1) ** 2
            def P(V, Vo, Ko):
                return 1.5 * Ko * ((Vo / V) ** (7 / 3) - (Vo / V) ** (5 / 3))
        if eoschoice == "3rd":
            def E(V, Eo, Vo, Ko, Kpo):
                return Eo + ((9 * Vo * Ko) / 16) * (
                    (Vo ** (2 / 3) * V ** (-2 / 3) - 1) ** 3 * Kpo + ((Vo ** (2 / 3) * V ** (-1 * 2 / 3) - 1) ** 2) * (
                        6 - 4 * Vo ** (2 / 3) * V ** (-2 / 3)))
            def P(V, Vo, Ko, Kpo):
                return 3 / 2 * Ko * ((Vo / V) ** (7 / 3) - (Vo / V) ** (5 / 3)) * (
                    1 + 3 / 4 * (Kpo - 4) * ((Vo / V) ** (2 / 3) - 1))
        if eoschoice == "vin":
            def E(V, Eo, Vo, Ko, Kpo):
                return Eo + 4 * Ko * Vo / (Kpo - 1) ** 2 - 2 * Vo * Ko / (Kpo - 1) ** 2 * (
                    5 + 3 * Kpo * ((V / Vo) ** (1 / 3) - 1) - 3 * (V / Vo) ** (1 / 3)) * numpy.exp(
                    -3 / 2 * (Kpo - 1) * ((V / Vo) ** (1 / 3) - 1))
            def P(V, Vo, Ko, Kpo):
                return 3 * Ko * (1 - (V / Vo) ** (1 / 3)) / ((V / Vo) ** (2 / 3)) * numpy.exp(
                    1.5 * (Kpo - 1) * (1 - (V / Vo) ** (1 / 3)))
        if eoschoice == "alp":
            def E(V, Eo, Vo, Ko, alpha):
                return Eo + 2 * Ko * Vo / (alpha - 1) ** 2 * ((Vo / V) ** ((alpha - 1) / 2) - 1) ** 2
            def P(V, Vo, Ko, alpha):
                return 2 * Ko / (alpha - 1) * ((Vo / V) ** alpha - (Vo / V) ** ((alpha + 1) / 2))
        if eoschoice == "abe":
            def E(V, Eo, Vo, Ko, alpha, beta):
                return Eo + Ko * Vo / (alpha - beta) * (
                    1 / (alpha - 1) * ((Vo / V) ** (alpha - 1) - 1) - 1 / (beta - 1) * ((Vo / V) ** (beta - 1) - 1))
            def P(V, Vo, Ko, alpha, beta):
                return Ko / (alpha - beta) * ((Vo / V) ** alpha - (Vo / V) ** beta)
        if eoschoice == "meo":
            def E(V, Eo, Vo, Ko, Kpo):
                return Eo + Ko * Vo * (
                    (1 / (Kpo * (Kpo - 1)) * (V / Vo) ** (1 - Kpo) + 1 / Kpo * V / Vo - 1 / (Kpo - 1)))
            def P(V, Vo, Ko, Kpo):
                return Ko / Kpo * ((Vo / V) ** Kpo - 1)
        if eoschoice == "kea":
            def E(V, Eo, Vo, Ko, Kpo, Kpi):
                return Eo + Ko * Kpo * Vo / Kpi ** 2 / (Kpi - 1) * (
                    (Kpi - 1) * (V / Vo - 1) + (Vo / V) ** (Kpi - 1) - 1) + Ko * Vo * (Kpo - Kpi) / Kpi * (
                    V / Vo * numpy.log(Vo / V) + V / Vo - 1)
            def P(V, Vo, Ko, Kpo, Kpi):
                return Ko * Kpo / Kpi ** 2 * ((Vo / V) ** Kpi - 1) - Ko * (Kpo - Kpi) / Kpi * numpy.log(Vo / V)
        return E, P
    else:
        if eoschoice == "2nd":
            def E(V, Eo, Ko):
                return Eo + ((9 * Vo * Ko) / 8) * ((Vo / V) ** (2 / 3) - 1) ** 2
            def P(V, Ko):
                return 1.5 * Ko * ((Vo / V) ** (7 / 3) - (Vo / V) ** (5 / 3))
        if eoschoice == "3rd":
            def E(V, Eo, Ko, Kpo):
                return Eo + ((9 * Vo * Ko) / 16) * (
                    (Vo ** (2 / 3) * V ** (-1 * 2 / 3) - 1) ** 3 * Kpo + ((Vo ** (2 / 3) * V ** (-1 * 2 / 3) - 1) ** 2) * (
                        6 - 4 * Vo ** (2 / 3) * V ** (-1 * 2 / 3)))
            def P(V, Ko, Kpo):
                return 3 / 2 * Ko * ((Vo / V) ** (7 / 3) - (Vo / V) ** (5 / 3)) * (
                    1 + 3 / 4 * (Kpo - 4) * ((Vo / V) ** (2 / 3) - 1))
        if eoschoice == "vin":
            def E(V, Eo, Ko, Kpo):
                return Eo + 4 * Ko * Vo / (Kpo - 1) ** 2 - 2 * Vo * Ko / (Kpo - 1) ** 2 * (
                    5 + 3 * Kpo * ((V / Vo) ** (1 / 3) - 1) - 3 * (V / Vo) ** (1 / 3)) * numpy.exp(
                    -3 / 2 * (Kpo - 1) * ((V / Vo) ** (1 / 3) - 1))
            def P(V, Ko, Kpo):
                return 3 * Ko * (1 - (V / Vo) ** (1 / 3)) / ((V / Vo) ** (2 / 3)) * numpy.exp(
                    1.5 * (Kpo - 1) * (1 - (V / Vo) ** (1 / 3)))
        if eoschoice == "alp":
            def E(V, Eo, Ko, alpha):
                return Eo + 2 * Ko * Vo / (alpha - 1) ** 2 * ((Vo / V) ** ((alpha - 1) / 2) - 1) ** 2
            def P(V, Ko, alpha):
                return 2 * Ko / (alpha - 1) * ((Vo / V) ** alpha - (Vo / V) ** ((alpha + 1) / 2))
        if eoschoice == "abe":
            def E(V, Eo, Ko, alpha, beta):
                return Eo + Ko * Vo / (alpha - beta) * (
                    1 / (alpha - 1) * ((Vo / V) ** (alpha - 1) - 1) - 1 / (beta - 1) * ((Vo / V) ** (beta - 1) - 1))
            def P(V, Ko, alpha, beta):
                return Ko / (alpha - beta) * ((Vo / V) ** alpha - (Vo / V) ** beta)
        if eoschoice == "meo":
            def E(V, Eo, Ko, Kpo):
                return Eo + Ko * Vo * (
                    (1 / (Kpo * (Kpo - 1)) * (V / Vo) ** (1 - Kpo) + 1 / Kpo * V / Vo - 1 / (Kpo - 1)))
            def P(V, Ko, Kpo):
                return Ko / Kpo * ((Vo / V) ** Kpo - 1)
        if eoschoice == "kea":
            def E(V, Eo, Ko, Kpo, Kpi):
                return Eo + Ko * Kpo * Vo / Kpi ** 2 / (Kpi - 1) * (
                    (Kpi - 1) * (V / Vo - 1) + (Vo / V) ** (Kpi - 1) - 1) + Ko * Vo * (Kpo - Kpi) / Kpi * (
                    V / Vo * numpy.log(Vo / V) + V / Vo - 1)
            def P(V, Ko, Kpo, Kpi):
                return Ko * Kpo / Kpi ** 2 * ((Vo / V) ** Kpi - 1) - Ko * (Kpo - Kpi) / Kpi * numpy.log(Vo / V)
        return E, P

def getparams(eoschoice, typePorE, Vo, vol, yval, *ip):
    if Vo > 0:
        ip = list(ip)
        del ip[1]
    if typePorE == "E":
        val = 0
    else:
        val = 1
        ip = list(ip)
        del ip[0]
    try:
        par, var = optimization.curve_fit(geteos(eoschoice, Vo)[val], vol, yval, p0=ip, maxfev=20000)
    except RuntimeError:
        print("Warning: The call to the function for {} failed to converge.".format(eoschoice))
        par = [0] * len(ip)
    except RuntimeWarning:
        print("Warning: The call to the function for {} experienced an invalid power.".format(eoschoice))
    if eoschoice == "2nd":
        return par, par[-1]
    elif eoschoice == "3rd":
        return par, par[-2], par[-1]
    elif eoschoice == "alp":
        return par, par[-1]
    elif eoschoice == "abe":
        return par
    else:
        return par

def output_screen_results(param1, param2, param3, param4, param5, param6, param7, typePorE):
    eVA3toGPa = 160.2176487
    if typePorE == "P":
        eVA3toGPa = 1 # no need to convert, already in GPa
        print("2bmeos {:15.10f} {:15.10f}    4.0".format(param1[0], param1[1] * eVA3toGPa))
        print("3bmeos {:15.10f} {:15.10f} {:15.10f}".format(param2[0], param2[1] * eVA3toGPa, param2[2]))
        print("vinet  {:15.10f} {:15.10f} {:15.10f}".format(param3[0], param3[1] * eVA3toGPa, param3[2]))
        print("alpha  {:15.10f} {:15.10f} {:15.10f}".format(param4[0], param4[1] * eVA3toGPa, (3 * param4[2] + 1) / 2))
        print("abeos  {:15.10f} {:15.10f} {:15.10f}".format(param5[0], param5[1] * eVA3toGPa, param5[2] + param5[3]))
        print("m_eos  {:15.10f} {:15.10f} {:15.10f}".format(param6[0], param6[1] * eVA3toGPa, param6[2]))
        print("keane  {:15.10f} {:15.10f} {:15.10f}".format(param7[0], param7[1] * eVA3toGPa, param7[2]))
    else:
        print("2bmeos {:15.10f} {:15.10f} {:15.10f}    4.0".format(param1[0], param1[1], param1[2] * eVA3toGPa))
        print("3bmeos {:15.10f} {:15.10f} {:15.10f} {:15.10f}".format(param2[0], param2[1], param2[2] * eVA3toGPa, param2[3]))
        print("vinet  {:15.10f} {:15.10f} {:15.10f} {:15.10f}".format(param3[0], param3[1], param3[2] * eVA3toGPa, param3[3]))
        print("alpha  {:15.10f} {:15.10f} {:15.10f} {:15.10f}".format(param4[0], param4[1], param4[2] * eVA3toGPa, (3 * param4[3] + 1) / 2))
        print("abeos  {:15.10f} {:15.10f} {:15.10f} {:15.10f}".format(param5[0], param5[1], param5[2] * eVA3toGPa, param5[3] + param5[4]))
        print("m_eos  {:15.10f} {:15.10f} {:15.10f} {:15.10f}".format(param6[0], param6[1], param6[2] * eVA3toGPa, param6[3]))
        print("keane  {:15.10f} {:15.10f} {:15.10f} {:15.10f}".format(param7[0], param7[1], param7[2] * eVA3toGPa, param7[3]))
    print ("\n   Fitting Finished...... \n")
    print (40 * '-')

def output_results(material, lenvol, vol, yval, Vo, param1, param2, param3, param4, param5, param6, param7, typePorE):
    eVA3toGPa = 160.2176487
    if typePorE == "E":
        # E2ndeos.out_
        output = open("E2ndeos.out_{}".format(material), "w")
        output.write("{:15.10f} {:15.10f} {:15.10f}    4.0\n".format(param1[0], param1[1], param1[2] * eVA3toGPa))
        output.write("\n Eo + ((9 * Vo * Ko) / 8) * ((Vo / V) ** (2 / 3) - 1) ** 2 \n")
        output.write("\n " + str(lenvol) + "\n")
        Efit = [0] * lenvol
        for i in range(lenvol):
            Efit[i] = geteos("2nd", Vo)[0](vol[i],*param1)
            diff = (Efit[i] - yval[i])/yval[i]*100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Efit[i], diff))
        output.close()
        yield Efit[:]
        # E3rdeos.out_
        output = open("E3rdeos.out_{}".format(material), "w")
        output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(param2[0], param2[1], param2[2] * eVA3toGPa, param2[3]))
        output.write("\n Eo + ((9 * Vo * Ko) / 16) * ((Vo ** (2 / 3) * V ** "
                     "(-1 * 2 / 3) - 1) ** 3 * Kpo + ((Vo ** (2 / 3) * V ** "
                     "(-1 * 2 / 3) - 1) ** 2) * (6 - 4 * Vo ** (2 / 3) * V ** "
                     "(-1 * 2 / 3))) \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Efit[i] = geteos("3rd", Vo)[0](vol[i],*param2)
            diff = (Efit[i] - yval[i])/yval[i]*100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Efit[i], diff))
        output.close()
        yield Efit[:]
        # Evineos.out_
        output = open("Evineos.out_{}".format(material), "w")
        output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(param3[0], param3[1], param3[2] * eVA3toGPa, param3[3]))
        output.write("\n Eo + 4 * Ko * Vo / (Kpo - 1) ** 2 - 2 * Vo * "
                     "Ko / (Kpo - 1) ** 2 * (5 + 3 * Kpo * ((V / Vo) ** "
                     "(1 / 3) - 1) - 3 * (V / Vo) ** (1 / 3)) * "
                     "numpy.exp(-3 / 2 * (Kpo - 1) * ((V / Vo) ** "
                     "(1 / 3) - 1)) \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Efit[i] = geteos("vin", Vo)[0](vol[i],*param3)
            diff = (Efit[i] - yval[i])/yval[i]*100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Efit[i], diff))
        output.close()
        yield Efit[:]
        # Ealpeos.out_
        output = open("Ealpeos.out_{}".format(material), "w")
        output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f} {:15.10f} : alpha\n".format(param4[0], param4[1], param4[2] * eVA3toGPa, (3 * param4[3] + 1) / 2, param4[3]))
        output.write("\n Eo + 2 * Ko * Vo / (alpha - 1) ** 2 * "
                     "((Vo / V) ** ((alpha - 1) / 2) - 1) ** 2 \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Efit[i] = geteos("alp", Vo)[0](vol[i], *param4)
            diff = (Efit[i] - yval[i]) / yval[i] * 100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Efit[i], diff))
        output.close()
        yield Efit[:]
        # Eabeeos.out_
        output = open("Eabeeos.out_{}".format(material), "w")
        output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f} {:15.10f} {:15.10f} : alpha, beta\n".format(param5[0], param5[1], param5[2] * eVA3toGPa, param5[3] + param5[4], param5[3], param5[4]))
        output.write("\n Eo + Ko * Vo / (alpha - beta) * (1 / (alpha - 1) "
                     "* ((Vo / V) ** (alpha - 1) - 1) - 1 / (beta - 1) * "
                     "((Vo / V) ** (beta - 1) - 1)) \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Efit[i] = geteos("abe", Vo)[0](vol[i], *param5)
            diff = (Efit[i] - yval[i]) / yval[i] * 100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Efit[i], diff))
        output.close()
        yield Efit[:]
        # Emeoeos.out_
        output = open("Emeoeos.out_{}".format(material), "w")
        output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(param6[0], param6[1], param6[2] * eVA3toGPa, param6[3]))
        output.write("\n Eo + Ko * Vo * ((1 / (Kpo * (Kpo - 1)) * (V / Vo)"
                     " ** (1 - Kpo) + 1 / Kpo * V / Vo - 1 / (Kpo - 1))) \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Efit[i] = geteos("meo", Vo)[0](vol[i], *param6)
            diff = (Efit[i] - yval[i]) / yval[i] * 100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Efit[i], diff))
        output.close()
        yield Efit[:]
        # Ekeaeos.out_
        output = open("Ekeaeos.out_{}".format(material), "w")
        output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f} {:15.10f} : Kpi\n".format(param7[0], param7[1], param7[2] * eVA3toGPa, param7[3], param7[4]))
        output.write("\n Eo + Ko * Kpo * Vo / Kpi ** 2 / (Kpi - 1) * "
                     "((Kpi - 1) * (V / Vo - 1) + (Vo / V) ** (Kpi - 1) - 1) + "
                     "Ko * Vo * (Kpo - Kpi) / Kpi * (V / Vo * "
                     "numpy.log(Vo / V) + V / Vo - 1) \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Efit[i] = geteos("kea", Vo)[0](vol[i], *param7)
            diff = (Efit[i] - yval[i]) / yval[i] * 100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Efit[i], diff))
        output.close()
        yield Efit[:]
    else:
        # P2ndeos.out_
        output = open("P2ndeos.out_{}".format(material), "w")
        output.write("{:15.10f} {:15.10f}    4.0\n".format(param1[0], param1[1]))
        output.write("\n 1.5 * Ko * ((Vo / V) ** (7 / 3) - (Vo / V) ** (5 / 3)) \n")
        output.write("\n " + str(lenvol) + "\n")
        Pfit = [0] * lenvol
        for i in range(lenvol):
            Pfit[i] = geteos("2nd", Vo)[1](vol[i], *param1)
            diff = (Pfit[i] - yval[i]) / yval[i] * 100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Pfit[i], diff))
        output.close()
        yield Pfit[:]
        # E3rdeos.out_
        output = open("P3rdeos.out_{}".format(material), "w")
        output.write(
            "{:15.10f} {:15.10f} {:15.10f}\n".format(param2[0], param2[1], param2[2]))
        output.write("\n 1.5 * Ko * ((Vo / V) ** (7 / 3) - (Vo / V) ** (5 / 3)) * ("\
                    "1 + 0.75 * (Kpo - 4) * ((Vo / V) ** (2 / 3) - 1)) \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Pfit[i] = geteos("3rd", Vo)[1](vol[i], *param2)
            diff = (Pfit[i] - yval[i]) / yval[i] * 100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Pfit[i], diff))
        output.close()
        yield Pfit[:]
        # Evineos.out_
        output = open("Pvineos.out_{}".format(material), "w")
        output.write(
            "{:15.10f} {:15.10f} {:15.10f}\n".format(param3[0], param3[1], param3[2]))
        output.write("\n 3 * Ko * (1 - (V / Vo) ** (1 / 3)) / ((V / Vo) ** (2 / 3)) * numpy.exp("\
                    "1.5 * (Kpo - 1) * (1 - (V / Vo) ** (1 / 3))) \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Pfit[i] = geteos("vin", Vo)[1](vol[i], *param3)
            diff = (Pfit[i] - yval[i]) / yval[i] * 100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Pfit[i], diff))
        output.close()
        yield Pfit[:]
        # Ealpeos.out_
        output = open("Palpeos.out_{}".format(material), "w")
        output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f} : alpha\n".format(param4[0], param4[1],
                                                                        (3 * param4[2] + 1) / 2, param4[2]))
        output.write("\n 2 * Ko / (alpha - 1) * ((Vo / V) ** alpha - (Vo / V) ** ((alpha + 1) / 2)) \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Pfit[i] = geteos("alp", Vo)[1](vol[i], *param4)
            diff = (Pfit[i] - yval[i]) / yval[i] * 100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Pfit[i], diff))
        output.close()
        yield Pfit[:]
        # Eabeeos.out_
        output = open("Pabeeos.out_{}".format(material), "w")
        output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f} {:15.10f} : alpha, beta\n".format(param5[0], param5[1], param5[2] + param5[3], param5[2], param5[3]))
        output.write("\n Ko / (alpha - beta) * ((Vo / V) ** alpha - (Vo / V) ** beta) \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Pfit[i] = geteos("abe", Vo)[1](vol[i], *param5)
            diff = (Pfit[i] - yval[i]) / yval[i] * 100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Pfit[i], diff))
        output.close()
        yield Pfit[:]
        # Emeoeos.out_
        output = open("Pmeoeos.out_{}".format(material), "w")
        output.write(
            "{:15.10f} {:15.10f} {:15.10f}\n".format(param6[0], param6[1], param6[2]))
        output.write("\n Ko / Kpo * ((Vo / V) ** Kpo - 1) \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Pfit[i] = geteos("meo", Vo)[1](vol[i], *param6)
            diff = (Pfit[i] - yval[i]) / yval[i] * 100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Pfit[i], diff))
        output.close()
        yield Pfit[:]
        # Ekeaeos.out_
        output = open("Pkeaeos.out_{}".format(material), "w")
        output.write(
            "{:15.10f} {:15.10f} {:15.10f} {:15.10f} : Kpi\n".format(param7[0], param7[1], param7[2], param7[3]))
        output.write("\n Ko * Kpo / Kpi ** 2 * ((Vo / V) ** Kpi - 1) - Ko * "
                     "(Kpo - Kpi) / Kpi * numpy.log(Vo / V) \n")
        output.write("\n " + str(lenvol) + "\n")
        for i in range(lenvol):
            Pfit[i] = geteos("kea", Vo)[1](vol[i], *param7)
            diff = (Pfit[i] - yval[i]) / yval[i] * 100
            output.write("{:15.10f} {:15.10f} {:15.10f} {:15.10f}\n".format(vol[i], yval[i], Pfit[i], diff))
        output.close()
        yield Pfit[:]

def plotting(typePorE, vol, yval, yfit, material):
    from matplotlib import pyplot
    ylab = "Pressure (GPa)"
    eoschoices = ["BM2nd","BM3rd","Vinet","ALEOS","ABEOS","M-EOS","KEANE"]
    fig1 = pyplot.figure(1)
    pyplot.subplots_adjust(wspace=None, hspace=None)
    for i, value in enumerate(eoschoices):
        number = int("24" + str(i+1))
        ax1 = fig1.add_subplot(number)
        ax1.set_title("{} vs. V Fitting for {} using {}".format(typePorE, material, value))
        ax1.set_xlabel("Volume (A^3)")
        if typePorE == "E":
            ax1.set_ylabel("Energy (eV/atom)")
        else:
            ax1.set_ylabel("Pressure (GPa)")
        ax1.plot(vol, yfit[i])
        ax1.plot(vol, yval,"ro")
    pyplot.show()
    return True


###############################################

if __name__ == '__main__':
    main()