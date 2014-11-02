import string

###Make the graph###
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
    
###Connected Component checking###
def connectedComponents(g):
    def updateLabels(labels, graph, i):
        for j in graph[i]:
            if labels[j] != labels[i]:
                labels[j] = labels[i]
                updateLabels(labels, graph, j)
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
###Collapsing in-degree 1 nodes into their parent
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


###Graph object. Avoid referencing class variables directly - use the methods instead
class graph:
    def __init__(self, g):
        (self.g, self.chains) = trim(g)
        self.vWeights = {k:len(v) for k,v in self.chains.items()}
        
    def nodes(self):
        return self.g.keys()
    def neighbors(self, n):
        return self.g[n]
    def vWeight(self, n):
        return self.vWeights.get(n, 0)
    
    def __len__(self):
        return len(self.g)
    def __repr__(self):
        return "<graph: " + str(len(self)) + " nodes>"
    
    def subGraph(self, node):
        ans = {}
        F = {node}
        while len(F) > 0:
            Fp = set()
            for v in F: 
                if v not in ans:
                    ans[v] = self.g[v]
                    Fp = Fp | set(self.g[v])
            F = Fp
        g = graph(ans)
        g.chains = {v: self.chains[v] for v in g.nodes()}
        g.vWeights = {v: self.vWeights[v] for v in g.nodes()}
        return g
        
    def pathLen(self, p):
        if len(p) == 0: return 0
        return len(p) + self.vWeight(p[-1])
    
    def expandPath(self, p):
        return p + self.chains[p[-1]]
    
    def append(self, node, (l, x)):
        if len(l) == 0: return ([node], 1 + self.vWeight(node))
        if not node in l: return (l + [node], len(l) + 1 + self.vWeight(node))
        else: return (l[l.index(node)+1:] + [node], l.index(node) + 1 + self.vWeight(node))
    
    def prepend(self, node, (l, x)):
        if not node in l: return ([node] + l, x + 1)
        else: return ([node] + l[:l.index(node)], l.index(node) + 1)
            
###A graph where all vertices with in-degree 1 are merged with their parents
class collapsedGraph(graph):
    def __init__(self, g):
        if isinstance(g, collapsedGraph):
            self.source = g.source
            self.wg = dict(g.wg)
            self.chains = dict(g.chains)
            self.innerChains = dict(g.innerChains)
            self.eWeights = dict(g.eWeights)
            self.vWeights = dict(g.vWeights)
            self.g = dict(g.g)
        else: self.source = g if isinstance(g, graph) else graph(g)
        (self.wg, self.chains, self.innerChains) = collapse(self.source.g, self.source.chains)
        self.eWeights = {(k,b):w for k,v in self.wg.items() for (b,w) in v}
        self.vWeights = {k:len(v) for k,v in self.chains.items()}
        self.g = {k: [c for c,_ in v] for k,v in self.wg.items()}
        
    def __repr__(self):
        return "<collapsedGraph: " + str(len(self)) + " nodes>"
    
    def subGraph(self, vert):
        return collapsedGraph(self.source.subGraph(vert))
    
    def pathLen(self, p):
        if len(p) == 0: return 0
        l = self.vWeights[p[-1]] + 1
        oldn = p[0]
        for n in p[1:]:
            l += self.eWeights[(oldn, n)]
            oldn = n
        return l
    
    def expandPath(self, p):
        newp = [p[0]]
        for n in p[1:]:
            newp += self.innerChains[(newp[-1], n)] + [n]
        return newp + self.chains[p[-1]]
    
    def append(self, node, (l, x)):
        if not node in l: return (l + [node], self.pathLen(l + [node]))
        else: return (l[l.index(node)+1:] + [node], self.pathLen(l[l.index(node)+1:] + [node]))
    
    def prepend(self, node, (l, x)):
        if not node in l: return ([node] + l, x + self.eWeights[(node, l[0])])
        else: 
            newl = [node] + l[:l.index(node)]
            return (newl, self.pathLen(newl))
        
g = graph(readGraph("graphMainComponent.txt"))