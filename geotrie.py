import pygtrie as trie


class GeoTrie:
    ''' An implementation of GeoTrie '''

    def __init__(self, gh_len):
        self.gh_len = gh_len
        # TODO: Add precision filter
        self.precision = 0
        self.trie = trie.StringTrie()

    def insert(self, key, value):
        # if len(key) != self.gh_len:
        #     raise Exception("Incorrect key length")
        node_val = self.trie.setdefault(key, [])
        node_val.append(value)
        self.trie[key] = node_val

    def search(self, key):
        if len(key) != self.gh_len:
            raise Exception("Incorrect key length")
        if self.trie.has_node(key):
            return self.trie[key]
        return []

    def clear(self):
        self.trie.clear()

    @staticmethod
    def __traverse_cb(path_conv, path, children, value=None):
        if value:
            return {path_conv(path): value}
        if children is None:
            return {}
        out = {}
        for c in children:
            out.update(c)
        return out

    def walk(self, fn):
        """fn takes a dictionary of keys in trie and their values"""
        fn(self.trie.traverse(GeoTrie.__traverse_cb))
