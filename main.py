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
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


# Methods that coarses the graph.
def coarse_graph(graph, similarity, max_levels, method_option, reduction_factor):
    #### Coarsening ####
    while not graph['level'] == max_levels:
        # The common neighbors measure is used to contract the network.
        graph['similarity'] = getattr(Similarity(graph, graph['adjlist']), similarity)
        matching = sharedmem.full(graph.vcount(), range(graph.vcount()), dtype='int')
        processes = []
        # Sets the method that will be used for creating the matching.
        method = None
        if(method_option == 0):
            method = graph.greed_two_hops
        elif(method_option == 1):
            method = graph.greed_rand_two_hops
        for layer in options.layers:
            start = sum(graph['vertices'][0:layer])
            end = sum(graph['vertices'][0:layer + 1])
            processes.append(Process(target = method, args = (range(start, end), reduction_factor[layer], matching)))
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        # Coarsening the graph.
        coarser = graph.coarsening(matching)
        graph = coarser
    return graph

if __name__ == "__main__":
    # Parse options command line
    parser = argparse.ArgumentParser()
    usage = 'usage: python %prog [options] args ...'
    parser.add_argument('-f', '--filename', action='store', dest='filename', help='[Bipartite Graph]', type=str)
    parser.add_argument('-o', '--output', action='store', dest='output', help='[Output]', type=str)
    parser.add_argument('-r', '--rf', action='store', dest='reduction_factor', type=float, nargs='+', help='[Reduction factor for each layer (default: None)]')
    parser.add_argument('-m', '--ml', action="store", dest='max_levels', type=int, default=1, help='[Max levels (default: 1)]')
    parser.add_argument('-c', '--contract', action="store", dest='contract', type=int, default=0, help='[Coarsening method (default: 0) (0 - greed, 1 - random greed)]')
    parser.add_argument('-cm', '--contractmethod', action="store", dest='contractmethod', type=int, default=0, help='[Similarity method for coarsening (default: 0)]')
    parser.add_argument('-s', '--similarity', action="store", dest='similarity', type=int, default=0, help='[Similarity method (default: 0)]')
    parser.add_argument('-i', '--ms', action="store", dest='min_size', type=float, default=3, help='[Minimum size of the communities (default: 3)]')
    parser.add_argument('-t', '--threshold', action="store", dest='threshold', type=float, default=0.5, help='[Cutting the dendrogram at threshold (default: 0.5)]')
    parser.add_argument('-ls', '--layers', action="store", dest='layers', type=str, help='<Required> Set flag', default=None)

    options = parser.parse_args()
    # Open a output file.
    file = options.output
    output_file = open(file, 'w')
    from_auc = 1
    to_auc = 2
    step_auc = 1
    from_pr = 1
    to_pr = 2
    step_pr = 1
    # from_auc = 100
    # to_auc = 10000
    # step_auc = 200
    # from_pr = 100
    # to_pr = 10000
    # step_pr = 200

    # Open the output file and writes the headers.
    for par in range(from_pr, to_pr, step_pr):
        output_file.write("%s," % ("pr" + str(par)))
    for par in range(from_auc, to_auc, step_auc):
        output_file.write("%s," % ("AUC" + str(par)))

    output_file.write("%s\n" % ("time"))

    # Read and pre-process
    if options.filename is None:
        parser.error("required -f [filename] arg.")
    else:
        # Loads the bipartite graph
        graph = load_bipartite(options.filename)

    if options.reduction_factor is None:
        # Sets the reduction factor parameter.
        options.reduction_factor = [0.5] * len(graph["vertices"])

    if len(graph["vertices"]) != len(options.reduction_factor):
        parser.error("Sizes of input arguments -n and -r do not match.")

    if options.output is None:
        filename, extension = os.path.splitext(os.path.basename(options.filename))
        if not os.path.exists('output'): os.makedirs('output')
        options.output = 'output/' + filename + '.csv'

    if options.layers is None:
        # Sets the layers that will be coarsened.
        layers = []
        options.layers = graph['layers']
        for layer in range(options.layers):
            layers.append(layer)
        options.layers = layers
    else:
        layers = []
        for layer in options.layers:
            layers.append(int(layer))
        options.layers = layers

    # The similarity functions that will be used for coarserning the graph.
    contract = ['common_neighbors']
    # The similarity functions that will be used for link prediction.
    similarity = ['common_neighbors']

    # k-fold cross validation parameter.
    k = 10

    n_edges = graph.ecount()
    size = graph.ecount() / k
    sets = [graph.get_edgelist()[x: x + size] for x in range(0, len(graph.get_edgelist()), size)]

    for i in range(k):
        # Creates a safe copy of the graph.
        graph_copy = graph.copy()
        # Selects the current probe set.
        probe_set = sets[i]
        # Delete the edges of graph.
        graph_copy.delete_edges(probe_set)
        graph_copy['adjlist'] = map(set, graph_copy.get_adjlist())

        # Starts the time counter.
        start_time = time.time()

        # Put the weights in a dictionary structure for fast access.
        edges = {}
        for edge in graph_copy.es:
            edges[(edge.source, edge.target)] = edge["weight"]

        vertices_type_1 = []
        vertices_type_2 = []
        # Separates the vertices by the types.
        for i in graph_copy.vs:
            if(i["type"] == 0):
                vertices_type_1.append(i.index)
            else:
                vertices_type_2.append(i.index)

        # Coarsening of the graph.
        graph_copy = coarse_graph(graph_copy, contract[options.contractmethod], options.max_levels, options.contract, options.reduction_factor)

        # Put the weights in a dictionary structure for fast access.
        super_edges = {}
        for edge in graph_copy.es:
            super_edges[(edge.source, edge.target)] = edge["weight"]

        # Local Search (Link prediction)
        Sim = Similarity(graph_copy, graph_copy['adjlist'])
        super_ranking = collaborative_filtering_weighted_sum(Sim, similarity[options.similarity])
        # Creates the real ranking os predictions.
        i = 0
        while(graph_copy.vs["type"][i] != 1):
            i += 1
        change = i
        i = 0
        ranking = {}
        while(i < change):
                j = change
                while(j < graph_copy.vcount()):
                    weight = -1
                    # Tests if the edge between the supervertices is a super edge.
                    if (i,j) in super_edges:
                        weight = super_edges[(i, j)]
                    # Tests if the edge between the supervertices is in the predicted ranking.
                    else:
                        weight = super_ranking[(i,j)]
                    # Adjust the edges weights.
                    n_edges = len(graph_copy['predecessors'][i]) * len(graph_copy['predecessors'][j])
                    # For each vertex in the supervertices, a edge is created.
                    for vertex_1 in graph_copy['predecessors'][i]:
                        for vertex_2 in graph_copy['predecessors'][j]:
                            # Tests if the edge already exists.
                            if not (vertex_1, vertex_2) in edges:
                                # The total weight is normalized by the number of edges.
                                ranking[(vertex_1, vertex_2)] = (weight / n_edges)
                    j += 1
                i += 1
        # Finishes the counter and print the result.
        elapsed_time = time.time() - start_time
        # Sorts the ranking for extracting the precision values.
        ranking_keys = sorted(ranking.items(), key = operator.itemgetter(1))
        # Calculates and prints the precisions in the file.
        for par in range(from_pr, to_pr, step_pr):
            # Calculates the precision value for the parameters.
            pr = precision(probe_set, ranking_keys, par)
            output_file.write("%f," % (pr))

        # Put the probe values in a dict for fast access.
        probes = {}
        for probe in probe_set:
            probes[probe] = ranking[probe]
            # Removes the probes from the ranking.
            del ranking[probe]

        # Calculates and prints the precisions in the file.
        for par in range(from_auc, to_auc, step_auc):
            # Calculates the AUC value for the parameters.
            auc = AUC(probes, ranking, par)
            output_file.write("%f," % (auc))

        # #Re-adds the deleted probe values to the ranking.
        # for probe in probe_set:
        #     ranking[probe] = probes[probe]
        # Prints the elapsed time in the file.
        output_file.write("%f\n" % (elapsed_time))

    output_file.close()
