#!/usr/bin/env python
# -*- coding: utf-8 -*-
import igraph

from optparse import OptionParser
from pandas import DataFrame

from pmhgraph.pmh import PMHGraph
from measures.similarity import *
import numpy as np
import random
import operator


# Calculates the precision of a link predictor. Needs a probe_set which corresponds to a
# set of removed edges from the graph, the ranking of a link predictor and a size L.
def precision(probe_set, ranking_keys, L = 1000):
    hits = 0.0
    for i in range(L):
        if(ranking_keys[i][0] in probe_set):
            hits += 1.0
    return (hits / L)

# Calculates the AUC of a link predictor. Needs a probe_set which corresponds to a
# set of removed edges from the graph and the ranking of a link predictor.
def AUC(probe_set, ranking, comparisons = 1000):
    n_line = 0
    n_lines = 0
    probes_keys = probe_set.keys()[:]
    ranking_keys = ranking.keys()[:]
    # Shuffles the lists for random selection.
    random.shuffle(probes_keys)
    random.shuffle(ranking_keys)
    for i in range(comparisons):
        probe_value = probe_set[probes_keys[i]]
        ranking_value = ranking[ranking_keys[i]]
        if(probe_value > ranking_value):
            n_line += 1
        elif(probe_value == ranking_value):
            n_lines += 1
    return ((n_line + 0.5 * n_lines) / comparisons)
