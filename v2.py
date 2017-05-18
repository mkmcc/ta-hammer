import numpy as np

################################################################################
## import course and student data

# import course list
course_names = np.loadtxt('courses.dat',
                          usecols=(0,),
                          dtype=np.dtype((str, 35)))
# convert to integer format
courses = np.arange(len(course_names))


# import student preferences
students_str = np.loadtxt('students.csv',
                           dtype=np.dtype((str, 35)),
                           delimiter=',')

# split names from data
student_names = students_str[:,:2]
students_str  = students_str[:,2:]


# convert student preference data to integer format
def course_name_to_number(name):
    return np.where(course_names == name)[0][0]

vfunc = np.vectorize(course_name_to_number)

students = np.asarray([ vfunc(s) for s in students_str ])

################################################################################



################################################################################
## genetic optimization algorithm

# utility functions
def not_contains(a, elem):
    return np.intersect1d(a, elem).shape[0] == 0



# happiness function
#
# https://en.wikipedia.org/wiki/Preference-rank_translation
weights = [ 0.75, 0.17, 0.06, 0.02, 0.0 ]
# TODO: maybe allow students to specify their own weights
#       alternatively, tweak weights so everyone gets at least their
#       third choice... i think this is better!
nstudents = students.shape[0]
bad = -10.0 * nstudents
#weights = [ 0.75, 0.17, 0.08, -nstudents, bad ]


def happiness(student, course):
    if not_contains(student, course):
        return bad

    return weights[np.where(student == course)[0][0]]

def total_happiness(students, assignments):
    scores = [ happiness(s, a) for s, a in zip(students, assignments) ]
    student_happiness = np.sum(np.asarray(scores)) # todo: try 1/sum(1/scores)

    return student_happiness / nstudents



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
    ii = np.random.randint(low=0, high=l-1, size=2)
    tmp = p[ii[0]]
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

num_parents = 16000
assignments = np.asarray([ mk_assignment() for i in range(num_parents) ])

scores = np.array([total_happiness(students, assignment) for assignment in assignments])

print "max initial happiness: {0}".format(np.max(scores))
print "min initial happiness: {0}".format(np.min(scores))



# run the simulation for 100 generations or until converged
for gen in range(1, 100):
    assignments = update_generation(assignments, scores)
    scores = np.array([total_happiness(students, assignment) for assignment in assignments])

    print "generation: %3d; max: %6.3f; median: %6.3f" % (gen, np.max(scores), np.median(scores))

    if np.max(scores) == np.median(scores):
        print "converged!"
        break



# print out results

# sort parents by their score value
score_inds    = scores.argsort()
scores = scores[score_inds[::-1]]
assignments = assignments[score_inds[::-1]]

h = [ happiness(s, a) for s, a in zip(students, assignments[0]) ]
c_names = np.asarray(course_names)[assignments[0]]
s_names = np.asarray(student_names)

pretty = [ "{0}: {1} ({2})".format(s, c, hh) for s, c, hh in zip(s_names, c_names, h) ]
print " "
print "best pairing:"
for p in pretty:
    print p
