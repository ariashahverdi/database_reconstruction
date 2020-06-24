import networkx as nx

# Given an array of size n, computes the volumes of all the ranges
# output sizeL n(n-1)/2 + n
def range_computer(arr, with_noise = False):
    n = len(arr)
    # print('input length:', n)

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

    # print('ouput length:', len(output))
    return output


def create_graph(vols):
    G = nx.Graph()
    G.add_nodes_from(vols)
    vols.sort()
    #print(vols)
    for i in vols:
        temp_vols = vols[:]
        temp_vols.remove(i)
        for j in temp_vols:
            temp_vols2 = temp_vols[:]
            temp_vols2.remove(j)
            if abs(j-i) in temp_vols2:
                G.add_edge(i, j, weight=4.7)
    return G


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
            
    #print(vols)
    for i in vols:
        temp_vols = vols[:]
        #temp_vols.remove(i)
        for j in temp_vols:
            temp_vols2 = temp_vols[:]
            #temp_vols2.remove(j)
            if abs(j-i) in guess:
                G.add_edge(i, j, weight=4.7)
    return G, guess


# given an array (usually of primitive ranges [1-1], [1-2], [1-3]...) return the differences between pairs of neighbours
def get_unary_ranges(arr):
    arr.sort()
    ranges = [arr[0]]
    for i, j in zip(arr[:-1], arr[1:]):
        ranges.append(j-i)
    return ranges


volumes = []
# The first returned result is the volumes in the sorted way and the second
# returned result in the actual database
def nodes_to_vols(nodes, volumes=volumes):
    vols = nodes
    vols = sorted(vols)

    single_vols = []
    prev = 0
    for next in vols:
        single_vols.append(next-prev)
        prev = next

    return vols, single_vols