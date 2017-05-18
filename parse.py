import numpy as np

data = np.loadtxt('students.csv',
                  delimiter=',',
                  dtype=np.dtype((str, 256)))

header = data[0]
data = data[1:]

test = data[:,-1]
data = data[:,:-1]

names = data[:,0:2]
data = data[:,2:]

print header
print " "
print data
print " "
print names
print " "
print test
