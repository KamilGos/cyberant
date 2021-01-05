from collections import defaultdict, deque
from heapq import *
import logging
import re


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)


class PathFinder:
    def __init__(self, mapSize):
        self.mapSize = mapSize
        self.edgeLength = 1
        self.edges = self.generateEdges()


    def generateEdges(self):
        edges = []
        for x in range(self.mapSize[0]):
            for y in range(self.mapSize[1]):
                # up = x, y+1
                if y + 1 <= self.mapSize[1] - 1:
                    edges.append((str([x, y]), str([x, y + 1]), 1))
                # down
                if y - 1 >= 0:
                    edges.append((str([x, y]), str([x, y - 1]), 1))
                # left
                if x - 1 >= 0:
                    edges.append((str([x, y]), str([x - 1, y]), 1))
                # right
                if x + 1 <= self.mapSize[0] - 1:
                    edges.append((str([x, y]), str([x + 1, y]), 1))
        LOG.info("edges generated")
        return edges

    @staticmethod
    def stringListToList(slist):
        retlist = []
        for elem in slist:
            retlist.append([int(re.search('\[(.*),', elem).group(1)), int(re.search(',(.*)\]', elem).group(1))])
        return retlist

    def showEdges(self):
        print("Available Edges:")
        for edge in self.edges:
            print(edge)

    def dijkstra(self, f, t):
        g = defaultdict(list)
        for l, r, c in self.edges:
            g[l].append((c, r))

        q, seen, mins = [(0, f, ())], set(), {f: 0}
        while q:
            (cost, v1, path) = heappop(q)
            if v1 not in seen:
                seen.add(v1)
                path += (v1,)
                if v1 == t:
                    return self.stringListToList(list(path))

                for c, v2 in g.get(v1, ()):
                    if v2 in seen: continue
                    prev = mins.get(v2, None)
                    next = cost + c
                    if prev is None or next < prev:
                        mins[v2] = next
                        heappush(q, (next, v2, path))
        return float("inf")


if __name__ == "__main__":
    mapSize = [3, 3]
    PF = PathFinder(mapSize)
    PF.showEdges()

    path = PF.dijkstra("[0, 0]", "[2, 2]")
    print(path)
