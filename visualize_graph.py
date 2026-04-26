import json
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


INPUT_FILE = Path("data/processed/asu_cs_courses.json")
OUTPUT_FILE = Path("data/output/asu_course_graph.png")


def load_courses():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def categorize_course(title):
    title_lower = title.lower()

    if any(word in title_lower for word in [
        "artificial intelligence",
        "ai systems",
        "machine learning",
        "reinforcement learning"
    ]):
        return "AI/ML"

    if any(word in title_lower for word in ["security", "cryptography"]):
        return "Cybersecurity"

    if any(word in title_lower for word in ["database", "data science"]):
        return "Data/Database"

    if any(word in title_lower for word in ["linux", "network", "architecture", "host", "device"]):
        return "Systems"

    if any(word in title_lower for word in [
        "programming",
        "computer science i",
        "computer science ii",
        "data structures"
    ]):
        return "Programming/Foundation"

    if any(word in title_lower for word in ["research", "internship", "senior design", "thesis"]):
        return "Research/Capstone"

    return "Other"


def build_graph(courses):
    graph = nx.DiGraph()

    for course in courses:
        code = course["course_code"]
        title = course["title"]
        category = categorize_course(title)

        graph.add_node(code, node_type="course", label=code)
        graph.add_node(category, node_type="category", label=category)
        graph.add_edge(code, category, relation="belongs_to_category")

        for fmt in course.get("formats", []):
            graph.add_node(fmt, node_type="format", label=fmt)
            graph.add_edge(code, fmt, relation="offered_as")

    return graph


def visualize_graph(graph):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(14, 10))

    pos = nx.spring_layout(graph, seed=42, k=0.8)

    course_nodes = [
        node for node, data in graph.nodes(data=True)
        if data.get("node_type") == "course"
    ]

    category_nodes = [
        node for node, data in graph.nodes(data=True)
        if data.get("node_type") == "category"
    ]

    format_nodes = [
        node for node, data in graph.nodes(data=True)
        if data.get("node_type") == "format"
    ]

    nx.draw_networkx_nodes(graph, pos, nodelist=course_nodes, node_size=900)
    nx.draw_networkx_nodes(graph, pos, nodelist=category_nodes, node_size=1600)
    nx.draw_networkx_nodes(graph, pos, nodelist=format_nodes, node_size=1400)

    nx.draw_networkx_edges(graph, pos, arrows=True, arrowstyle="->", arrowsize=12)

    labels = {
        node: data.get("label", node)
        for node, data in graph.nodes(data=True)
    }

    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8)

    plt.title("ASU CS Course Knowledge Graph")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE)
    print(f"Graph visualization saved to {OUTPUT_FILE}")


def main():
    courses = load_courses()
    graph = build_graph(courses)
    visualize_graph(graph)


if __name__ == "__main__":
    main()