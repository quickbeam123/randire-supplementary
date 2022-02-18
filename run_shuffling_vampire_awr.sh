#!/bin/bash
timelimit -t 100 -T 1 ./vampire_rel_randire_6024 $1 -t 100 -i 100000 --input_syntax tptp -stat full -sa discount --random_seed $2 -awr $3 $4
exit 0
