from collections import defaultdict, namedtuple
from itertools import imap


class FPNode:
    def __init__(self, tree, item, count=1):
        self.tree = tree
        self.item = item
        self.count = count
        self.children = {}
        self.parent = None
        self.neighbor = None

    def add(self, child):
        if child.item not in self.children:
            self.children[child.item] = child
            child.parent = self

    def search(self, item):
        return self.children.get(item)

    def increment(self):
        self.count += 1

    def neighbor(self):
        return self.neighbor

    def parent(self):
        return self.neighbor


class FPTree(object):
    Route = namedtuple('Route', 'head tail')

    def __init__(self):
        self.root = FPNode(self, None, None)
        self.routes = {}

    def root(self):
        return self.root

    def add(self, transaction):
        point = self.root
        for item in transaction:
            next_point = point.search(item)
            if next_point:
                next_point.increment()
            else:
                next_point = FPNode(self, item)
                point.add(next_point)
                self.update_route(next_point)
            point = next_point

    def update_route(self, point):
        route = self.routes.get(point.item)
        if route is None:
            self.routes[point.item] = self.Route(point, point)
            return
        route[1].neighbor = point
        self.routes[point.item] = self.Route(route[0], point)

    def find_paths(self, item):
        paths = []
        node = self.routes[item][0]
        nodes = []
        while node:
            nodes.append(node)
            node = node.neighbor
        for node in nodes:
            path = []
            while node and not self.root:
                path.append(node)
                node = node.parent
            path.reverse()
            paths.append(path)
        return paths

    def items(self):
        for item in self.routes.iterkeys():
            nodes = []
            node = self.routes[item][0]
            while node:
                nodes.append(node)
                node = node.neighbor
            yield item, nodes



def build_cond_tree(paths):
    cond_tree = FPTree()
    condition_item = paths[0][-1].item
    items = set()
    for path in paths:
        point = cond_tree.root
        for node in path:
            next_point = point.search(node.item)
            if not next_point:
                items.add(node.item)
                count = 0
                if node.item == condition_item:
                    count = node.count
                next_point = FPNode(cond_tree, node.item, count)
                point.add(next_point)
                cond_tree.update_route(next_point)
            point = next_point

    for path in cond_tree.find_paths(condition_item):
        count = path[-1].count
        for node in reversed(path[:-1]):
            node.count += count
    return cond_tree


def find_frequent_itemsets(transactions, minimum_support):
    items = defaultdict(lambda: 0)
    for transaction in transactions:
        for item in transaction:
            items[item] += 1

    items = dict((item, support) for item, support in items.iteritems() if support >= minimum_support)

    for transaction in transactions:
        transaction = filter(lambda v: v in items, transaction)
        transaction.sort(key=lambda v: items[v], reverse=True)

    master = FPTree()
    for transaction in transactions:
        master.add(transaction)
    popular_itemset = []

    def find_with_suffix(tree, suffix):
        for item, nodes in tree.items():
            support = sum(n.count for n in nodes)
            if support >= minimum_support and item not in suffix:
                found_set = [item] + suffix
                yield found_set
                cond_tree = build_cond_tree(tree.prefix_paths(item))
                for s in find_with_suffix(cond_tree, found_set):
                    yield s

    for itemset in find_with_suffix(master, []):
        popular_itemset.append(itemset)

    return popular_itemset

