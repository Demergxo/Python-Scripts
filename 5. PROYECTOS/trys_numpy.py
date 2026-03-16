import numpy as np
import matplotlib.pyplot as plt
from math import pow

def numpy_sum(n):
    a = np.arange(n) ** 2
    b = np.arange(n) ** 3
    c = np.arange(n) ** 4
    c = a + b
    print(a)
    print(b)
    print(c)
    
numpy_sum(5)

def poten(base, exp):
    result = pow(base, exp)
    return result

x = poten(3,2)
print(int(x))