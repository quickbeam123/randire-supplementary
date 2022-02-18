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

def prepare_one(task):
  (vampire,ilimit,syntax,strat,randomization,seed,prob_name) = task
  # print (vampire,ilimit,syntax,strat,randomization,seed,prob_name)
  
  to_run = ["./run_shuffling_vampire_generic.sh",vampire,ilimit,syntax,strat,randomization,seed,prob_name]

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

kolik = 10

class ProbStat:
  def __init__(self):
    self.tot_iter = 0
    self.tot_instr = 0
    self.successes = 0
    self.attempts = 0
    
    self.last_instr_means = []
  
  def __repr__(self):
    return "iter{} instr{} succ{} attem{} means{}".format(self.tot_iter,self.tot_instr,self.successes,self.attempts,str(self.last_instr_means))
  
  def add(self, success, iterations, instructions):
    self.attempts += 1
    if success != "---":
      self.successes += 1
    self.tot_iter += iterations
    self.tot_instr += instructions
  
    instr_mean = self.tot_instr / self.attempts
  
    self.last_instr_means.append(instr_mean)
    if len(self.last_instr_means) > kolik:
      self.last_instr_means = self.last_instr_means[-kolik:]
    
  def stable(self,prob_name=None): # prob_name given just to debug
    # print repr(self)
    # print "stable for", prob_name,
    if len(self.last_instr_means) < kolik:
      # print False, "not enough attepts yet"
      return False
    last = self.last_instr_means[-1]
    if last < 1.0:
      # print True, "was always too easy"
      return True
    for mean in self.last_instr_means[:-1]:
      if mean < 1.0:
        # print False, "old mean was small while list one isnt?"
        return False
      if last / mean < 0.99 or mean / last < 0.99:
        # print False, "either", last / mean, "or", mean / last, "too small"
        return False
    # print True, "seems truly stable"
    return True

def load_partial(prob_info,partial):
  for (prob_name, seed, success, iterations, instructions) in partial:
    info = prob_info[prob_name]
    info.add(success, iterations, instructions)
        
    # print seed, success, iterations, instructions
    # print repr(info), info.stable()

if __name__ == "__main__":
  # Sample the whole library so much that we can see how much chaos is really in there
  #
  # to be run as in: ./genericVariance.py 50000 "tptp" "problemsSTD.txt" "-sa discount -awr 10" "-si on -rawr on -rtra on" "tptp_db"
  # or
  # as in: ../shuffling/genericVariance.py 20000 "smtlib2" "smt4vamp.txt" "-sa discount -awr 10" "-si on -rawr on -rtra on" "../shuffling/smtlib_discount10_shuffleAll"
  # the db_dir must exist already
  
  vampire = sys.argv[1]
  ilimit = sys.argv[2]
  syntax = sys.argv[3]
  prob_list_file = sys.argv[4]
  strat = sys.argv[5]
  randomization = sys.argv[6]
  db_dir = sys.argv[7]
  
  # read the full problem list
  prob_list = []
  with open(prob_list_file,"r") as f:
    for line in f:
      prob_list.append(line[:-1])

  prob_info = defaultdict(ProbStat)

  # read previously computed results (update last_db_id)
  file_begin = "run."
  file_end = ".pkl"
  last_db_id = -1
  for file in os.listdir(db_dir):
    if file.startswith(file_begin) and file.endswith(file_end):
      id = int(file.split(".")[1])
      if id > last_db_id:
        last_db_id = id
    
      print "Reading",file
      with open(os.path.join(db_dir, file),'r') as f:
        partial = pickle.load(f)
  
      load_partial(prob_info,partial)

  pool = Pool(processes=40)
  
  active_prob_list = prob_list
  while True:
    # decide for which problems we still want to run
    active_prob_list = [problem for problem in active_prob_list if not prob_info[problem].stable(problem)]
    print len(active_prob_list)
    sys.stdout.flush()
  
    if len(active_prob_list) == 0:
      break
  
    # create the current tast batch
    tasks = []
    for problem in active_prob_list:
      seed = random.randint(1,0x7fffffff)
      # 1) with proof printing may take ages for big proofs!
      # 2) randomize
      # 3) the strat itself
      # tasks.append((problem,seed,"-p off      -si on -rawr on -rtra on     -sa otter -awr 1 -newcnf on -lcm predicate -gs on -av off -s 11 -sp frequency -nwc 2.5"))
      # tasks.append((problem,seed,"-p off      -si on -rawr on -rtra on     -sa discount -awr 10 -bce on"))
      tasks.append((vampire,ilimit,syntax,strat,randomization,str(seed),problem))

    results = pool.map(prepare_one, tasks, chunksize = 1)

    '''
    results = []
    for task in tasks:
      results.append(prepare_one(task))
    '''

    load_partial(prob_info,results)

    # store results
    last_db_id += 1
    with open(os.path.join(db_dir,file_begin+str(last_db_id)+file_end),'w') as f:
      pickle.dump(results,f)

