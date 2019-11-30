# GeoTries
A geohash base Trie algorithm for geospatial indexing

## Geohashes

```
lvl | bits |   error       |    base4   |  base16  |  base64
-------------------------------------------------------------
  0 |   0  |  20015.087 km |   prec  0  |  prec 0  |  prec 0
  1 |   2  |  10007.543 km |   prec  1  |          |
  2 |   4  |   5003.772 km |   prec  2  |  prec 1  |
  3 |   6  |   2501.886 km |   prec  3  |          |  prec 1
  4 |   8  |   1250.943 km |   prec  4  |  prec 2  |
  5 |  10  |    625.471 km |   prec  5  |          |
  6 |  12  |    312.736 km |   prec  6  |  prec 3  |  prec 2
  7 |  14  |    156.368 km |   prec  7  |          |
  8 |  16  |     78.184 km |   prec  8  |  prec 4  |
  9 |  18  |     39.092 km |   prec  9  |          |  prec 3
 10 |  20  |     19.546 km |   prec 10  |  prec 5  |
 11 |  22  |   9772.992  m |   prec 11  |          |
 12 |  24  |   4886.496  m |   prec 12  |  prec  6 |  prec 4
 13 |  26  |   2443.248  m |   prec 13  |          |
 14 |  28  |   1221.624  m |   prec 14  |  prec  7 |
 15 |  30  |    610.812  m |   prec 15  |          |  prec 5
 16 |  32  |    305.406  m |   prec 16  |  prec  8 |
 17 |  34  |    152.703  m |   prec 17  |          |
 18 |  36  |     76.351  m |   prec 18  |  prec  9 |  prec 6
 19 |  38  |     38.176  m |   prec 19  |          |
 20 |  40  |     19.088  m |   prec 20  |  prec 10 |
 21 |  42  |    954.394 cm |   prec 21  |          |  prec 7
 22 |  44  |    477.197 cm |   prec 22  |  prec 11 |
 23 |  46  |    238.598 cm |   prec 23  |          |
 24 |  48  |    119.299 cm |   prec 24  |  prec 12 |  prec 8
 25 |  50  |     59.650 cm |   prec 25  |          |
 26 |  52  |     29.825 cm |   prec 26  |  prec 13 |
 27 |  54  |     14.912 cm |   prec 27  |          |  prec 9
 28 |  56  |      7.456 cm |   prec 28  |  prec 14 |
 29 |  58  |      3.728 cm |   prec 29  |          |
 30 |  60  |      1.864 cm |   prec 30  |  prec 15 |  prec 10
 31 |  62  |      0.932 cm |   prec 31  |          |
 32 |  64  |      0.466 cm |   prec 32  |  prec 16 |
 -------------------------------------------------------------
```

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
*/
function geohashIntersecting(polygon p, length l) {
    // one of the overelap discovery algorithms is called here
}

```

### Overlaps Discovery Algorithm

- ##### Neighbour BFS

```
/*
  Use centroid of polygon as starting point.
  Then, perform BFS on centroid, visiting its neighbours and check for intersection.
  Continue till we find a level where none of neighbours intersect the polygon.  
*/
function neighbour_bfs(polygon p, length l) {
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

- ##### Subsampling

```
/*
    Find minimum edge of geohashof length l
    Divide bounding box of polygon at above intervals
    For every point produced, check if its geohash intersects poly
*/
function subsampling(polygon p, length l) {
    gh_bbox = geohash((0,0), l).bounding_box
    intercept = min(gh_bbox.width, gh_bbox.height)
    poly_bbox = p.bounding_box
    overlaps = []
    subsamples = []
    for lon in [poly_bbox.lon_min, poly_bbox.lon_max] in steps of intercept {
        for lon in [poly_bbox.lat_min, poly_bbox.lat_max] in steps of intercept {
            subsamples.append(geohash((lon, lat), l))
        }
    }

    for sample in subsamples {
        if sample.bbox intersects poly {
            overlaps.append(sample)
        }   
    }
    return overlaps  
}
```

- ##### Top-down search

```
/*
    Find geohash of shortest length that contains p
    If not found, find all geohashes of length 1 that intersect p
    For every geohash found above,
        Recursively search children until geohash of length l is made, and
        return if it intersects poly 
*/
function topdown_search(polygon p, length l) {
    1. let search_items = []
    2. find smallest geohash s that contains p
    3. if s
            search_items = [s]
       else
            search_items = all geohashes of length 1 that intersect poly
    4. overlaps = []
    5. for item in search_items
        5a. overlaps.append(search_children(poly, item, l))
    return overlaps
}

function search_children(polygon p, prefix pfx, length l) {
    if pfx.length = l {
        if pfx.bbox.intersects(p) {
            return [p]
        } else {
            return []
        }
    }

    if not pfx.bbox.intersects(poly) {
        return []
    }
    overlaps = []
    children = pfx.children
    for c in children {
        overlaps.append(search_child(p, child, l))
    }
    return overlaps
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
    containers = []
    for c in candidates {
        if c contains p {
            containers.append(c)
        }
    }
    return containers
}
```


## Optimization

1. Use HAMTrie instead of regular Trie for space optimization
2. Use generators instead of lists where possible
3. Cache geohashes and their polygons?

## TODO

1. Add support for region queries
2. Add update logic (geotrie and strtree)
3. Benchmark update logic
4. Benchmark region queries
5. Analyze disk access as a performance metric
6. Line queries?

```
For rect (n,m), how many (a,b) rects can itersect it
x = floor(n/a)
y = floor(m/b)
X = x+1
Y = y+1
p = 1 + ax - n
q = 1 + by - n
=> xy + 2(X + Y) + 3pq + 1

for squares on square:
=> x^2 + 4X + 4 + 3(1+ax-n)^2 + 1
```