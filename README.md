# ta-hammer
when the only tool you have is a hammer...

## about
this is a simple genetic algorithm for optimizing TA/course pairings.
students each give an ordered list of preferences for their courses, and this program attempts to find the optimal pairing.

the program optimizes 'happiness' inferred from students' ranked preferences (https://en.wikipedia.org/wiki/Preference-rank_translation).
different models are implemented in the =models/= directory, and a comparison of results can be found in =test-results/compare.org=

this is a surprisingly difficult problem, but i think the genetic algorithm solves it well!

## technical details
really the only interesting detail here is that there's a constraint that pairings must be *valid*; i.e., each course must have a student assigned.
so i use a cyclic crossover for the crossover function, and i use a swap for the mutation function.
everything else is pretty vanilla, and i haven't yet tweaked any of the parameters!

## example usage with randomly-generated data
```
courses:
[0 1 2 3 4 5 6 7 8 9]
 
student preferences:
[[0 8 4 2 7]
 [8 4 2 6 9]
 [0 3 7 9 4]
 [4 0 5 9 1]
 [2 0 8 7 9]
 [9 2 0 8 4]
 [1 0 7 5 4]
 [1 6 9 8 0]
 [3 6 0 7 9]
 [5 8 6 7 2]]
 
max initial happiness: -11.89
min initial happiness: -100.0
generation:   1; max: -11.890; median: -59.883
generation:   2; max: -11.890; median: -51.909
generation:   3; max: -2.850; median: -50.883
...
generation:  25; max:  0.442; median: -0.176
generation:  26; max:  0.442; median:  0.308
generation:  27; max:  0.567; median:  0.308
generation:  28; max:  0.567; median:  0.393
generation:  29; max:  0.567; median:  0.424
generation:  30; max:  0.567; median:  0.442
generation:  31; max:  0.567; median:  0.442
generation:  32; max:  0.567; median:  0.567
converged!
 
best pairing:
student-1:  course-1  (1st choice)
student-2:  course-9  (1st choice)
student-3:  course-4  (2nd choice)
student-4:  course-5  (1st choice)
student-5:  course-3  (1st choice)
student-6:  course-10 (1st choice)
student-7:  course-8  (3rd choice)
student-8:  course-2  (1st choice)
student-9:  course-7  (2nd choice)
student-10: course-6  (1st choice)
```

## comparison of different happiness models on real-world data

data from =test-data/students-fall.org=

|-----------+----------+-----------+--------+-----------+------|
|           |          | benchmark | andrea | pref-rank | evil |
|-----------+----------+-----------+--------+-----------+------|
| Austin    | Celena   | A         | A      | A         | C    |
| Santos    | Celena   | B         | B      | A         | C    |
| Warren    | Starr    | AA        | AA     | AA        | C    |
| Hodge     | Sylvie   | B         | A      | B         | C    |
| Rodriquez | Yuki     | A         | A      | A         | C    |
| Schmidt   | Lecia    | AA        | AA     | AA        | C    |
| Bradley   | Madeline | AA        | AA     | AA        | C    |
| Phillips  | Gwyneth  | A         | A      | A         | C    |
| Graves    | Celena   | AA        | B      | B         | C    |
| Phelps    | Briana   | AA        | AA     | AA        | C    |
| England   | Hollie   | B         | AA     | AA        | C    |
| Lowery    | Inga     |           | AA     | AA        | C    |
| Bullock   | Isidro   | AA        | AA     | AA        | C    |
| Sweeney   | Sandee   |           | AA     | AA        | C    |
| Goff      | Lean     | AA        | AA     | AA        | C    |
| Tran      | Adriane  | AA        | AA     | AA        | C    |
| Battle    | Loretta  |           | B      | B         | C    |
|-----------+----------+-----------+--------+-----------+------|

the =pref-rank= and =andrea= models perform similarly, and marginally
better than the benchmark
