#!/usr/bin/env python3

import sys, os

import subprocess, time, signal

import pickle
import gzip
import math, random
from collections import defaultdict

import numpy as np

import matplotlib.pyplot as plt

from matplotlib import colors

plt.rcParams['text.usetex'] = True

from scipy.interpolate import interp1d

from scipy.stats import norm

if __name__ == "__main__":
  # To run as: ./plot_AWRgraph.py PRO017+2_shuffleAll.pkl
  
  with open(sys.argv[1],'rb') as f:
    results = pickle.load(f,encoding='utf-8')

  # for every prooflen, Xs and Ys to plot (in the same color)
  # by_prooflen = defaultdict(lambda : ([],[]))

  buckets = defaultdict(list)
  
  Xs = []
  Ys = []

  for (age,wei,seed),(success, iterations, instructions, prooflen) in results:
    if success == False or success == "---":
      print (float(age)/float(wei),seed,success)
      continue
      
    instructions = math.log(instructions*1000000,10)
    
    buckets[(age,wei)].append(instructions)
    
    x = math.log(float(age)/float(wei),2)
    y = instructions
    
    '''
    (Xs,Ys) = by_prooflen[prooflen]
    
    Xs.append(x)
    Ys.append(y)
    
    by_prooflen[prooflen] = (Xs,Ys)
    '''
    
    Xs.append(x)
    Ys.append(y)
    # Ys.append(math.log(y))
    
    # print prooflen, x,y, Xs,Ys
  
  fig, ax1 = plt.subplots(figsize=(3, 2.5))
  
  # alternatives? https://stackoverflow.com/questions/2369492/generate-a-heatmap-in-matplotlib-using-a-scatter-data-set
  
  # plt.hexbin(Xs,Ys,yscale="log",extent=(-10, 2, 1.7, 5),bins='log',gridsize=(80,40),linewidths=0.1)
  plt.hexbin(Xs,Ys,extent=(-10, 2, 7.5, 11),bins='log',gridsize=(80,40),linewidths=0.1)
  # plt.hist2d(Xs,Ys,bins = 100,cmap = "RdYlGn_r",norm = colors.LogNorm())
  
  # plt.xlim([-10, 2])
 
  '''
  plt.xticks(np.arange(-10, 2.1, step=2.0))
  plt.xlim([-10, 2.0])
              
  plt.savefig(sys.argv[1]+".hex.png", format='png', dpi=300)

  exit(0)
  '''

  
  '''
  fig, ax1 = plt.subplots(figsize=(3, 2.5))

  color = 'tab:red'
  ax1.set_xlabel('awr')
  # ax1.set_ylabel('0.0-1.0 axis', color=color)
  # for (Xs,Ys) in by_prooflen.values():

  ax1.scatter(Xs, Ys, alpha = 0.1, s = 5,edgecolor="none")
  # ax1.tick_params(axis='y', labelcolor=color)
  '''
  
  XYZs = []

  for (age,wei),iter_list in buckets.items():
    x = math.log(float(age)/float(wei),2)
    y = np.mean(iter_list)
    z = np.std(iter_list)
    
    XYZs.append((x,y,z))

  XYZs.sort()
  
  Xs = np.array([x for (x,y,z) in XYZs])
  Ys = np.array([y for (x,y,z) in XYZs])
  Zs = np.array([z for (x,y,z) in XYZs])

  ax1.plot(Xs, Ys, "-", label = "average", zorder=3, color = "deeppink", linewidth = 1.0)
  # ax1.fill_between(Xs, Ys-Zs, Ys+Zs, zorder=2, facecolor="blue", alpha=0.5)
  
  '''
  ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

  color = 'tab:blue'
  
  ax2.set_ylabel('num of iter', color=color)  # we already handled the x-label with ax1
  ax2.plot(SXs, Zs, 'o', color=color)
  ax2.tick_params(axis='y', labelcolor=color)

  bandwidth=0.05
  l = np.linspace(0.0,1.0,1000)
  all_kernels = sum(norm(x,bandwidth).pdf(l) for x in Xs)
  pos_kernels = sum(norm(x,bandwidth).pdf(l) for x in SXs)
  ax1.plot(l, pos_kernels / all_kernels, '-', color="tab:red")
 
  fig.tight_layout()  # otherwise the right y-label is slightly clipped
  '''

  # plt.yscale("log")
  # plt.ylim([30, 100000])
  
  plt.ylim([7.5, 11])
  
  plt.xlim([-10, 2.0])

  plt.xticks(np.arange(-10, 2.1, step=2.0))

  ax1.set_xlabel(r'$\log_2(\mathit{awr})$')
  ax1.set_ylabel(r'$\log_{10}(\mathrm{instructions})$')

  plt.subplots_adjust(bottom=0.2,left=0.2)

  plt.savefig(sys.argv[1]+".png", format='png', dpi=300)

  # plt.show()



