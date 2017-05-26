#!/usr/bin/env python

import numpy as np
import sys

from ast import literal_eval
from optparse import OptionParser

import os.path



################################################################################
## parse command line options

usage = "usage: %prog -f student-preferences.csv"
parser = OptionParser(usage)

parser.add_option("-f", "--file",
                  dest="filename",
                  action="store", type="string",
                  help="read data from FILENAME")

parser.add_option("-m", "--model",
                  dest="modelname",
                  default="models/andrea.yaml",
                  action="store", type="string",
                  help="read happiness model from FILENAME")

parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose")

parser.add_option("-q", "--quiet",
                  action="store_true", dest="verbose")

(options, args) = parser.parse_args(sys.argv)

if options.filename == None:
    parser.error("incorrect number of arguments")

if options.verbose:
    print "reading student preferences from {0}...".format(options.filename)
    print "using happiness model {0}...".format(options.modelname)
    print " "

##
################################################################################



################################################################################
## utility functions

def not_contains(a, elem):
    return np.intersect1d(a, elem).shape[0] == 0

# YAML happens to have a format which is compatible with python
# dictionaries.  we can simply evaluate it as python code.
#
def yaml_to_dict(filename):
    inf = open(filename,'r')
    model = literal_eval(inf.read())
    inf.close()

    return model

##
################################################################################



################################################################################
## import student preference data
## TODO: this is fragile, and assumes correct input

try:
    data = np.loadtxt(options.filename,
                      delimiter=',',
                      dtype=np.dtype((str, 256)))
except:
    print "ERROR: reading '{0}'".format(options.filename)
    if not os.path.isfile(options.filename):
        print "       file '{0}' not found".format(options.filename)
    else:
        print "       file '{0}' is not a valid CSV file".format(options.filename)
    sys.exit(1)

header        = data[0]
nassignments  = data[1]
data          = data[2:]

course_names  = header[2:]
nassignments  = nassignments[2:]
student_names = data[:,0:2]
data          = data[:,2:]


if options.verbose:
    print "course names:"
    print course_names
    print "number of TA slots per course:"
    print nassignments
    print " "


# duplicate course columns by the number of TA slots for that course
try:
    nassignments = nassignments.astype(np.int)
except:
    print "ERROR: invalid number of TA slots encountered in second row of {0}".format(options.filename)
    print nassignments
    print "should all be integers"
    sys.exit(1)

if np.sum(nassignments) != data.shape[0]:
    print "ERROR: number of students ({0}) not equal to number of assignments ({1})".format(np.sum(nassignments), data.shape[0])
    sys.exit(1)

# TODO: this is a bit hackish... can i write it more clearly?
cols = np.transpose(data)
data = [ ([cols[i].tolist()] * nassignments[i]) for i in range(cols.shape[0]) ]
data = np.transpose(np.vstack(data))


## convert Andrea's codes to numeric values
pref_mapping = yaml_to_dict(options.modelname)

def score_to_score(letter):
    try:
        return pref_mapping[letter]
    except:
        print "invalid score '{0}' found in preference file {1}".format(letter, options.filename)
        print "values allowed by happiness model {0}:".format(options.modelname)
        print [ key for key,value in pref_mapping.items() ]
        sys.exit(1)

def score_to_score_inv(score):
    # score should be valid if it gets to this point
    key = next(key for key, value in pref_mapping.items() if value == score)
    return key

vfunc = np.vectorize(score_to_score)
student_preferences = vfunc(data)
courses = np.arange(data.shape[0])


# duplicate entries in the course_names array based on the number of
# TA slots
# TODO: can i write this more clearly?
course_names2 = [ ([course_names[i]] * nassignments[i]) for i in range(cols.shape[0]) ]
course_names2 = reduce(lambda x,y: x+y, course_names2)
course_names = np.asarray(course_names2)

## end import student preference data
################################################################################



################################################################################
## genetic optimization algorithm

def happiness(student, course):
    return student[course]

def total_happiness(students, assignments):
    scores = [ happiness(s, a) for s, a in zip(students, assignments) ]
    student_happiness = np.sum(np.asarray(scores))

    return student_happiness / students.shape[0]



# genetic crossover
# - need to be careful that, if given two valid parents, this produces
#   two valid children.  use the cyclic crossover for this.
def cyclic_crossover(p1, p2):
    # initialize children to -1
    # TODO: better way to do this?
    c1 = np.arange(np.shape(p1)[0]) * 0 - 1
    c2 = np.arange(np.shape(p1)[0]) * 0 - 1

    # loop until we reach a closed cycle, filling c1 from p1
    i = 0
    while(not_contains(c1, p1[i])):
        c1[i] = p1[i]
        i = np.where(p1==p2[i])[0][0]

    # swap the rest of elements
    idx = np.where(c1 == -1)
    c1[idx] = p2[idx]
    c2[idx] = p1[idx]

    # and backfill from p2
    idx = np.where(c2 == -1)
    c2[idx] = p2[idx]

    return [c1, c2]



# mutation
# - again, need to make sure this keeps the assignments valid.  do
#   this by swapping assignments, rather than randomly assigning
def mutate(p):
    # swap two randomly-selected elements
    l = np.shape(p)[0]
    ii = np.random.randint(low=0, high=l, size=2)

    tmp      = p[ii[0]]
    p[ii[0]] = p[ii[1]]
    p[ii[1]] = tmp

    return p



# update a generation of assignments
def update_generation(assignments, scores):
    # first, sort possible assignments by their score value
    score_inds  = scores.argsort()
    scores      = scores[score_inds[::-1]]
    assignments = assignments[score_inds[::-1]]

    # replace the weakest half with crossover from the strongest half

    # probability for picking "parent" assignments
    prob = scores
    prob[num_parents/2:] = 0.0
    prob = prob - np.min(prob)
    prob = prob / np.sum(prob)

    inds = np.arange(num_parents)

    # now, do the replacement
    for i in range(num_parents/2, num_parents, 2):
        # find two "parent" assignments, weighted by their fitness
        ps = np.random.choice(inds, size=2, replace=False, p=prob)
        p1 = assignments[ps[0]]
        p2 = assignments[ps[1]]

        # stick in two children resulting from the cyclic crossover
        c1, c2 = cyclic_crossover(p1, p2)
        assignments[i  ] = c1
        assignments[i+1] = c2

    # finally, mutate 10% of the population to jump out of local minima
    idx = np.random.choice(np.arange(num_parents), size=num_parents/10, replace=False)
    for i in idx:
        assignments[i] = mutate(assignments[i])

    return assignments



# initialize first generation with uniformly-random assignments
def mk_assignment():
    return np.random.permutation(courses)

num_parents = 1000 # 16000
assignments = np.asarray([ mk_assignment() for i in range(num_parents) ])

scores = np.array([total_happiness(student_preferences, assignment) for assignment in assignments])

print "max initial happiness: {0}".format(np.max(scores))
print "min initial happiness: {0}".format(np.min(scores))



# run the simulation for 100 generations or until converged
for gen in range(1, 100):
    assignments = update_generation(assignments, scores)
    scores = np.array([total_happiness(student_preferences, assignment) for assignment in assignments])

    print "generation: %3d; max: %6.3f; median: %6.3f" % (gen, np.max(scores), np.median(scores))

    if np.max(scores) == np.median(scores):
        print "converged!"
        break



# print out results

# sort parents by their score value
score_inds    = scores.argsort()
scores = scores[score_inds[::-1]]
assignments = assignments[score_inds[::-1]]

h = [ happiness(s, a) for s, a in zip(student_preferences, assignments[0]) ]
c_names = np.asarray(course_names)[assignments[0]]
s_names = np.asarray(student_names)

pretty = [ "{0: <24}: {1: <12} ({2})".format(s, c, score_to_score_inv(hh)) for s, c, hh in zip(s_names, c_names, h) ]
print " "
print "best pairing:"
for p in pretty:
    print p
