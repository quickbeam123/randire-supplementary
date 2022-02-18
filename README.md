# Supplementary materials to reproduce experiments in a paper on randomized Vampire

1) The used version of Vampire can be found at
vampire branch: https://github.com/vprover/vampire/tree/randire
commit: https://github.com/vprover/vampire/commit/444ac02184984e6b3bdacd13a4d727d14ec10243

2) To compile Vampire run
make vampire_rel
to produce
vampire_rel_randire_6024

3) We used TPTP version 7.5.0
the attached file problemsSTD.txt lists the used first-order problems

4) To obtain a randomized performance profile as in Experiment 1
the attached python 2 script genericVariance.py (which internally calls attached bash script run_shuffling_vampire_generic.sh)
can be used as in:

./genericVariance.py ./vampire_rel_randire_6024 50000 "tptp" "problemsSTD.txt" "-sa discount -awr 10" "-si on -rawr on -rtra on" "tptp_db(dis10)"

Note that
- "-awr 10" is in Vampire the same as "-awr 1:10"
- the perf tool must be installed and perfing enabled by the admin:
  sudo sysctl -w kernel.perf_event_paranoid=-1
- the target folder "tptp_db(dis10)" must already exists

5) Plots as in Fig 1 and 2 are produced by the attached python 3 script histogramsForAll.py as in

./histogramsForAll.py tptp_db\(dis10\)

The script also print out some additional info that we report on in the paper.

6) The scatter plots such in Fig 3 were produced by the attached python 3 script compareTwo.py as in:

./compareTwo.py 'tptp_db(dis10)' 'tptp_db(dis10-av)' problemsSTD_50Gi_rel_randire_6024_discount10*.pkl
./compareTwo.py 'tptp_db(dis10)' 'tptp_db(dis10+bce)' problemsSTD_50Gi_rel_randire_6024_discount10_bce-on.pkl

The respective third arguments are not compulsory. They serve to distinguish the problems on which the technique was applied (blue) from others (red).
These files were obtained from independent vampire runs and are supplied in this repo.

Actually, before running compareTwo.py, we added 

./tptpVarianceCompensate.py 'tptp_db(dis10)' 'tptp_db(dis10+bce)'
./tptpVarianceCompensate.py 'tptp_db(dis10+bce)' 'tptp_db(dis10)'
etc

which match up the number of independently seeded runs in one performance profile vs in the other. 
(Otherwise too many ``unlikely to get solved problems'' / ``technique was not applied dots'' may end up too far from the main diagonal by coincidence, which is confusing.
Note that adding more data to a profile should always only make it more precise!)

7) Data for the AWR histograms in Fig 4 was collected using the attached python 2 script logarithmicAWR.py to be called as in

./logarithmicAWR.py Problems/PRO/PRO017+2.p _shuffleAll "-si on -rawr on -rtra on" 
./logarithmicAWR.py Problems/PRO/PRO017+2.p _shuffleAll-slsq "-si on -rawr on -rtra on -slsq on" 

8) The histograms themselves were obtained using the attached python 3 script plot_AWRgraph.py to be called as in

./plot_AWRgraph.py PRO017+2_shuffleAll.pkl

