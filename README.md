# GeoTries
A geohash base Trie algorithm for geospatial indexing

## Geohashes

| Geohash length  | Cell width  | Cell height  |
|-----------------|-------------|--------------|
|       1         |	≤ 5,000km 	|	5,000km    |
|       2         |	≤ 1,250km 	|	625km      | 
|       3         |	≤ 156km 	|	156km      | 
|       4         |	≤ 39.1km 	|	19.5km     | 
|       5         |	≤ 4.89km 	|	4.89km     | 
|       6         |	≤ 1.22km 	|	0.61km     | 
|       7         |	≤ 153m 	    |	153m       | 
|       8         |	≤ 38.2m 	|	19.1m      |
|       9         |	≤ 4.77m 	|	4.77m      | 
|      10         |	≤ 1.19m 	|	0.596m     | 
|      11         |	≤ 149mm 	|	149mm      | 
|      12         |	≤ 37.2mm 	|	18.6mm     | 


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
    T = new Trie[polygon]
    for polygon p in s {
        geos = geohashesIntersecting(p, l)
        for geohash in geos {
            T.insert(geohash, p)
        }
    }

/*
  Insert into geotrie
*/
function Trie::insert(geohash, p) {
    if not this.has_node(geohash) {
        this.add_node(geohash, [])
    }
    node_val = this.search(geohash)
    node_val.append(p)
    this.set_node(geohash, node_val)
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
                q2.push(nbr)
            }
        }
        if q1 is empty and levelActive is true {
            levelActive = false
            swap q1, q2
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
function lookup(point p, length l, Trie T) {
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


## Optimization

1. Use HAMTrie instead of regular Trie for space optimization
2. Better alternative to BFS for neighbourhood scanning
3. Check for precision of bboxes and point before comparing