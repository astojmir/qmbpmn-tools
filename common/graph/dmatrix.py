
from .priodict import priorityDictionary

def dijkstra(LM, start, end=None):
    """
    Find shortest paths from the start vertex to all
    vertices nearer than or equal to the end.

    The output is a pair (D,P) where D[v] is the distance
    from start to v and P[v] is the predecessor of v along
    the shortest path from s to v.
    """
    # Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117228
    # David Eppstein, UC Irvine, 4 April 2002

    D = {}	# dictionary of final distances
    P = {}	# dictionary of predecessors
    Q = priorityDictionary()   # est.dist. of non-final vert.
    Q[start] = 0

    for v in Q:
        D[v] = Q[v]
        if v == end: break

        row_slc = slice(LM.indptr[v], LM.indptr[v+1])
        for w, dist in zip(LM.indices[row_slc], LM.data[row_slc]):
            vwLength = D[v] + dist
            if w in D:
                if vwLength < D[w]:
                    raise ValueError, \
                          "Dijkstra: found better path to already-final vertex"
            elif w not in Q or vwLength < Q[w]:
                Q[w] = vwLength
                P[w] = v

    return (D,P)


def shortest_path(LM, start, end):
    """
    Find a single shortest path from the given start vertex
    to the given end vertex.
    The input has the same conventions as dijkstra().
    The output is a list of the vertices in order along
    the shortest path.
    """
    # Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117228
    # David Eppstein, UC Irvine, 4 April 2002

    D,P = dijkstra(LM, start, end)
    Path = []
    while 1:
        Path.append(end)
        if end == start: break
        end = P[end]
    Path.reverse()
    return Path
