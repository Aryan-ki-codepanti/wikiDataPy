
import networkx as nx
import matplotlib.pyplot as plt
from reader import WikiReader
from pprint import pprint

from matplotlib import pyplot as plt


class WikiGraph:

    def __init__(self, src_id):
        self.src_id = src_id
        self.edges = set()
        self.nodes = set()

        self.outdeg = 3

    def build_graph(self, current=None, r=3):
        if not r:
            return
        if not current:
            current = self.src_id

        self.nodes.add(current)
        ents = WikiReader.getRelatedEntitiesProps(
            current,  isTest=False, limit=self.outdeg)

        # print(f"CURRENT : {current}")
        # pprint(ents)

        # recurse
        for x, y in ents:
            self.edges.add((current, x, y))
            self.build_graph(current=y, r=r-1)

    def plot_graph(self):

        G = nx.DiGraph()

        for start, label, end in self.edges:
            G.add_edge(start, end, label=label)

        plt.figure(figsize=(20, 15))

        pos = nx.spring_layout(G, k=1, seed=42)

        nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue',
                font_size=8, font_weight='bold', edge_color='gray', arrowsize=30, arrowstyle="-|>", connectionstyle="arc3,rad=0.2")

        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_color='red')

        plt.title("Entity and Property Network Visualization")
        plt.show()


def test_build_graph():
    g = WikiGraph("Q5")

    g.build_graph()
    g.plot_graph()
    # pprint(g.nodes)
    # pprint(g.edges)


if __name__ == "__main__":
    test_build_graph()
