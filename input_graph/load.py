import operator
from collections import defaultdict
from itertools import combinations, izip
from multiprocessing import Manager, Process
from random import choice, randint, sample, shuffle
from pmhgraph.pmh import PMHGraph
import numpy as np
import csv
from igraph import Graph


# Loads the MovieLens rates file and convert as a bipartite graph file.
def load_bipartite(file):
	f = open(file, 'rt')
	# Stores the edges between group 1 and 2.
	dict_edges = {}
	# Stores the group 1 and group 2 vertices IDs.
	group1_ids = {}
	group2_ids = {}
	# Counters that corrects the group 1 and group 2 IDS.
	group1_counter = 0
	group2_counter = 0
	try:
		reader = csv.reader(f)
		# Hides the header from the reader.
		header = f.readline()
		for row in reader:
			from_vertex = int(row[0])
			to_vertex = int(row[1])
			# If the vertex is not yet in the group 1, then add.
			if(not (from_vertex in group1_ids)):
				group1_ids[from_vertex] = group1_counter
				group1_counter = group1_counter + 1
			# If the vertex is not yet in the group 2, then add.
			if(not (to_vertex in group2_ids)):
				group2_ids[to_vertex] = group2_counter
				group2_counter = group2_counter + 1
		# The length of the group 1.
		group1_length = len(group1_ids)
		# The length of the group 2.
		group2_length = len(group2_ids)
		# Vector of vertices.
		vertices = [group1_length, group2_length]
		# Returns to the beginning of the file.
		f.seek(0)
		reader = csv.reader(f)
		# Hides the header from the reader.
		header = f.readline()

		for row in reader:
			from_vertex = group1_ids[int(row[0])]
			to_vertex = (group2_ids[int(row[1])] + group1_length)
			weight = float(row[2])
			# Add the new edge between from_vertex to to_vertex with the weight.
			dict_edges[(from_vertex, to_vertex)] = weight

		edges, weights = izip(*dict_edges.items())
		# Creates the graph.
		graph = PMHGraph((group1_length + group2_length), list(edges))
		# Add the edges weights to the es attr.
		graph.es['weight'] = weights
		# Add the edges weights to the es attr.
		graph.vs['weight'] = 1
		types = []
		for i in range(len(vertices)):
			types += [i] * vertices[i]
		graph.vs['type'] = types
		graph['adjlist'] = map(set, graph.get_adjlist())
		graph['layers'] = len(vertices)
		graph['vertices'] = vertices
		graph['level'] = 0
		graph['predecessors'] = {}
		for i in range(graph.vcount()):
			graph['predecessors'][i] = [i]
		# Not allow direct graphs
		if graph.is_directed(): graph.to_undirected(combine_edges=None)
	finally:
	    f.close()
	return graph
