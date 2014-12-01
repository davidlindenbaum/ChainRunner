import random
import sys
from MovieGraph import *

###Output final answer to string###
def pathToString(path, moviefile):
    def overlapCount(a, b):
        atoks = string.split(a, " ")
        btoks = string.split(b, " ")
        for i in xrange(1, len(atoks) + 1):
            for j in xrange(max(1, i-2), min(i+2, len(btoks)) + 1):
                if string.join(atoks[-i:],'') == string.join(btoks[0:j],''): return j
        return 0
    if len(path) != len(set(path)):
        print "ERROR: Path contains duplicates"
        return ""
    namelist = []
    fin = open(moviefile)
    for line in fin: namelist.append(string.strip(line))
    fin.close()
    prev = namelist[path[0]]
    result = namelist[path[0]]
    for i in path[1:]:
        over = overlapCount(prev, namelist[i])
        if over == 0: 
            print "ERROR: No overlap between titles",prev,namelist[i]
            return ""
        result += " " + string.join(string.split(namelist[i])[over:])
        prev = namelist[i]
    return result

###Search algorithm 1###
def searchFrom(start, graph, chains):
    maxd = 1
    maxp = []
    nodesUsed = {start: [[start]]}
    leaves = [(start, [start])]
    while len(leaves)>0:
        print len(leaves)
        (n, p) = leaves.pop()
        d = len(p) + len(chains[n])
        if d > maxd:
            maxd = d
            maxp = p + chains[n]
            print "depth",maxd
        #p = path to reach node n, child = child of n
        for child in graph[n]:
            pnew = p + [child]
            if not child in nodesUsed:
                leaves.append((child, pnew))
                nodesUsed[child] = [(pnew)]
            elif not child in p:
                b = max([len(x) for x in nodesUsed[child]])
                if len(pnew) > b:
                    leaves.append((child, pnew))
                    nodesUsed[child].append(pnew)
                #else:
                    #leaves.insert(0, (child, pnew))
                    #nodesUsed[child].append(pnew)
    return (maxd, maxp)

def searchAll(graph):
    (g, chains) = trim(graph)
    maxlen = 0
    maxpath = []
    count = 0
    for i in g:
        count += 1
        if count%10 == 0: print count, "of", len(g), "starts tried"
        (d, p) = searchFrom(i, g, chains)
        if d > maxlen:
            maxlen = d
            maxpath = p
            print d
    return maxpath


###Search algorithm 2###
###Takes which node to update, the graph, the current paths dict, 
###and the dict representing how long each vert has gone without updating
###returns the (path, len) pair for the new best path from this vert
def updatePaths(node, g, paths, idleCounts, allPaths):
    mypaths = paths[node]
    oldLens = {x for (_,x) in mypaths}
    refresh = idleCounts[node] > 30
    if refresh: mypaths = [([node], g.vWeight(node) + 1)]
    for child in g.neighbors(node):
        if idleCounts[child] <= 1 or refresh:
            for path in paths[child]:
                mypaths.append(g.prepend(node, path))
    
    mypathsNoDup = []
    for x in mypaths:
        if not x in mypathsNoDup:
            mypathsNoDup.append(x)
            #allPaths[node].add(tuple(x[0]))
    mypathsNoDup.sort(key = lambda (l,x):x)
    
    paths[node] = mypathsNoDup[-10:]
    if {x for (_,x) in paths[node]} == oldLens: idleCounts[node] += 1
    else: idleCounts[node] = 0
    return mypaths[-1]
    
###Takes a graph object, does the search and returns a dict (vert -> (path, len) list)
###vert maps to a list of the longest paths from the vert, paired with their lengths
def findPaths(g, allPaths = None):
    if allPaths == None: allPaths = {n: set() for n in g.nodes()}
    bestp, blen = [], 0
    paths = {n: [([n], g.vWeight(n) + 1)] for n in g.nodes()}
    idleCounts = {n:0 for n in g.nodes()}
    changesMade = 1
    keys = g.nodes()
    try:
        while changesMade > 0:
            random.shuffle(keys)
            changesMade = 0
            a = False
            for n in keys:
                result = updatePaths(n, g, paths, idleCounts, allPaths)
                if result[1] > blen:
                    (bestp, blen) = result
                    a = True
                if idleCounts[n] == 0: changesMade += 1
                
            if a:
                print bestp, blen
            print "updated", changesMade, "nodes, max len", blen, "          \r",
            sys.stdout.flush()
    except KeyboardInterrupt:
        print "done, longest path:", blen, "        "
        print bestp
        return (paths, allPaths)
    print "done, longest path:", blen, "        "
    print bestp
    return (paths, allPaths)

def writePaths(paths):
    f = open('somanypaths.txt', 'w')
    f.write('{\n')
    for n in paths:
        f.write(str(n) + ': ' + str(paths[n]) + '\n')
    f.write('}')
    f.close()
