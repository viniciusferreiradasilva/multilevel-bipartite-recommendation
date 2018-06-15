#!/usr/bin/env python
# -*- coding: utf-8 -*-
import igraph

from measures.similarity import *
from measures.statistic import *
import numpy as np

# Method for link prediction. Passes the similarity object, a string that represents the index's
# name and the node that will receive the prediction. The most likely vertex has it's ID returned.
def predict_most_likely(similarity, index, node):
    graph = similarity.graph
    types = graph.vs["type"]
    index = getattr(similarity, index)
    nodes = range(graph.vcount())
    nodes.remove(node)
    # Get the candidates for link prediction.
    candidates = [x for x in nodes if x not in graph.neighbors(node)]
    greatest_value = 0
    most_likely = -1
    # Verifies for every candidate vertex which one that has the greates value for the index.
    for vertex in candidates:
        value = index(node, vertex)
        if(value > greatest_value):
            greatest_value = value
            most_likely = vertex
    print "Vertex:",most_likely, "Value:", greatest_value
    return most_likely

# Method for link prediction. Passes the similarity object, a string that represents the index's
# name and the node that will receive the prediction. A ranking is built for the candidate vertices
# for a node.
def predict_ranking_for_node(similarity, index, node):
    graph = similarity.graph
    types = graph.vs["type"]
    index = getattr(similarity, index)
    nodes = range(graph.vcount())
    nodes.remove(node)
    # Get the candidates for link prediction.
    candidates = [x for x in nodes if x not in graph.neighbors(node)]
    # Ranking of predictions.
    ranking = []
    # Verifies for every candidate vertex which one that has the greates value for the index.
    for vertex in candidates:
        if(types[vertex] != types[node]):
            value = index(node, vertex)
            if(not ranking):
                ranking.append((value, vertex))
            else:
                added = False
                i = 0
                while(not added):
                    if (i >= len(ranking) or ranking[i][1] < value):
                        ranking.insert(i, (value, vertex))
                        added = True
                    else:
                        i = i + 1
    return ranking

# Method for link prediction. Passes the similarity object, a string that represents the index's
# name and the node that will receive the prediction. A ranking is built for the candidate edges.
def predict_ranking(similarity, index):
    graph = similarity.graph
    index = getattr(similarity, index)
    types = similarity.graph.vs["type"]
    # Create the list of candidates edges.
    candidates = []
    # Ranking of predictions.
    ranking = []
    for i in range(graph.vcount()):
        j = i
        while j < graph.vcount():
            if(j != i and (not ((i,j) in graph.get_edgelist())) and (not ((j,i) in graph.get_edgelist()))):
                candidates.append((i, j))
            j += 1
    # Builds the list os candidate edges.
    for candidate in candidates:
        from_vertex = candidate[0]
        to_vertex = candidate[1]
        # Tests if the vertices are from different groups.
        if(types[from_vertex] != types[to_vertex]):
            # Calculates the score for the candidate edge.
            value = index(from_vertex, to_vertex)
            if(not ranking):
                ranking.append((value, candidate))
            else:
                added = False
                i = 0
                while(not added):
                    if (i >= len(ranking) or ranking[i][0] < value):
                        added = True
                        # Inserts the value in the rigth position.
                        ranking.insert(i, (value, candidate))
                    else:
                        i = i + 1
    return ranking
