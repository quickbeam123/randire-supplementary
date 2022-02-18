#!/usr/bin/env python

from __future__ import division

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

def prepare_one((prob_name,seed,extras)):
  # print (prob_name,seed,extras)
  
  to_run = ["./run_shuffling_vampire_50Gi_perf.sh",prob_name,str(seed),extras]

  # print to_run

  output = subprocess.check_output(to_run)

  iterations = 0
  instructions = 0
  result = "---"
  for line in output.split("\n"):
    # print line
    
    if line.startswith("% Activations started:"):
      iterations = int(line.split()[-1])
    if line.startswith("% Instructions burned:"):
      instructions = int(line.split()[-2])
    if line.startswith("% SZS status"):
      if ("Satisfiable" in line or "CounterSatisfiable" in line):
        result = "sat"
      elif ("Theorem" in line or "Unsatisfiable" in line or "ContradictoryAxioms" in line):
        result = "uns"
      else:
        result = "unk"

  return (prob_name, seed, result, iterations, instructions)

class ProbStat:
  def __init__(self):
    self.tot_iter = 0
    self.tot_instr = 0
    self.successes = 0
    self.attempts = 0
    
  def __repr__(self):
    return "iter{} instr{} succ{} attem{} means{}".format(self.tot_iter,self.tot_instr,self.successes,self.attempts,str(self.last_instr_means))
  
  def add(self, success, iterations, instructions):
    self.attempts += 1
    if success != "---" and success != False:
      self.successes += 1
    self.tot_iter += iterations
    self.tot_instr += instructions
  
def load_partial(prob_info,partial):
  for (prob_name, seed, success, iterations, instructions) in partial:
    info = prob_info[prob_name]
    info.add(success, iterations, instructions)
                
    # print seed, success, iterations, instructions
    # print repr(info), info.stable()

if __name__ == "__main__":
  # Sample the whole TPTP so much that we can see how much chaos is really in there
  # - actually, this is an add-on which loads two explicitly named folders
  # - and additionally runs as many probes on behalf of the first folder
  #   so that it has at least as many for each problem as those in the second
  # - the actual params for vampire still need to be hardwired here!
  #
  # to be run as in: ./tptpVarianceCompensate.py 'tptp_db(dis10)' 'tptp_db(dis10+bce)'
  
  # read the full problem list
  prob_list = []
  with open("problemsSTD.txt","r") as f:
    for line in f:
      prob_list.append(line[:-1])

  prob_info = defaultdict(ProbStat)

  # read previously computed results (update last_db_id)
  file_begin = "tptprun."
  file_end = ".pkl"
  db_dir = sys.argv[1]
  last_db_id = -1
  
  for file in os.listdir(db_dir):
    if file.startswith(file_begin) and file.endswith(file_end):
      id = int(file.split(".")[1])
      if id > last_db_id:
        last_db_id = id
    
      with open(os.path.join(db_dir, file),'r') as f:
        partial = pickle.load(f)
  
      load_partial(prob_info,partial)

  prob_info2 = defaultdict(ProbStat)
  db_dir2 = sys.argv[2]
  for file in os.listdir(db_dir2):
    if file.startswith(file_begin) and file.endswith(file_end):
      with open(os.path.join(db_dir2, file),'r') as f:
        partial = pickle.load(f)
  
      load_partial(prob_info2,partial)

  tasks = []
  for prob,info in prob_info.items():
    info2 = prob_info2[prob]

    for _ in range(info2.attempts - info.attempts):
      seed = random.randint(1,0x7fffffff)
      # 1) with proof printing may take ages for big proofs!
      # 2) randomize
      # 3) the strat itself
      tasks.append((prob,seed,"-p off      -si on -rawr on -rtra on     -sa discount -awr 10 -av off"))

  print len(tasks)
  sys.stdout.flush()

  pool = Pool(processes=70)
  results = pool.map(prepare_one, tasks, chunksize = 1)

  # store results
  last_db_id += 1
  with open(os.path.join(db_dir,file_begin+str(last_db_id)+file_end),'w') as f:
    pickle.dump(results,f)
