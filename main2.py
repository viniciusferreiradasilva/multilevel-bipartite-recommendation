#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import sharedmem
import igraph
import argparse

from itertools import izip, product
from multiprocessing import Process, Manager, Pool, Pipe
from optparse import OptionParser

from pmhgraph.pmh import PMHGraph
from measures.similarity import *
from input_graph.load import load_bipartite
from lp.collaborative_filtering import *
from lp.metrics import *
import numpy as np

import subprocess
from subprocess import Popen, PIPE, STDOUT

# Loads the bipartite graph
graph = load_bipartite("data/ratings_100000.csv")
print "Graph loaded..."
# Local Search (Link prediction)
Sim = Similarity(graph, graph['adjlist'])
super_ranking = collaborative_filtering_weighted_sum(Sim, "common_neighbors")
print "Links predicted..."
