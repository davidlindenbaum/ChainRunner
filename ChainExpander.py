from MovieGraph import *

def findNewChain(start, ends, skip, chain, g, allowEnd, margin, maxdepth):
    if len(chain) == maxdepth: return []
    chain.append(start)
    
    best = []
    depth = len(chain)

    for next in g.neighbors(start):
        #Don't follow the same chain we're trying to expand
        if depth < len(ends) and ends[depth] == next: continue
        ind = ends.index(next) if next in ends else -1
        if next in skip and ind == -1: continue
        if ind >= 0 and ind < depth:
            p = chain + ends[ind:]
            if len(p) > len(best) and len(set(p)) == len(p): best = p
            
        p = findNewChain(next, ends, skip, list(chain), g, allowEnd, margin, maxdepth)
        if len(p) > len(best): best = p
        
    return best
    
def expandChain(chain, g, margin, maxdepth):
    origlen = len(chain)
    skip = set(chain)
    
    for i in range(len(chain)):
        print i+1,"of",len(chain)
        next = chain[i:i+margin+1]
        r = findNewChain(chain[i], next, skip, [], g, False, margin, maxdepth)

        if len(r) > len(next):
            skip -= set(next)
            skip |= set(r)
            chain[i:i+margin+1] = r
            print chain, len(chain)
            
    if len(chain) > origlen:
        print len(chain)
        print chain






def extendBasic(paths, p, g):
    def disjoint(a, b):
        return len(set(a) & set(b)) == 0
    for i in range(len(p)):
        if p[i] in paths: 
            for a in paths[p[i]]:
                if disjoint(a, p[:i]) and len(a) > len(p)-i: print("Found better")

def extendPath(paths, p):
    def disjoint(a, b):
        return len(set(a) & set(b)) == 0
    def disjointPre(a, b):
        if disjoint(a,b): return a
        for i in range(len(a)):
            if a[i] in b: return a[:i]
    #i = each index in p at which we're trying to insert a new path
    for i in range(len(p)):
        print i
        if p[i] in paths:
            #a = a path we can insert at position i, disjoint with the first i elems of p
            for a in paths[p[i]]:
                a = disjointPre(a, p[:i])
                #how much of a will we try to insert
                for j in range(len(a)):
                    b = a[:j+1]
                    if disjoint(b, p[i+1:]) and len(b) > len(p)-i-1: return p[:i]+b
                    if b[-1] in p[i+1:]:
                        loc = p.index(b[-1])
                        res = p[:i] + list(b[:-1]) + disjointPre(p[loc:], b[:-1])
                        if len(res) > len(p): return res
                        
def extendPath2(paths, p):
    def disjoint(a, b):
        return len(set(a) & set(b)) == 0
    for i in range(len(p)):
        print i
        if p[i] in paths:
            pathsi = paths[p[i]]
            for j in range(i, len(p)):
                if p[j] in pathsi:
                    pathsij = pathsi[p[j]]
                    for subp in pathsij:
                        if len(subp) > j-i+1 and disjoint(subp, p[:i] + p[j+1:]):
                            return p[:i] + list(subp) + p[j+1:]