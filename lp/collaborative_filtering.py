#!/usr/bin/env python
# -*- coding: utf-8 -*-
import igraph

from measures.similarity import *
import numpy as np


# Method for collaborative filtering. Passes the similarity object, a string that represents the index's
# name. A ranking is built for the all the candidates.
# The aggregate function is the second one in the Adomavicious paper.
def collaborative_filtering_weighted_sum(similarity, index):
    index = getattr(similarity, index)
    graph = similarity.graph
    vertices_type_1 = []
    vertices_type_2 = []
    # Separates the vertices by the type.
    for i in graph.vs:
        if(i["type"] == 0):
            vertices_type_1.append(i.index)
        else:
            vertices_type_2.append(i.index)
    # Calculates the similarities between all the type 1 vertices and puts in a dictionary structure for fast access.
    similarities = {}
    for i in range(len(vertices_type_1)):
        j = i
        while(j < len(vertices_type_1)):
            if(i != j):
                similarity = index(i, j)
                similarities[(i, j)] = similarity
                similarities[(j, i)] = similarity
            j += 1
    # Put the weights in a dictionary structure for fast access.
    edges = {}
    for edge in graph.es:
        edges[(edge.source, edge.target)] = edge["weight"]
    # Calculates the candidates for all the type 1 vertices.
    candidates = {}
    for i in vertices_type_1:
        candidates[i] = []
        # Calculates the score for every item and put in the ranking.
        for j in vertices_type_2:
            if(not ((i,j) in edges or (j,i) in edges)):
                candidates[i].append(j)
    ranking = {}
    # Calculates the ranking for collaborative filtering.
    for i in vertices_type_1:
        for j in candidates[i]:
            sum = 0
            similarities_sum = 0
            for k in graph['adjlist'][j]:
                sum += (similarities[(i, k)] * (edges[(k, j)]))
                similarities_sum = similarities_sum + similarities[(i, k)]
            candidate = (i, j)
            # Calculates the kappa value for this candidate.
            kappa = 0
            if(similarities_sum != 0):
                kappa = (1 / similarities_sum)
            value = kappa * sum
            # Add the value and the candidate to the ranking.
            ranking[candidate] = value
    return ranking
