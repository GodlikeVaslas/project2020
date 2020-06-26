from collections import defaultdict, namedtuple


class FPNode:
    def __init__(self, item, count=1):
        self._item = item
        self._count = count
        self._parent = None
        self._children = {}
        self._neighbor = None

    def add(self, child):
        if child.item not in self._children:
            self._children[child.item] = child
            child.parent = self

    def search(self, item):
        return self._children.get(item)

    @property
    def item(self):
        return self._item

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value

    def increment(self):
        self._count += 1

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def neighbor(self):
        return self._neighbor

    @neighbor.setter
    def neighbor(self, value):
        self._neighbor = value

    @property
    def root(self):
        return self._item is None and self._count is None


class FPTree:
    Route = namedtuple('Route', 'head tail')

    def __init__(self):
        self._root = FPNode(None, None)
        self._routes = {}

    @property
    def root(self):
        return self._root

    def add(self, transaction):
        point = self._root
        for item in transaction:
            next_point = point.search(item)
            if next_point:
                next_point.increment()
            else:
                next_point = FPNode(item)
                point.add(next_point)
                self.update_route(next_point)

            point = next_point

    def update_route(self, point):
        route = self._routes.get(point.item)
        if route is None:
            self._routes[point.item] = self.Route(point, point)
            return
        route[1].neighbor = point
        self._routes[point.item] = self.Route(route[0], point)

    def items(self):
        items = []
        for item in self._routes:
            items.append((item, self.nodes(item)))
        return items

    def nodes(self, item):
        node = self._routes[item][0]
        nodes = []
        while node:
            nodes.append(node)
            node = node.neighbor
        return nodes

    def find_paths(self, item):
        paths = []
        for node in self.nodes(item):
            path = []
            while node and not node.root:
                path.append(node)
                node = node.parent
            path.reverse()
            paths.append(path)
        return paths


def build_cond_tree(paths):
    cond_tree = FPTree()
    condition_item = None
    items = set()
    for path in paths:
        if len(path) == 0:
            continue
        if condition_item is None:
            condition_item = path[-1].item
        point = cond_tree.root
        for node in path:
            next_point = point.search(node.item)
            if not next_point:
                items.add(node.item)
                count = 0
                if node.item == condition_item:
                    count = node.count
                next_point = FPNode(node.item, count)
                point.add(next_point)
                cond_tree.update_route(next_point)
            point = next_point
    assert condition_item is not None
    for path in cond_tree.find_paths(condition_item):
        count = path[-1].count
        for node in reversed(path[:-1]):
            node.count += count
    return cond_tree


def fpgrowth(transactions, minimum_support):
    items = defaultdict(lambda: 0)
    for transaction in transactions:
        for item in transaction:
            items[item] += 1

    items = dict((item, support) for item, support in items.items() if support >= minimum_support)

    master = FPTree()
    for transaction in transactions:
        transaction = list(filter(lambda v: v in items, transaction))
        transaction.sort(key=lambda v: items[v], reverse=True)
        master.add(transaction)
    popular_itemset = []

    def find_with_suffix(tree, suffix):
        for elem, nodes in tree.items():
            support = 0
            for n in nodes:
                support += n.count
            if support >= minimum_support and elem not in suffix:
                found_set = [elem] + suffix
                yield found_set
                cond_tree = build_cond_tree(tree.find_paths(elem))
                for s in find_with_suffix(cond_tree, found_set):
                    yield s

    for itemset in find_with_suffix(master, []):
        popular_itemset.append(itemset)

    return popular_itemset

