import json
import networkx as nx
from pathlib import Path


INPUT_FILE = Path("data/processed/asu_cs_courses.json")


def load_courses():
    with INPUT_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_graph(courses):
    G = nx.DiGraph()

    for course in courses:
        course_code = course["course_code"]
        title = course["title"]
        credits = course["credits"]

        # add course node
        G.add_node(
            course_code,
            node_type="course",
            title=title,
            credits=credits
        )

        # add format nodes + relationships
        for fmt in course.get("formats", []):
            G.add_node(fmt, node_type="format")
            G.add_edge(course_code, fmt, relation="offered_as")

    return G


def print_summary(G):
    print("\n=== GRAPH SUMMARY ===")
    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())

    print("\n=== SAMPLE COURSE NODES ===")
    count = 0
    for node, data in G.nodes(data=True):
        if data.get("node_type") == "course":
            print(node, "->", data)
            count += 1
        if count == 5:
            break

    print("\n=== SAMPLE EDGES ===")
    count = 0
    for source, target, data in G.edges(data=True):
        print(f"{source} --[{data['relation']}]--> {target}")
        count += 1
        if count == 10:
            break


def main():
    courses = load_courses()
    graph = build_graph(courses)
    print_summary(graph)


if __name__ == "__main__":
    main()