
import networkx as nx
import numpy as np
import random
import sys
import csv
import pdb
import time

from helper import *
from dbs_and_measurements import *


# number of volumes that must be common to two solutions in order to 
# regard them a 'Match'
INTERSECTION_THRESHOLD = 3

# only cliques of legitimate size are 'expanded', i.e. if a node
# outside of the clique is highly connected to the clique,
# the node will be added to the clique
LEGITIMATE_CLIQUE_SIZE = 8 # subject to change during the execution


VOLUME_LOWER_BOUND = 5
VOLUME_UPPER_BOUND = 100000

NOISE_BUDGET = 0
NEW_VOLS_LIMIT = 4

# number of keys
N = 12

# Lenght of database
db_len = 100000

# volumes
volumes = []
volumes_noisy = []


# Find if two values are approximitely equal
def aprox_equal(val1, val2, noise_budget=0.0):
    if abs(val1-val2) <= min(val1,val2) * noise_budget:
        return True
    return False

# Returns length of the approximate longest common substring of X[0..m-1] and Y[0..n-1]  
def aprox_LCSubStr(X, Y, noise_budget=0.0): 
    m = len(X)
    n = len(Y)
    LCSuff = [[[0,0,0] for k in range(n+1)] for l in range(m+1)] 
    matching_blocks_dict = {}
            
    # Following steps to build LCSuff[m+1][n+1] in bottom up fashion 
    for i in range(m + 1): 
        for j in range(n + 1): 
            if (i == 0 or j == 0): 
                LCSuff[i][j][0] = 0
                LCSuff[i][j][1] = i
                LCSuff[i][j][2] = j
            elif(aprox_equal(X[i-1], Y[j-1], noise_budget)):
                LCSuff[i][j][0] = LCSuff[i-1][j-1][0] + 1
                LCSuff[i][j][1] = LCSuff[i-1][j-1][1]
                LCSuff[i][j][2] = LCSuff[i-1][j-1][2]
                idx1, idx2 = LCSuff[i][j][1], LCSuff[i][j][2]
                if (idx1,idx2) in matching_blocks_dict:
                    matching_blocks_dict[(idx1,idx2)] += 1
                else:
                    matching_blocks_dict[(idx1,idx2)] = 1
            else: 
                LCSuff[i][j][0] = 0
                LCSuff[i][j][1] = i
                LCSuff[i][j][2] = j

    matching_blocks_val = list(matching_blocks_dict)
    matching_blocks = []
    for i in matching_blocks_val:
        idx1 = i[0]
        idx2 = i[1]
        length = matching_blocks_dict[i]
        matching_blocks.append((idx1, idx2, length))
    
    return matching_blocks 

# given two arrays, finds their extended LCSubstring
# note that the notion of 'common subsequence' sis a bit different
def match_sequences(primary, secondary, noise_budget=NOISE_BUDGET):
    print('Primary   : {}'.format(primary))
    print('Secondary : {}'.format(secondary))
    matching_blocks = aprox_LCSubStr(primary, secondary, noise_budget = 2*noise_budget)

    # The following will give us the formast as follows:
    # Each pair give us : ( start in first string, end in first string
    #                       start in second string, end in second string)
    # it is denoted by start1, stop1, start2, stop2
    matching_blocks = [(i, i+n, j, j+n) for i, j, n in matching_blocks]
    print('Matching blocks are : {}'.format(matching_blocks))

    longest_matching_block = (0,0,0,0)
    for block in matching_blocks:
        start1, stop1, start2, stop2 = block
        
        update = True
        while stop1 <= len(primary) and stop2 <= len(secondary) and update:
            update = False
            for i in range(stop2, len(secondary)):
                found_flag = False
                for j in range(1, len(primary)-stop1+1): 
                    if aprox_equal(sum(primary[stop1:stop1+j]), secondary[i], 2*noise_budget):
                        stop1 += j
                        stop2 += 1
                        update = True
                        found_flag = True
                        break
                if not found_flag:
                    break
            for i in range(stop1, len(primary)):
                found_flag = False
                for j in range(1, len(secondary)-stop2+1): 
                    if aprox_equal(sum(secondary[stop2:stop2+j]), primary[i], 2*noise_budget):
                        stop1 += 1
                        stop2 += j
                        update = True
                        found_flag = True
                        break
                if not found_flag:
                    break
        
        update = True
        while start1 >= 0 and stop2 >= 0 and update:
            update = False
            for i in reversed(range(start2)):
                found_flag = False
                for j in range(1, start1+1):  
                    if aprox_equal(sum(primary[start1-j:start1]), secondary[i], 2*noise_budget):
                        start1 -= j
                        start2 -= 1
                        update = True
                        found_flag = True
                        break
                if not found_flag:
                    break

            for i in reversed(range(start1)):
                found_flag = False
                for j in range(1, start2+1):  
                    if aprox_equal(sum(secondary[start2-j:start2]), primary[i], 2*noise_budget):
                        start1 -= 1
                        start2 -= j
                        update = True
                        found_flag = True
                        break
                if not found_flag:
                    break
                        
        if stop1-start1 > longest_matching_block[1]-longest_matching_block[0]:
            print('update longest from {}'.format(block))
            longest_matching_block = (start1, stop1, start2, stop2)

    print('Longest blocks is : {}'.format(longest_matching_block))

    return longest_matching_block

# Find the longest common substring of two lists
# returns their match both aligned similarly, and reversely
# this is to find out if the two given lists (database candidates) 
# match as they are, or are approximate mirrors of each other
def find_lcs(primary, secondary):
    r_secondary = secondary[:]
    r_secondary.reverse()
    match1 = match_sequences(primary, secondary, NOISE_BUDGET)
    match2 = match_sequences(primary, r_secondary, NOISE_BUDGET)
    return (match1, match2)


# given two arrays, looks to find relations of the form arr1[i] == sum(arr2[j:j+k])
# whenever found, arr1[i] will be replaced by the elements arr2[j:j+k].
# note that the inputs to this function are always substrings of cliques
# next to their longest common substring.
# for example [a, b, c, d, e+f, g, h]
#          [k, a, b, c, d, e, f, g]
# then, straighten_out will be called once with ([], [k]),
# and once with ([e+f, g, h], [e, f, g])
def straighten_out(arr1, arr2):
    print('- straighten_out() for', arr1, arr2)
    # base cases of recursion
    if len(arr1) == 0:
        return arr2
    if len(arr2) == 0:
        return arr1
    val1 = arr1[0]
    val2 = arr2[0]

    if aprox_equal(val1, val2, NOISE_BUDGET):
        result = [arr1[0]]
        the_rest = straighten_out(arr1[1:], arr2[1:])
        if not the_rest is None:
            result.extend(straighten_out(arr1[1:], arr2[1:]))
            return result
        else:
            return
    # the case when arr1, arr2 = [a+b], [a]
    if len(arr1) == 1 and len(arr2) == 1:
        if arr1[0] < arr2[0] and arr2[0] - arr1[0] in volumes_noisy: 
            return [arr1[0], arr2[0]-arr1[0]]
        elif arr1[0] < arr2[0] and arr2[0] - arr1[0] not in volumes_noisy:
            print(arr2[0] - arr1[0], ' not in volumes')
        elif arr2[0] < arr1[0] and arr1[0] - arr2[0] in volumes_noisy:
            return [arr2[0], arr1[0]-arr2[0]]
        elif arr2[0] < arr1[0] and arr1[0] - arr2[0] not in volumes_noisy:
            print(arr1[0] - arr2[0], ' not in volumes')
    # general case
    if len(arr2) > 1:
        for i in range(2, len(arr2)+1):
            val1 = arr1[0]
            val2 = sum(arr2[:i])

            if aprox_equal(val1, val2, NOISE_BUDGET):
                slice1 = arr2[:i]
                slice2 = straighten_out(arr1[1:], arr2[i:])
                if not slice2 is None:
                    slice1.extend(slice2)
                    return slice1
                else:
                    return
    if len(arr1) > 1:
        for i in range(2, len(arr1)+1):
            val1 = arr2[0]
            val2 = sum(arr1[:i])

            if aprox_equal(val1, val2, NOISE_BUDGET):
                slice1 = arr1[:i]
                slice2 = straighten_out(arr2[1:], arr1[i:])
                if not slice2 is None:
                    slice1.extend(slice2)
                    return slice1
                else:
                    return
    return

# calls the straighten_out function on reverse of the given arrays
# this is needed to "straighen out" the substring to the left of the LCSubstring
def straighten_out_reverse(arr1, arr2):
    arr1.reverse()
    arr2.reverse()
    result = straighten_out(arr1, arr2)
    if result:
        result.reverse()
    return result

# Modify the LCS such that the LCS always have more volumes, meaning that if
# there exists a volume which can be broken down to smaller volumes using the 
# information in lcs2 we do that
def modify_lcs(lcs1, lcs2):
    print('modify lcs: {}, {}'.format(lcs1, lcs2))

    res = []
    idx1, idx2 = 0, 0
    while idx1 < len(lcs1) and idx2 < len(lcs2):
        if aprox_equal(lcs1[idx1], lcs2[idx2], 2*NOISE_BUDGET):
            res.append(lcs1[idx1])
            idx1 += 1
            idx2 += 1
            
        else:
            i = idx1 + 1
            while i <= len(lcs1):
                if aprox_equal(sum(lcs1[idx1:i]), lcs2[idx2], 2*NOISE_BUDGET):
                    res = res + lcs1[idx1:i]
                    idx1 = i
                    idx2 += 1
                    break
                i += 1
            j = idx2 + 1
            while j <= len(lcs2):
                if aprox_equal(lcs1[idx1], sum(lcs2[idx2:j]), 2*NOISE_BUDGET):
                    res = res + lcs2[idx2:j]
                    idx1 += 1
                    idx2 = j
                    break
                j += 1

    return res


# given two parts of the solution (2 cliques) and their matching (LCS coordinates),
# merge them if it is possible (as dictated by the conditions in straighten_out())
# if not possible, return None
def attempt_merge(base_sol, cand_sol, match):
    print('~ attempt_merge() with', base_sol, cand_sol, match)
    start1, stop1, start2, stop2 = match

    lcs1 = base_sol[start1:stop1]
    lcs2 = cand_sol[start2:stop2]
    
    # Make sure the LCS has all the elementary volumes
    lcs = modify_lcs(lcs1, lcs2)
    print(lcs, start1, stop1, start2, stop2)

    slice1 = straighten_out_reverse(base_sol[:start1], cand_sol[:start2])
    print('--- slice 1', slice1)
    slice2 = lcs
    slice3 = straighten_out(base_sol[stop1:], cand_sol[stop2:])
    print('--- slice 3', slice3)

    if slice1 is None or slice3 is None:
        return
    else:
        base_sol = slice1
        base_sol.extend(slice2)
        base_sol.extend(slice3)
        return base_sol

# Given two parts of the solution (2 cliques) and their matching 
# (LCS coordinates) merge them in whatever orientation is better 
# (direct or reverse) and return the result.
def merge(base_sol, cand_sol):
    print('= merge() for solution', base_sol, cand_sol)
    direct_match, reverse_match = find_lcs(base_sol, cand_sol)
    print('direct match and reverse match are as follows')
    print(direct_match, reverse_match)
    print('* merge {}, {}'.format(base_sol, cand_sol))

    # check if (any) match is of legitimate size
    if (direct_match[1] - direct_match[0] > INTERSECTION_THRESHOLD or reverse_match[1] - reverse_match[0] > INTERSECTION_THRESHOLD):
        # check which way it makes more sense to merge
        if direct_match[1] - direct_match[0] > reverse_match[1] - reverse_match[0]:
            print('direct wins')
            res = attempt_merge(base_sol, cand_sol, direct_match)
            if res is None:
                print('+ merge cancelled')
            else:
                base_sol = res
                print('+ b:', base_sol)
        elif direct_match[1] - direct_match[0] < reverse_match[1] - reverse_match[0]:
            print('reverse wins')
            cand_sol.reverse()
            res = attempt_merge(base_sol, cand_sol, reverse_match)
            if res is None:
                print('+ merge cancelled')
            else:
                base_sol = res
                print('+ b:', base_sol)
        else: #  direct_match[1] - direct_match[0] == reverse_match[1] - reverse_match[0]:
            # if there is a tie, check both matches to see if a merge is possible.
            res = attempt_merge(base_sol, cand_sol, direct_match)
            if res is None:
                cand_sol.reverse()
                res = attempt_merge(base_sol, cand_sol, reverse_match)
                if res is None:
                    print('+ merge cancelled')
                else:
                    base_sol = res
                    print('+ b:', base_sol)

        return base_sol
    else:
        print ('No long common sublist found')
        return base_sol

# Add volume to the graph, as a node and as (possibly) edges
def add_volume(G, vol):
    if vol > 0 and vol not in volumes_noisy:
        print('- adding volume:', vol)
        # add the node
        G.add_node(vol)
        volumes.append(vol)
        # add edges to the new node
        for n in G.nodes:
            if n != vol and not G.has_edge(n, vol):
                if abs(n - vol) in volumes_noisy:
                    G.add_edge(n, vol)

        # Add edges corresponding to the new volume
        for e in nx.non_edges(G):
            if aprox_equal(abs(e[1] - e[0]), vol, NOISE_BUDGET):
                G.add_edge(e[1], e[0])

        # Add the noisy values:
        window_down = int( vol * (1 - (0.1* NOISE_BUDGET)))
        window_up = int( vol * (1 + (0.9*NOISE_BUDGET)))
        for j in range(window_down, window_up):
            volumes_noisy.append(j)

    return G


def match_extend(mode, H):
    print('-- Run Match & Extend --')
    
    # Get the list of all the cliques in the graph
    # The order returned by enumerate_all_cliques is from the smallest clique to 
    # largest one, so we reverse the order
    all_cliques = list(nx.enumerate_all_cliques(H))[::-1]
    k = len(all_cliques[0])
    print('Graph clique number before running Match & Extend:', k)

    base_solutions = []
    for cliq in all_cliques:
        if len(cliq) == k:
            # Construct the database from the cliques that have maximal size
            #  and save them as the initial base_solutions
            base_solutions.append(get_unary_ranges(cliq))
        else: 
            break

    # If the size of the Clique is equal to N we found the maximum clique and we
    # are done
    if k == N:
        print('no need to run Match & Extend, abort.')
        return H, base_solutions[0], []

    # Print all the possible base_solutions
    print('cliq number:', k, '\nnumber of such cliques:', len(base_solutions))
    for b in base_solutions:
        print(b)
    
    # If we want to see the performance of only the noisy clique finding,
    # just return the first result in base_solutions and don't continue with 
    # Match & Extend
    if mode == 'clique':
        return H, base_solutions[0], []

    # Running Match & Extend starting with the first biggest clique
    base_sol = base_solutions[0]
    print('######## Starting with base solution:', base_sol, '########')
    steps_data = []
    step = 0

    # Until a solution of length N is reached, find a clique that is
    # compatible enough with the base solution, and merge them
    # add the new resulting volumes
    while True:
        # We store the clique number k and the number of cliques of size k at 
        # each step of the algorithm
        #pdb.set_trace()
        cliques_info = {}
        for j in [k, k-1, k-2, k-3, k-4]:
            cliques_info[j] = len([c for c in all_cliques if len(c) == j])
        steps_data.append((len(base_sol), cliques_info))

        found = False
        print('. Step {} begin. clique number:'.format(step), k)

        # if the maximal clique size gets larger, we also increase the minimal 
        # clique size to be considered accurate
        global LEGITIMATE_CLIQUE_SIZE
        LEGITIMATE_CLIQUE_SIZE = k-5
        
        cliques = [cliq for cliq in all_cliques if len(cliq) > LEGITIMATE_CLIQUE_SIZE]

        if k >= N:
            base_sol = get_unary_ranges(cliques[0])
            print('## done ##')
            break

        # In the following preprocessing step, we iterate over all cliques to find 
        # the ones that would cause the least amount of new volumes added to our graph
        least_disruptive_cliques = {}
        for cliq in cliques:
            # Check the result of Merge for all the cliques of legitimate size
            cand_sol = get_unary_ranges(cliq)
            temp = merge(base_sol, cand_sol)

            # if base_sol is not a subsolution of temp
            # and if all the resulting volumes are within allowed bounds
            # (dictated by VOLUME_UPPER_BOUND)
            if len(temp) > len(base_sol):
                if all([range <= VOLUME_UPPER_BOUND for range in range_computer(temp)]):
                    n_new_vols = 0
                    # Check howw many new volumes the cand_sol will add and save
                    # that into a dictionary
                    for r in range_computer(temp):
                        if r > 0 and r not in volumes_noisy:
                            n_new_vols += 1
                    if n_new_vols in least_disruptive_cliques:
                        least_disruptive_cliques[n_new_vols].append(cliq)
                    else:
                        least_disruptive_cliques[n_new_vols] = [cliq]

        if len(least_disruptive_cliques) == 0:
            break
        d = sorted(least_disruptive_cliques.keys())[0]

        if d <= NEW_VOLS_LIMIT:
            # Get the clique which adds the least amount of volumes to the graph
            cliq = least_disruptive_cliques[d][0]
            cand_sol = get_unary_ranges(cliq)
            temp = merge(base_sol, cand_sol)

            # find the volumes that the resulting solution will produce and add 
            # them to the volumes list and add the corresponding nodes and edges 
            # to the graph.
            found = True
            print('+ b:', temp)
            for r in range_computer(temp):
                H = add_volume(H, r)
            base_sol = temp

        print('. Step {} end. clique number:'.format(step), k)
        step += 1

        # if we could not add more nodes in this run, or if clique of size N is found
        if not found: 
            break
        
        # We found the correct number of elements for our database, we are done
        if len(base_sol) >= N:
            cliques_info = {}
            for j in [k, k-1, k-2, k-3, k-4]:
                cliques_info[j] = len([c for c in all_cliques if len(c) == j])
            steps_data.append((len(base_sol), cliques_info))
            break

    print('Graph clique number after Match & Extend:', k)

    return H, base_sol, steps_data


# run the algorithm on all experiments and print out a report
def general_test(mode, noise_budget_val, drop_num_val, seed_val):
    
    experiments1 = ['nis2008_1', 'nis2008_2', 'nis2008_3', 'nis2008_4', 'nis2008_5', 'nis2008_6', 'nis2008_7', 'nis2008_8', 'nis2008_9', 'nis2008_10']

    experiments2 = ['nis2008_16_non_uniform_q','nis2008_19_non_uniform_q']

    #experiments2 = ['nis2008_17_non_uniform_q','nis2008_18_non_uniform_q', 'nis2008_19_non_uniform_q','nis2008_20_non_uniform_q', 'nis2008_21_non_uniform_q', 'nis2008_22_non_uniform_q', 'nis2008_23_non_uniform_q', 'nis2008_24_non_uniform_q', 'nis2008_25_non_uniform_q']#, 'nis2008_7_non_uniform_q', 'nis2008_8_non_uniform_q', 'nis2008_9_non_uniform_q', 'nis2008_10_non_uniform_q']

    experiments3 = ['nis2008_1_gauss' , 'nis2008_2_gauss', 'nis2008_3_gauss', 'nis2008_4_gauss', 'nis2008_5_gauss', 'nis2008_6_gauss', 'nis2008_7_gauss', 'nis2008_8_gauss', 'nis2008_9_gauss', 'nis2008_10_gauss']

    experiments4 = ['nis2008_4_m2']#, 'nis2008_7_m1', 'nis2008_8_m1']#, 'nis2008_4_m1', 'nis2008_5_m1']#, 'nis2008_6', 'nis2008_7', 'nis2008_8', 'nis2008_9', 'nis2008_10']

    experiments5 = ['nis2008_4_m2']#, 'nis2008_7_m2', 'nis2008_8_m2']#, 'nis2008_5_m2']#, 'nis2008_4_m2', 'nis2008_5_m2']#, 'nis2008_6', 'nis2008_7', 'nis2008_8', 'nis2008_9', 'nis2008_10']

    experiments = experiments2#experiments1 + experiments2 + experiments3

    global NOISE_BUDGET
    NOISE_BUDGET = noise_budget_val

    dbs = []
    guesses = []
    graphs_final = []
    runtimes = []
    dropped_vols = []
    execution_data = {}

    for ex_name in experiments:
        # Get the original database and volumes from running cache attack
        global db
        db = eval('db_'+ ex_name)
        vols = eval(ex_name + '_vols')

        # Experiments for dropping some random volumes
        # If drop_num_val is set to 0 this part has no effect
        drop_num = drop_num_val 
        random.seed(seed_val)
        true_range_vols = range_computer(db)
        # We just drop values greater than maximum /4 so not to drop elementary
        # volumes
        drop_candidates = [v for v in true_range_vols if v > max(true_range_vols)/4]
        random.shuffle(drop_candidates)
        dropped = []
        for i in range(drop_num):
            true_vol_dropped = drop_candidates.pop()
            vols.sort(key=lambda x: abs(x-true_vol_dropped))
            drp = vols[0]
            vols.remove(drp)
            dropped.append(drp)
            temp_vols = vols[:]
            for j in temp_vols:
                if abs(j-true_vol_dropped) < (NOISE_BUDGET * true_vol_dropped):
                    vols.remove(j)
                    dropped.append(j)
        vols.sort()
        dropped_vols.append(dropped)

        # In our Experiments N = 12
        global N
        N = len(db)

        start = time.time()

        # Create the noisy graph and the noisy volumes
        # Noisy volumes = volumes obtained from cache measurement + the window 
        # around them
        global volumes_noisy
        H, volumes_noisy = create_graph_noisy(vols, NOISE_BUDGET)

        # Run the Match & Extend Algorithm
        H, base_sol, exec_data = match_extend(mode, H)

        execution_data[ex_name] = exec_data

        graphs_final.append(H)
        dbs.append(db)
        guesses.append(base_sol)

        end = time.time()
        runtimes.append(end-start)

    # Print the report
    f_name = "report_{}.txt".format(drop_num)
    f = open(f_name, "a+")
    f_name2 = "excel_{}.txt".format(drop_num)
    f2 = open(f_name2, "a+")
    f2.write('\n')
    template = "{0:25}{1:80}{2:10}" # column widths: 8, 80, 10
    template2 = "{0:80}{1:5}{2:80}{3:5}" # column widths: 8, 80, 10
    f.write('-------- Report --------\n')
    f.write(template.format("Exp Name", "db", "description\n"))# header
    for i, ex_name in enumerate(experiments):
        d, g = np.array(dbs[i]), np.array(guesses[i])
        if len(g) == N:
            if np.linalg.norm(g-d) > np.linalg.norm(np.flip(g)-d):
                g = np.flip(g)
            v_diff = list(g-d)
            v_diff2 = [abs(i) for i in v_diff]
            diff_norm = np.linalg.norm(np.array(v_diff)/np.array(d))
            f.write(template.format(ex_name, str(dbs[i]), 'real db\n'))
            f.write(template.format('', str(list(g)), 'guess\n'))
            f.write(template.format('', str(v_diff), 'diff\n'))
            f.write(template.format('', str(diff_norm), 'diff_norm\n'))
            f.write(template.format('', str(runtimes[i]), 'runtime\n'))
            f.write(template.format('', str(dropped_vols[i]), 'droppped\n'))

            f2.write(template2.format(str(list(g)), '\t', str(v_diff2), '\n'))
        else:
            f.write(template.format(ex_name, str(dbs[i]), 'real db\n'))
            f.write(template.format('', str(list(g)), 'guess\n'))
            f.write(template.format('', str(dropped_vols[i]), 'runtime\n'))

            #f2.write(template2.format(str(list(g)), '\n'))
        
    f.close()
    f2.close()

    return

def main():
    args = sys.argv[1:]
    if len(args) == 4:
        mode = str(sys.argv[1]) # If you just want to run clique set it to 'clique'
        noise_budget_val = float(sys.argv[2]) # Value for the noise budget
        drop_num_val = int(sys.argv[3]) # Set to number of volumes to be dropped randomly
        seed_val = int(sys.argv[4]) # Set the seed for randomly dropping volumes
        general_test(mode, noise_budget_val, drop_num_val, seed_val)
    
    return

if __name__ == "__main__":
    main()