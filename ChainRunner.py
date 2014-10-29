import string
from blist import sortedlist
import random
from functools import total_ordering
import sys

###Make the graph###
##comments##
def makeGraph(fname):
    def overlap(a, b):
        atoks = string.split(a, " ")
        btoks = string.split(b, " ")
        for i in xrange(1, len(atoks) + 1):
            if i <= len(btoks) and atoks[-i:] == btoks[0:i]: return True
        return False
    
    namelist = []
    graph = []
    
    fin = open(fname)
    for line in fin: namelist.append(string.strip(line))
    fin.close()
    for a in xrange(0, len(namelist)):
        if a % 10 == 0: print a
        graph.append([])
        for b in xrange(0, len(namelist)):
            if a != b and overlap(namelist[a], namelist[b]):
                graph[a].append(b)
    return dict(enumerate(graph))

def readGraph(fname):
    graph = {}
    fin = open(fname)
    for line in fin:
        k = int(line.split(":")[0])
        graph[k] = []
        for i in string.split(line.split(":")[1]):
            graph[k].append(int(i))
    fin.close()
    return graph
    
def writeGraph(g, fname):
    fout = open(fname, "w")
    for i in g:
        fout.write(str(i) + ": ")
        for j in g[i]:
            fout.write(str(j) + " ")
        fout.write("\n")
    fout.close()

def writeGraph2(g, chains, fname):
    fout = open(fname, "w")
    for i in g:
        fout.write(str(i) + " " + str(len(chains[i])) + ": ")
        for j in g[i]:
            fout.write(str(j) + " ")
        fout.write("\n")
    fout.close()
    
def toDot(g, fname):
    fout = open(fname, "w")
    fout.write("digraph G {\n")
    for i in g:
        for j in g[i]:
            fout.write(str(i) + " -> " + str(j) + ";\n")
    fout.write("}")
    fout.close()

###Output final answer to string###
def pathToString(path, moviefile):
    def overlapCount(a, b):
        atoks = string.split(a, " ")
        btoks = string.split(b, " ")
        for i in xrange(1, len(atoks) + 1):
            if i <= len(btoks) and atoks[-i:] == btoks[0:i]: return i
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
            print "ERROR: No overlap between titles"
            return ""
        result += " " + string.join(string.split(namelist[i])[over:])
        prev = namelist[i]
    return result

###Connected Component checking###
def updateLabels(labels, graph, i):
    for j in graph[i]:
        if labels[j] != labels[i]:
            labels[j] = labels[i]
            updateLabels(labels, graph, j)

def connectedComponents(g):
    graph = {}
    for k in g:
        if not k in graph: graph[k] = set()
        for i in g[k]:
            graph[k].add(i)
            if not i in graph: graph[i] = set()
            graph[i].add(k)
            
    labels = dict({(i,i) for i in graph})
    for i in graph:
        updateLabels(labels, graph, i)
        
    inv_map = {}
    for k, v in labels.iteritems():
        inv_map[v] = inv_map.get(v, [])
        inv_map[v].append(k)
    return inv_map

def getLargeComponents(minsize, graph):
    comps = connectedComponents(graph)
    largecomps = []
    for k in comps:
        if len(comps[k]) >= minsize: largecomps.append(dict((i, graph[i]) for i in comps[k]))
    return largecomps

def inducedSubgraph(graph, vert):
    ans = {}
    F = {vert}
    while len(F) > 0:
        Fp = set()
        for v in F: 
            if v not in ans:
                ans[v] = graph[v]
                Fp = Fp | set(graph[v])
        F = Fp
    return ans

###Trimming dead-end chains/trees###
def hasDeadEnds(g):
    return not all((len(g[k]) > 0 for k in g))
def trim(graph):
    leafChains = {k: [] for k in graph}
    while hasDeadEnds(graph):
        newg = {}
        for k in graph:
            if len(graph[k]) > 0: newg[k] = []
            for i in graph[k]:
                if len(graph[i]) == 0:
                    if len(leafChains[i]) >= len(leafChains[k]): leafChains[k] = [i] + leafChains[i]
                else: newg[k].append(i)
        graph = newg
    return (graph, {k: leafChains[k] for k in leafChains if k in graph})


def collapse(graph, chains):
    def inDeg(n):
        return len([x for x in graph if n in graph[x]])
    innerChains = {}
    newchains = dict(chains)
    g = {n: [(c, 1) for c in l] for n,l in graph.items() if inDeg(n) != 1}
    for n in g:
        while not all([c in g for (c, w) in g[n]]):
            newl = []
            for (c, w) in g[n]:
                if c not in g:
                    newl += [(x,w+1) for x in graph[c]]
                    
                    for x in graph[c]: innerChains[(n, x)] = (innerChains[(n, c)] + [c]) if w > 1 else [c]
                    
                    if len(newchains[n]) < len(newchains[c]): newchains[n] = [c] + newchains[c]
                else: newl.append((c, w))
            g[n] = newl
    return (g, {n:c for n,c in newchains.items() if n in g}, innerChains)

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

class graph:
    def __init__(self, g):
        (self.g, self.chains) = trim(g)
        (self.wg, self.chains, self.innerChains) = collapse(self.g, self.chains)
        
        self.eWeights = {(k,b):w for k,v in self.wg.items() for (b,w) in v}
        self.eWeights = {(k,b):1 for k,v in self.g.items() for b in v}
        self.vWeights = {k:len(v) for k,v in self.chains.items()}
        self.g = {k: [c for c,_ in v] for k,v in self.wg.items()}
        
    def chainLen(self, c):
        if len(c) == 0: return 0
        l = 1
        oldn = c[0]
        for n in c[1:]:
            l += self.eWeights[(oldn, n)]
            oldn = n
        return l + self.vWeights[c[-1]]
    
    def expandChain(self, c):
        newc = [c[0]]
        for n in c[1:]:
            newc += self.innerChains[(newc[-1], n)] + [n]
        return newc + self.chains[c[-1]]
    
@total_ordering
class chain(object):
    def __init__(self, g, c = []):
        self.c = list(c)
        self.g = g
        self.len = g.chainLen(c)
    def __getitem__(self, i):
        if isinstance(i, slice): return chain(self.g, self.c[i])
        else: return self.c[i]
    def __add__(self, other):
        newc = chain(self.g)
        if len(self) > 0 and len(other) > 0: newc.len = g.eWeights[(self[-1], other[0])] - g.vWeights[self[-1]] - 1
        if isinstance(other, chain):
            newc.c = self.c + other.c
            newc.len += len(self) + len(other)
        else:
            newc.c = self.c + other
            newc.len += len(self) + g.chainLen(other)
        return newc
    def __radd__(self, other):
        return chain(self.g, other) + self
    def __iadd__(self, other):
        if len(self) > 0 and len(other) > 0: self.len += g.eWeights[(self[-1], other[0])] - g.vWeights[self[-1]]
        if isinstance(other, chain):
            self.c += other.c
            self.len += len(other)
        else:
            self.c += other
            self.len += g.chainLen(other)
        return self
    def __len__(self): return self.len
    def __eq__(self, other): return self.c == other.c
    def __gt__(self, other): return len(self) > len(other) or (len(self) == len(other) and self.c > other.c)
    def __repr__(self): return "(" + str(self.c) + " len: " + str(self.len) + ")"
    def index(self, n): return self.c.index(n)

###Search algorithm 2###
def updatePaths(node, g, paths, bestp, idleCounts):
    #if idleCounts[node] > 10: return (False, bestp)
    mypaths = paths[node]
    oldLens = [len(x) for x in mypaths]
    refresh = idleCounts[node] > 30
    if refresh: mypaths = sortedlist([chain(g, [node])], key = lambda x: len(x))
    for child in g.g[node]:
        if idleCounts[child] <= 1 or refresh:
            for path in paths[child]:
                if not node in path: mypaths.add([node]+path)
                else: mypaths.add([node] + path[:path.index(node)])
    if len(mypaths[-1]) > len(bestp): bestp = mypaths[-1]
    
    paths[node] = mypaths[-10:]
    if [len(x) for x in paths[node]] == oldLens: idleCounts[node] += 1
    else: idleCounts[node] = 0
    return bestp
    
def findPaths(g):
    bestp = chain(g)
    blen = 0
    paths = {n: sortedlist([chain(g, [n])], key = lambda x: len(x)) for n in g.g}
    idleCounts = {n:0 for n in g.g}
    changesMade = 1
    keys = list(g.g.keys())
    while changesMade > 0:
        random.shuffle(keys)
        changesMade = 0
        for n in keys:
            bestp = updatePaths(n, g, paths, bestp, idleCounts)
            if idleCounts[n] == 0: changesMade += 1
            
        if len(bestp) > blen:
            blen = len(bestp)
            print bestp
        print "updated", changesMade, "nodes, max len", blen, "          \r",
        sys.stdout.flush()
    print "done, longest path:", blen, "        "
    print bestp

g = graph(readGraph("graphMainComponent.txt"))