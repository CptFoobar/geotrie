# GeoTries
A geohash base Trie algorithm for geospatial indexing

## Algorithm

### Initialization

1. Set length l for geohashes

### Building the Trie

```
/*
  Create a Trie for polygons keyed by alphanumerics
  For every polygon, find all the geohashes that intersect this polygon
  and add them to the trie
  This results in a trie where every leaf node maps a geohash to a list of
  shapes it intersects
*/
function buildTree(shapes s, length l) {
    T = new HAMTrie[polygon]
    for polygon p in s {
        geos = geohashesIntersecting(p, l)
        for geohash in geos {
            T.insert(geohash, p)
        }
    }

/*
  Find geohashes whose bounding box intersects this polygon.
  For this, use centroid of polygon as starting point.
  Then, perform BFS on centroid, visiting its neighbours and check for intersection.
  Continue till we find a level where none of neighbours intersect the polygon.  
*/
function geohashIntersecting(polygon p, length l) {
    c = p.centroid
    g = geohash(c, l)
    boxes = []
    visited = Map[String, Boolean]()
    q1 = Queue([g])
    q2 = Queue()
    levelActive = false

    while q1 is not empty {
        n = q1.pop()
        if not visited[n] {
            visited[n] = true
            if n.bbox intersects p {
                boxes.append(n)
                levelActive = true
            }
        }
        next = n.neighbours()
        for nbr in next {
            if not visited[nbr] {
                q1.push(nbr)
            }
        }
        if q1 is empty and levelActive is true {
            levelActive = true
            q1.swap(q2)
        }
    }
    return boxes
}

```


### Searching in Trie

```
/*
  Lookup the containing polygon for point p by generating its l-length geohash
  and searching in geotrie.
  Iterate through polygons obtained and find if any contains point
*/
function lookup(point p, length l, HAMTrie T) {
    g = geohash(p, l)
    candidates = T.search(g)
    for c in candidates {
        if c contains p {
            return c
        }
    }
    return null
}
```