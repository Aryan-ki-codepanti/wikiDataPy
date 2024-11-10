
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
        self.names = {}

        self.outdeg = 3

    def buildGraph(self, current=None, r=3):
        if not r:
            return
        if not current:
            current = self.src_id

        self.nodes.add(current)
        ents = WikiReader.getRelatedEntitiesProps(
            current,  isTest=False, limit=self.outdeg)

        # recurse
        for x, y in ents:
            self.edges.add((current, x, y))
            self.buildGraph(current=y, r=r-1)

    def plotGraph(self):

        G = nx.DiGraph()

        for start, label, end in self.edges:
            G.add_edge(start, end, label=label)

        plt.figure(figsize=(20, 15))

        pos = nx.spring_layout(G, k=1, seed=42)

        # have different color for source node
        cols = list(map(lambda x: "red" if x ==
                    self.src_id else "skyblue", G.nodes()))

        nx.draw(G, pos, with_labels=True, node_size=3000, node_color=cols,
                font_size=8, font_weight='bold', edge_color='gray', arrowsize=30, arrowstyle="-|>", connectionstyle="arc3,rad=0.2")

        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_color='red')

        plt.title("Entity and Property Network Visualization")
        plt.show()

    def fetchNames(self, lang='en'):
        ids = set()
        for x, y, z in self.edges:
            ids.add(x)
            ids.add(y)
            ids.add(z)

        ids = list(ids)

        x = WikiReader.getEntitiesByIds(
            ids, options={"languages": [lang, "en"] if lang != 'en' else ['en'], "props": ["labels"]}, isTest=False)

        for k, v in x.items():

            self.names[k] = k
            if 'labels' in v:
                if lang in v['labels']:
                    self.names[k] = v['labels'][lang]['value']
                elif 'en' in v['labels']:
                    self.names[k] = v['labels']['en']['value']

    def plotNamedGraph(self, lang='en'):
        self.fetchNames(lang=lang)
        G = nx.DiGraph()

        for start, label, end in self.edges:
            G.add_edge(self.names[start], self.names[end],
                       label=self.names[label])

        plt.figure(figsize=(20, 15))

        pos = nx.spring_layout(G, k=1, seed=42)

        # have different color for source node
        cols = list(map(lambda x: "red" if x ==
                    self.names[self.src_id] else "skyblue", G.nodes()))

        nx.draw(G, pos, with_labels=True, node_size=3000, node_color=cols,
                font_size=8, font_weight='bold', edge_color='gray', arrowsize=30, arrowstyle="-|>", connectionstyle="arc3,rad=0.2")

        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_color='red', font_size=7)

        plt.title("Entity and Property Network Visualization")
        plt.show()


def test_build_graph():
    g = WikiGraph("Q5")

    g.buildGraph(r=2)
    g.plotNamedGraph()
    # g.plot_graph()
    # pprint(g.nodes)
    # pprint(g.edges)


if __name__ == "__main__":
    test_build_graph()

'''


edges = {
    ('Q101352', 'P1687', 'P6978'),
    ('Q101352', 'P279', 'Q121493679'),
    ('Q101352', 'P460', 'Q4116295'),
    ('Q1071027', 'P1535', 'Q16655449'),
    ('Q1071027', 'P279', 'Q10856962'),
    ('Q1071027', 'P527', 'Q101352'),
    ('Q10856962', 'P1424', 'Q11131773'),
    ('Q10856962', 'P279', 'Q60596080'),
    ('Q10856962', 'P910', 'Q6633985'),
    ('Q1457756', 'P2959', 'Q9757236'),
    ('Q1457756', 'P301', 'Q8425'),
    ('Q1457756', 'P31', 'Q59541917'),
    ('Q16655449', 'P2283', 'Q1071027'),
    ('Q16655449', 'P279', 'Q2085518'),
    ('Q170494', 'P1382', 'Q7239'),
    ('Q170494', 'P1889', 'Q29581314'),
    ('Q170494', 'P279', 'Q4936952'),
    ('Q20743760', 'P123', 'Q251266'),
    ('Q20743760', 'P31', 'Q3331189'),
    ('Q20743760', 'P629', 'Q20743757'),
    ('Q21201', 'P1424', 'Q8086768'),
    ('Q21201', 'P2578', 'Q8425'),
    ('Q21201', 'P910', 'Q6642550'),
    ('Q23852', 'P1343', 'Q20743760'),
    ('Q23852', 'P279', 'Q170494'),
    ('Q23852', 'P910', 'Q6539712'),
    ('Q3708001', 'P1204', 'Q7562301'),
    ('Q3708001', 'P31', 'Q4663903'),
    ('Q3708001', 'P910', 'Q8758490'),
    ('Q5', 'P1552', 'Q1071027'),
    ('Q5', 'P361', 'Q8425'),
    ('Q5', 'P527', 'Q23852'),
    ('Q6539712', 'P301', 'Q23852'),
    ('Q6539712', 'P31', 'Q4167836'),
    ('Q8425', 'P1151', 'Q3708001'),
    ('Q8425', 'P2579', 'Q21201'),
    ('Q8425', 'P910', 'Q1457756')
}

'''
