#!/bin/bash

# arguments:
# 1) vampire executable
# 2) instruction limit (such that vampire will manage to burn all the instructions under 100s), e.g. "50000", which amounts to about 15s
# 3) input syntax ("tptp" or "smtlib2")
# 4) params defining strategy "-sa discount -awr 10"
# 5) params defining randomizatoin "-si on -rawr on -rtra on"
# 6) random seed
# 7) problem

timelimit -t 100 -T 1 $1 -t 100 -i $2 -stat full -p off --input_syntax $3 $4 $5 --random_seed $6 $7 | grep "Activations\|Instructions\|SZS status"

exit 0
