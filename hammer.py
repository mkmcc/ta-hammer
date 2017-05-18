import numpy as np

# mock up some synthetic data to work with
#
# TODO: really want to be able to import this from some CSV file
#
ncourses  = 10
nstudents = ncourses

course_names = [ "course-{0}".format(i+1) for i in range(ncourses) ]
courses = np.arange(len(course_names))

def mkstudent():
    return np.random.choice(courses, size=5, replace=False)

student_names = [ "student-{0}".format(i+1) for i in range(nstudents) ]
students = np.asarray([ mkstudent() for i in range (nstudents) ])

print "courses:"
print courses
print " "
print "student preferences:"
print students
print " "



# happiness function
#
# https://en.wikipedia.org/wiki/Preference-rank_translation
weights = [ 0.75, 0.17, 0.06, 0.02, 0.0 ]
# TODO: maybe allow students to specify their own weights
#       alternatively, tweak weights so everyone gets at least their
#       third choice... i think this is better!
weights = [ 0.75, 0.17, 0.08, -nstudents, -10*nstudents ]

bad = -100.0

def happiness(student, course):
    ind = np.intersect1d(student, course)
    if ind.shape[0] == 0:
        return bad

    return weights[np.where(student == course)[0][0]]

# difference two lists
def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]

def total_happiness(students, assignments):
    scores = [ happiness(s, a) for s, a in zip(students, assignments) ]
    student_happiness = np.sum(np.asarray(scores)) # todo: try 1/sum(1/scores)

    return student_happiness / nstudents



# crossover
def contains(a, elem):
    return np.intersect1d(a, elem).shape[0] == 0

def cyclic_crossover(p1, p2):
    # initialize children to -1
    c1 = np.arange(np.shape(p1)[0]) * 0 - 1
    c2 = np.arange(np.shape(p1)[0]) * 0 - 1

    # loop until we reach a closed cycle, filling c1 from p1
    i = 0
    while(contains(c1, p1[i])):
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
    # sort parents by their score value
    score_inds    = scores.argsort()
    scores = scores[score_inds[::-1]]
    assignments = assignments[score_inds[::-1]]

    # replace the weakest half with crossover from the strongest half
    prob = scores
    prob[num_parents/2:] = 0.0
    prob = prob - np.min(prob)
    prob = prob / np.sum(prob)

    inds = np.arange(num_parents)

    for i in range(num_parents/2, num_parents, 2):
        # find two parents, weighted by their fitness
        ps = np.random.choice(inds, size=2, replace=False, p=prob)
        p1 = assignments[ps[0]]
        p2 = assignments[ps[1]]

        # stick in two children resulting from the cyclic crossover
        c1, c2 = cyclic_crossover(p1, p2)
        assignments[i  ] = c1
        assignments[i+1] = c2

    # mutate 10% of the population
    idx = np.random.choice(np.arange(num_parents), size=num_parents/10, replace=False)
    for i in idx:
        assignments[i] = mutate(assignments[i])

    return assignments



# initialize first generation
def mk_assignment():
    return np.random.permutation(courses)

num_parents = 1000
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