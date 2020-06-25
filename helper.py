import networkx as nx

# Given an array of size n (considered as the volumes 
# of ranges of size one, in the correct order),
# computes the volumes of all the ranges
# output size: n(n+1)/2
def range_computer(arr, with_noise = False):
    n = len(arr)

    output = []
    sum = 0
    for i in range(n):
        sum = arr[i]
        output.append(sum)
        if with_noise:
            output.append(sum-1)
            output.append(sum+1)
        for j in range(1,n-i):
            sum += arr[i+j]
            output.append(sum)
            if with_noise:
                output.append(sum-1)
                output.append(sum+1)
    output.sort()

    return output


def create_graph(vols):
    G = nx.Graph()
    G.add_nodes_from(vols)
    vols.sort()

    for i in vols:
        temp_vols = vols[:]
        temp_vols.remove(i)
        for j in temp_vols:
            temp_vols2 = temp_vols[:]
            temp_vols2.remove(j)
            if abs(j-i) in temp_vols2:
                G.add_edge(i, j)
    return G


# Given the volumes and noise budget first create a assymetric window around 
# each volume and call it guess. Guess is all the initial volumes + the 
# assymetric around it. Then using the guess add an edge from i to j if their 
# difference belongs to guess. Return the noisy graph constructed and the noisy
# volumes
def create_graph_noisy(vols, noise_budget=0):
    G = nx.Graph()
    G.add_nodes_from(vols)
    vols.sort()
    guess = []
    # Add the noisy values:
    for i in vols:
        window_down = int( i * (1 - (0.1* noise_budget)))
        window_up = int( i * (1 + (0.9*noise_budget)))
        for j in range(window_down, window_up):
            guess.append(j)
            
    for i in vols:
        temp_vols = vols[:]
        for j in temp_vols:
            if abs(j-i) in guess:
                G.add_edge(i, j, weight=4.7)
    return G, guess


# given an array (e.g. of primitive ranges [1-1], [1-2], [1-3]...) return 
# the differences between pairs of neighbours and as as result of that the 
# returned list is in the form of [1-1], [2-2], [3,3], ... 
def get_unary_ranges(arr):
    arr.sort()
    ranges = [arr[0]]
    for i, j in zip(arr[:-1], arr[1:]):
        ranges.append(j-i)
    return ranges


# The first returned result is the volumes in the sorted way and the second
# returned result is the actual database
def nodes_to_vols(nodes, volumes=[]):
    vols = nodes
    vols = sorted(vols)

    single_vols = []
    prev = 0
    for next in vols:
        single_vols.append(next-prev)
        prev = next

    return vols, single_vols
