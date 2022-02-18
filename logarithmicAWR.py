#!/usr/bin/env python

import sys, os

import cPickle as pickle
import gzip
import math, random
from collections import defaultdict
import subprocess
import tempfile

import time

from fractions import Fraction

from multiprocessing import Pool

def prepare_one((prob_name,age,wei,seed,extras)):
  # print (prob_name,age,wei,seed)
  # print ["./run_with_aw_and_seed.sh",prob_name,str(seed),"{}:{}".format(age,wei)]

  to_run = ["./run_shuffling_vampire_awr.sh",prob_name,str(seed),"{}:{}".format(age,wei),extras]

  # print to_run

  output = subprocess.check_output(to_run)

  iterations = 0
  instruction = 0
  prooflen = 0
  success = False
  for line in output.split("\n"):
    # print line
  
    if line.startswith("%"):
  
      if line.startswith("% Activations started:"):
        iterations = int(line.split()[-1])
      if line.startswith("% Instructions burned:"):
        instruction = int(line.split()[-2])
      if line.startswith("% SZS status") and \
        ("Satisfiable" in line or "CounterSatisfiable" in line or "Theorem" in line or "Unsatisfiable" in line or "ContradictoryAxioms" in line):
        success = True
    else:
      prooflen += 1

  return ((age,wei,seed),(success, iterations, instruction, prooflen))

if __name__ == "__main__":
  #
  # with the aim of creating a curve like Fig 2 in https://link.springer.com/content/pdf/10.1007%2F978-3-030-29436-6_27.pdf
  # run vampire on a given problem for a range on awr points between -10 and 2 (when logarithmied)
  #
  # more than one sample is supported for awr value (then different random seeds are used)
  #
  # then store all this in a pickle for later processing
  #
  # to be run as in: ./logarithmicAWR.py Problems/PRO/PRO017+2.p _shuffleAll "-si on -rawr on -rtra on" # extra_name "extra vampire options"
  
  num_samples = 100
  
  prob_name = sys.argv[1]
  prob_name_spl = prob_name.split("/")[-1].split(".")
  assert(len(prob_name_spl) > 1)
  extra_tag = sys.argv[2]
  extras = sys.argv[3]
  
  out_name = "{}{}.pkl".format(prob_name_spl[0],extra_tag)
  
  tasks = []
  precision = 100
  for int_x in xrange(12*precision+1):
    x = 1.0*int_x/precision - 10.0
    
    # print x,
    
    x = math.pow(2,x)
  
    # print x,
  
    # (num,den) = x.as_integer_ratio()
    f = Fraction.from_float(x).limit_denominator()
    
    age = f.numerator
    wei = f.denominator
        
    assert(age >= 0 and wei >= 0 and (age != 0 or wei != 0))
  
    # print age, wei
  
    for _ in xrange(num_samples):
      seed = random.randint(1,0x7fffffff)
      tasks.append((prob_name,age,wei,seed,extras))

  pool = Pool(processes=15)
  results = pool.map(prepare_one, tasks, chunksize = 1)
  
  '''
  results = []
  for task in tasks:
    results.append(prepare_one(task))
  '''

  # print results

  with open(out_name,'w') as f:
    pickle.dump(results,f)


