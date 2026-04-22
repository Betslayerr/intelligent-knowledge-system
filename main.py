import json
import networkx as nx


def load_data():
    with open("data/courses.json") as f:
        return json.load(f)


def build_graph(data):
    G = nx.DiGraph()

    for item in data:
        if "requires" in item:
            G.add_edge(item["course"], item["requires"], relation="requires")

        if "teaches" in item:
            G.add_edge(item["course"], item["teaches"], relation="teaches")

    return G


def main():
    data = load_data()
    graph = build_graph(data)

    print("Nodes:", graph.nodes())
    print("Edges:", graph.edges(data=True))


if __name__ == "__main__":
    main()