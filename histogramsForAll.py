#!/usr/bin/env python3

import sys, os

import gzip
import math, random, pickle
from collections import defaultdict

import numpy as np

class SoundnessCheck:
  def __init__(self,probinfo):
    self.probinfo = probinfo
  
  def check(self,prob,stat):
    (_rate,spc) =  probinfo[prob.split("/")[-1]]
    tptp_stat_raw = spc.split("_")[1]

    if tptp_stat_raw in ["UNS","THM","CAX"]:
      tptp_stat = "uns"
    elif tptp_stat_raw in ["SAT","CSA"]:
      tptp_stat = "sat"
    else:
      tptp_stat = "unk"

    # we can't always trust the probinfo
    if prob == 'Problems/CSR/CSR188+1.p' and tptp_stat_raw == "CSA":
      tptp_stat = "uns"

    if stat != "---" and tptp_stat != stat:      
      print(prob,stat,tptp_stat_raw) 


class ProbStat:
  def __init__(self):
    self.results = []
    self.iters = []
    self.instrs = []
    self.seeds = []

  def add(self, result, iterations, instructions, seed):
    self.iters.append(iterations)
    self.instrs.append(instructions)
    self.results.append(result)
    self.seeds.append(seed)

def load_partial(prob_info,partial):
  for (prob_name, seed, result, iterations, instructions) in partial:
    info = prob_info[prob_name]
    info.add(result, iterations, instructions, seed)

if __name__ == "__main__":
  # Sample the whole TPTP so much that we can see how much chaose is really in there
  #
  # to be run as in: ./histogramsForAll.py tptp_db\(dis10\) problemsSTD_50Gi_rel_shuffling_6024_discount10.pkl
  
  prob_info = defaultdict(ProbStat)

  # file_begin = "tptprun."
  file_end = ".pkl"
  db_dir = sys.argv[1]
  for file in os.listdir(db_dir):
    if file.endswith(file_end): # file.startswith(file_begin) and\          
      # print("Reading",file)
      with open(os.path.join(db_dir, file),'rb') as f:
        partial = pickle.load(f,encoding='utf-8')
  
      load_partial(prob_info,partial)
    
  stats_hack = None
  if len(sys.argv) > 2:
    with open(sys.argv[2],'rb') as f:
      stats_hack = pickle.load(f,encoding='utf-8')

  with open("probinfo7.5.0.pkl",'rb') as f:
    probinfo = pickle.load(f,encoding='utf-8')
  sc = SoundnessCheck(probinfo)

  # hunting for the coefficient of variation (https://en.wikipedia.org/wiki/Coefficient_of_variation)
  '''  
  to_sort = []
  for prob_name,info in prob_info.items():
    frac = sum(1 for succ in info.successes if succ != False and succ != "---")/len(info.successes)
    instructions = np.array(info.instrs)
    mean = np.mean(instructions)
    std = np.std(instructions)
    if mean > 0.0:
      cv = std/mean
    else:
      cv = 0.0

    to_sort.append((frac < 1.0,cv,mean,std,frac,\
      info.instrs,info.iters,info.successes,info.seeds,prob_name))
  
  CVs = []
  to_sort.sort()
  for i, (isHard,cv,mean,std,frac,instructions, iterations, successes, seeds, prob_name) in enumerate(to_sort):
    if frac > 0.0:
      CVs.append(cv)

    print(i,prob_name,isHard,cv,mean,std,frac)
    print(instructions)
    print(iterations)
    print(seeds)
    print(successes)
    print(probinfo[prob_name.split("/")[-1]])
    print()
  '''

  import matplotlib.pyplot as plt
  import matplotlib.patches as mpatches

  # udelame "kaktusy"
  '''
  plain_sample = []
  plain_strat = []
  double_strat = []
  for prob_name,info in prob_info.items():
    succs = info.successes
    instrs = info.instrs

    idx = random.randint(1,len(succs))-1
    if succs[idx] == "sat" or succs[idx] == "uns":
      plain_sample.append(instrs[idx])

    if "sat" in succs or "uns" in succs:
      plain_strat.append(sum([instr if succs[i] != False and succs[i] != "---" else 100000 for i,instr in enumerate(instrs)])/len(instrs))

    cnt = 0
    suma = 0.0
    had_succ = False
    for i in range(len(succs)):
      if succs[i] != False and succs[i] != "---":
        had_succ = True
        val_i = instrs[i]
      else:
        val_i = 100000
      for j in range(len(succs)):
        val_j = instrs[i] if succs[i] != False and succs[i] != "---" else 100000
        
        cnt += 1        
        suma += 2*min(val_i,val_j)
        
    if had_succ:
      double_strat.append(suma/cnt)
  
  plain_strat.sort()
  plain_sample.sort()
  double_strat.sort()

  fig, ax1 = plt.subplots(figsize=(6, 2.5))

  # color = 'tab:blue'
  ax1.set_xlabel('individual (first-order) TPTP problems')
  ax1.set_ylabel('mean par-2 to solve (Gi)')
  ax1.plot(range(len(plain_strat)),plain_strat,linewidth =1 )
  ax1.plot(range(len(plain_sample)),plain_sample,linewidth =1 )
  ax1.plot(range(len(double_strat)),double_strat,linewidth =1 )

  ax1.set_xlim([7000,10000])

  plt.savefig("cactus.png",format='png', dpi=300)
  plt.close(fig)

  exit(0)
  '''

  how_many_weird = 0

  # A newer TPTP graph 
  PAR_PENALTY = 100000
  to_sort = []
  for prob_name,info in prob_info.items():
    '''
    if prob_name == 'Problems/NLP/NLP011+1.p':
      print(list(zip(info.seeds,info.results,info.instrs)))
    '''

    succ_cnt = 0
    instrs = []
    for i,instr in enumerate(info.instrs):
      if info.results[i] in [True, "sat", "uns"]:
        succ_cnt += 1
      else:
        instr = PAR_PENALTY
      instrs.append(instr)

      sc.check(prob_name,info.results[i])

    probsolve = succ_cnt/len(info.instrs)
  
    if stats_hack and probsolve == 0.0:
      resvec = stats_hack[prob_name]
      if resvec[0] == "sat" or resvec[0] == "uns":
        how_many_weird += 1
        print(prob_name)
        print(stats_hack[prob_name])
        print(list(zip(info.instrs,info.results)))
        print()

    to_sort.append((probsolve,instrs,prob_name))
    
  if how_many_weird > 0:
    print("how_many_weird",how_many_weird)

  Xs = []
  Ys = []

  how_many_contribs = 4
  addional_contribs = np.zeros(1+how_many_contribs)

  how_many_cacti = 1 # additional cacti show parallel performance of running multiple compies of the strat (as in the LPAR92 paper)
  weighted_instrs = tuple([] for _ in range(how_many_cacti))

  to_sort.sort()
  easy_cnt = 0
  med_cnt = 0

  for i, (probsolve, instrs, prob_name) in enumerate(to_sort):
    Xs.append(i)
    Ys.append(probsolve)

    if probsolve == 1.0:
      easy_cnt += 1
    elif probsolve > 0.0:
      med_cnt += 1

    instrs.sort()

    l = len(instrs)
    # print(l)
    for instr in instrs:
      for k in range(how_many_cacti):      
        w = (l/len(instrs))**(k+1) - ((l-1)/len(instrs))**(k+1)
        # print(k,l,w)
        weighted_instrs[k].append((instr,w))
      l -= 1
    # print()
    
    frac = probsolve
    contrib = [frac]
    compl = (1.0-frac)
    for _ in range(how_many_contribs):
      frac *= compl
      contrib.append(frac)
    addional_contribs += np.array(contrib)

  Ys.sort(reverse=True)

  expect = addional_contribs[0].item()
  var = addional_contribs[1].item()
  sigma = math.sqrt(var)
    
  fig, ax1 = plt.subplots(figsize=(6, 2.0))
  
  color = 'tab:blue'
  ax1.set_xlabel('(first-order) TPTP problems')
  ax1.set_ylabel('prob. of solving', color=color)
  ax1.plot(Xs,Ys,color=color)
  ax1.tick_params(axis='y', labelcolor=color)

  rect = mpatches.Rectangle((easy_cnt,0.0),med_cnt,1.0, 
                        #fill=False,
                        alpha=0.1,
                        facecolor=color)
  plt.gca().add_patch(rect)
  
  ax2 = ax1.twinx()

  # kaktusy 
  color = 'tab:red'
  ax2.set_ylabel('instructions (1e10)', color=color)  # we already handled the x-label with ax1
  ax2.tick_params(axis='y', labelcolor=color)
  ax2.set_yticks(np.arange(0, 5.1, step=1.0))
  # ax2.ticklabel_format(axis='y', style='sci', scilimits=(-3, 3), useOffset=False)
  
  for k in range(how_many_cacti):
    Xs = []
    Ys = []
    accum_w = 0.0
    for (instr,w) in sorted(weighted_instrs[k]):
      if instr > 50000:
        break
      accum_w += w
      # print(accum_w,instr / 10000)
      Xs.append(accum_w)
      Ys.append(instr / 10000)
      
    ax2.plot(Xs,Ys,color=color)

  '''
  color = 'tab:red'
  ax2.set_ylabel('coeff of variation', color=color)  # we already handled the x-label with ax1
  ax2.tick_params(axis='y', labelcolor=color)
  ax2.scatter(range(len(CVs)),CVs,marker='.',s=1,color=color)
  '''

  '''
  # cactus for: pre-emptively switching machines running (idx+1) copies of the same strat
  idx = 1

  Xs = []
  Ys = []
  accum_w = 0.0
  for (instr,w) in sorted(weighted_instrs[idx]):
    if instr > 25000:
      break
    accum_w += w
    # print(accum_w,instr / 10000)
    Xs.append(accum_w)
    Ys.append(instr / 10000 * (idx+1))    
  ax2.plot(Xs,Ys,color=color,linestyle="dotted")
  '''
  
  print("Easycnt",easy_cnt,"+ medcnt",med_cnt,"=",easy_cnt+med_cnt)
  print("Expect",expect,"+/-",sigma)
  print("Additional contribs",addional_contribs)
  
  for line in [np.sum(addional_contribs[0:i+1]) for i in range(len(addional_contribs))]:
    ax2.axvline(line,ymin=0.05, ymax=0.95,ls='--', lw=1,color="gray")
  
  fig.tight_layout() # otherwise the right y-label is slightly clipped
  
  ax1.set_xlim([7000,10000])
  # ax1.set_xlim([0,(easy_cnt+med_cnt)*1.2])
  # ax1.set_xlim([250,800])
  
  plt.savefig("prob_solve.png",format='png', dpi=300)

  plt.close(fig)
  
  # The old TPTP graph below
  """
  to_sort = []
  for prob_name,info in prob_info.items():

    # SKIPPING SAT AT THE MOMENT!
    '''
    if "sat" in info.successes:
      continue
    '''

    to_sort.append((sum(1 for succ in info.successes if succ != False and succ != "---")/len(info.successes),\
      info.instrs,info.iters,info.successes,info.seeds,prob_name))
  
  Xs = []
  YsZs = []

  how_many_contribs = 6
  addional_contribs = np.zeros(1+how_many_contribs)

  to_sort.sort()
  for i, (frac, instructions, iterations, successes, seeds, prob_name) in enumerate(to_sort):
    '''
    print(i,prob_name,frac,sum(instructions)/len(instructions))
    print(list(zip(instructions,seeds)))
    print(iterations)
    print(successes)
    print()
    '''
    Xs.append(i)
    YsZs.append((frac,-sum([instr if successes[i] != False and successes[i] != "---" else 100000 for i,instr in enumerate(instructions)])/len(instructions))) # minus for the reverse sort

    contrib = [frac]
    compl = (1.0-frac)
    for _ in range(how_many_contribs):    
      frac *= compl
      contrib.append(frac)      
    addional_contribs += np.array(contrib)

  YsZs.sort(reverse=True)
  Ys = [ y for (y,z) in YsZs]
  Zs = [ -z / 1000 for (y,z) in YsZs] # minus the value back (don't wast space on the zeros)

  expect = addional_contribs[0].item()
  var = addional_contribs[1].item()
  sigma = math.sqrt(var)
    
  fig, ax1 = plt.subplots(figsize=(6, 2.5))
  
  color = 'tab:blue'
  ax1.set_xlabel('individual (first-order) TPTP problems')
  ax1.set_ylabel('probability of solving', color=color)
  ax1.plot(Xs,Ys,color=color)
  ax1.tick_params(axis='y', labelcolor=color)
  
  ax2 = ax1.twinx()
  
  color = 'tab:red'
  ax2.set_ylabel('mean par-2 score (Gi)', color=color)  # we already handled the x-label with ax1
  ax2.scatter(Xs,Zs,marker='.',s=1,color=color)
  ax2.tick_params(axis='y', labelcolor=color)
  ax2.ticklabel_format(axis='y', style='sci', scilimits=(-3, 3), useOffset=False)
  
  print("Expect",expect,"+/-",sigma)
  print("Additional contribs",addional_contribs)
  
  for line in [np.sum(addional_contribs[0:i+1]) for i in range(len(addional_contribs))]:
    ax2.axvline(line,ymin=0.05, ymax=0.95,ls='--', lw=1,color="gray")
  
  fig.tight_layout() # otherwise the right y-label is slightly clipped
  
  ax1.set_xlim([7000,10000])
  
  plt.savefig("prob_solve.png",format='png', dpi=300)

  plt.close(fig)
  
  exit(0)
  """
  
  # histograms for all (careful, targetfolder assumed in sys.argv[2])
  """
  import matplotlib.pyplot as plt
  
  for prob_name,info in prob_info.items():
    out_name = prob_name.split("/")[-1]+"ng"
        
    print(prob_name)
    print("  ",info.instrs)
    print("  ",info.successes)
    
    max_graph = 1.1*max(info.instrs)
    
    data = info.instrs
        
    fig, ax1 = plt.subplots(figsize=(8, 6))

    plt.hist(data,30)
    
    # plt.legend(loc='upper right')
      
    '''
    plt.yscale("log")
    plt.ylim([30, 100000])
    '''
    plt.xlim([0, max_graph])
    
    plt.savefig(os.path.join(sys.argv[2], out_name) , format='png', dpi=300)

    plt.close(fig)
"""
