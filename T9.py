import numpy as np
import math

T = np.array([[-2,2,2],[2,-2,2],[2,2,-2]])

def getpoints(T):
    nsuper = int(np.linalg.det(T))
    len2, len3, len4 = [math.sqrt(abs(T[i].dot(T[i]))) for i in range(3)]
    radius = int(max(len2,len3,len4))
    lattice = np.zeros((nsuper,3))
    a = range(-radius,radius+1)
    i = 0
    for i, j, k in zip(a,a,a):
        thearray = np.array([k,j,i])
        len1 = abs(k*k + j*j + i*i)
        if thearray.dot(thearray) > 0:
            if 0<=thearray.dot(T[0])/(len1*len2)<1 and 0<=np.array([k,j,i]).dot(T[1])/(len1*len3)<1 and 0<=np.array([k,j,i]).dot(T[2])/(len1*len4)<1:
                lattice[i]=np.array([k,j,i])
                i+=1
    return lattice

print(getpoints(T))


