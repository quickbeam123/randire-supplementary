#!/usr/bin/env python3

import sys, os

import gzip
import math, random, pickle
from collections import defaultdict

import numpy as np

instrout = 50000

class ProbStat:
  def __init__(self):
    self.successes = []
    self.iters = []
    self.instrs = []
    self.seeds = []

  def add(self, success, iterations, instructions, seed):
    self.iters.append(iterations)
    self.instrs.append(instructions)
    self.successes.append(success)
    self.seeds.append(seed)

  def get_mean_par(self,par=2):
    # print(list(zip(self.successes,self.instrs)))
    return sum(instr if (self.successes[i] != False and self.successes[i] != "---") else par*instrout\
      for i,instr in enumerate(self.instrs)) / len(self.instrs)

  def get_solve_prob(self):
    return sum(1 for succ in self.successes if succ != False and succ != "---") / len(self.successes)

def load_partial(prob_info,partial):
  for (prob_name, seed, success, iterations, instructions) in partial:
    info = prob_info[prob_name]
    info.add(success, iterations, instructions, seed)

if __name__ == "__main__":
  # Sample the whole TPTP so much that we can see how much chaose is really in there
  #
  # to be run as in:
  # ./compareTwo.py 'tptp_db(dis10)' 'tptp_db(dis10-av)' problemsSTD_50Gi_rel_shuffling_6024_discount10*.pkl
  # ./compareTwo.py 'tptp_db(dis10)' 'tptp_db(dis10+bce)' problemsSTD_50Gi_rel_shuffling_6024_discount10_bce-on.pkl
  
  prob_infos = []

  # read previously computed results (update last_db_id)
  # file_begin = "tptprun."
  file_end = ".pkl"
  for db_dir in sys.argv[1:3]:
    prob_info = defaultdict(ProbStat)
    last_db_id = -1
    for file in os.listdir(db_dir):
      if file.endswith(file_end):
        id = int(file.split(".")[1])
        if id > last_db_id:
          last_db_id = id
      
        # print("Reading",file)
        with open(os.path.join(db_dir, file),'rb') as f:
          partial = pickle.load(f,encoding='utf-8')
    
        load_partial(prob_info,partial)
    prob_infos.append(prob_info)

  assert len(prob_infos) == 2
  
  mask_hack = defaultdict(bool)
  if len(sys.argv) > 3:
    for file in sys.argv[3:]:
      with open(file,'rb') as f:
        one_mast = pickle.load(f,encoding='utf-8')
        for prob,res in one_mast.items():
          mask_hack[prob] |= res[-1]

  with open("probinfo7.5.0.pkl",'rb') as f:
    probinfo = pickle.load(f,encoding='utf-8')

  Xs = ([],[])
  Ys = ([],[])

  sum_frac_diff_1 = 0.0
  sum_frac_diff_2 = 0.0
  
  sum_par2_diff_1 = 0.0
  sum_par2_diff_2 = 0.0
  
  sum_frac_compl_1 = 0.0
  sum_frac_compl_2 = 0.0

  sum_frac_var_1 = 0.0
  sum_frac_var_2 = 0.0

  corner_hist = defaultdict(int)

  par = 2
  to_sort = []
  for prob in prob_info:
    idx = 0
    if mask_hack:
      # print(prob,mask_hack[prob])
      if mask_hack[prob]:
        idx = 1

    par2_1 = prob_infos[0][prob].get_mean_par(par)
    par2_2 = prob_infos[1][prob].get_mean_par(par)
    
    v1 = prob_infos[0][prob].get_solve_prob()
    v2 = prob_infos[1][prob].get_solve_prob()

    Xs[idx].append(v1)
    Ys[idx].append(v2)

    if v1 in [0.0,1.0] and v2 in [0.0,1.0]:
      corner_hist[(v1,v2)] += 1
      if v1 != v2:        
        print((v1,v2),prob)
        if prob in probinfo:
          print(probinfo[prob.split("/")[-1]])
        if v1 < v2:
          print("   ",prob_infos[1][prob].get_mean_par(1))
        else:
          print("   ",prob_infos[0][prob].get_mean_par(1))
    
    '''
    if v2 == 0.0:
      if v1 == 0.0:
        frac = 1.0
      else:
        frac = float('inf')
    else:
      frac = v1/v2
    '''
    to_sort.append((v1-v2,v1,v2,prob))
    
    sum_frac_diff_1 += max(v1-v2,0)
    sum_frac_diff_2 += max(v2-v1,0)
    
    # print(prob,par2_1,par2_2)
    sum_par2_diff_1 += max(par2_1-par2_2,0)
    sum_par2_diff_2 += max(par2_2-par2_1,0)
    
    sum_frac_compl_1 += (1-v2)*v1
    sum_frac_compl_2 += (1-v1)*v2
    
    sum_frac_var_1 += (1-v1)*v1
    sum_frac_var_2 += (1-v2)*v2
  
  sum_par2_diff_1 /= len(prob_info)
  sum_par2_diff_2 /= len(prob_info)
  
  import matplotlib.pyplot as plt
  fig, ax1 = plt.subplots(figsize=(3, 3))
  # ax1.scatter(Xs, Ys, c = Cs, s = 1)
  ax1.scatter(Xs[0], Ys[0], s = 1, color = "tab:red")
  if Xs[1]:
    # Ss = [corner_hist[x,y] for x,y in zip(Xs[1], Ys[1])]
    Ss = 1
    ax1.scatter(Xs[1], Ys[1], s = Ss, color = "tab:blue")

  ax1.set_xlabel(u'dis10')
  # ax1.set_ylabel(u'dis10 \u2014 AVATAR')
  ax1.set_ylabel(u'dis10 + BCE')

  fig.tight_layout()

  plt.savefig("compare_two_prob_scatter.png",format='png', dpi=300)
  plt.close(fig)
  
  print("sum_frac_diff:",sum_frac_diff_1-sum_frac_diff_2,"=",sum_frac_diff_1,"-",sum_frac_diff_2)
  print("sum_par2_diff:",sum_par2_diff_1-sum_par2_diff_2,"=",sum_par2_diff_1,"-",sum_par2_diff_2)
  
  print("sum_frac_compl:",sum_frac_compl_1,sum_frac_compl_2)
  print("sum_frac_var:",sum_frac_var_1,sum_frac_var_2)
  
  # print(sum_frac_diff/len(prob_info.keys()))
  
  print("Cornerhist")
  for (v1,v2),cnt in sorted(corner_hist.items(),reverse=True,key=lambda x: x[1])[:4]:
    print((v1,v2),cnt)

  exit(0)
  to_sort.sort()
  
  for i,(frac_diff,v1,v2,prob) in enumerate(to_sort):
    print(i,frac_diff,v1,v2)
    print(prob,probinfo[prob.split("/")[-1]])
    print(list(zip(prob_infos[0][prob].successes,prob_infos[0][prob].seeds)))
    print(list(zip(prob_infos[1][prob].successes,prob_infos[1][prob].seeds)))
    print()
    
