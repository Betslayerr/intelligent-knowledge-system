import json
from pathlib import Path

import networkx as nx


INPUT_FILE = Path("data/processed/asu_cs_courses.json")
OUTPUT_FILE = Path("data/output/query_results.json")


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

    if any(word in title_lower for word in [
        "security",
        "cryptography"
    ]):
        return "Cybersecurity"

    if any(word in title_lower for word in [
        "database",
        "data science"
    ]):
        return "Data/Database"

    if any(word in title_lower for word in [
        "linux",
        "network",
        "architecture",
        "host",
        "device"
    ]):
        return "Systems"

    if any(word in title_lower for word in [
        "programming",
        "computer science i",
        "computer science ii",
        "data structures"
    ]):
        return "Programming/Foundation"

    if any(word in title_lower for word in [
        "research",
        "internship",
        "senior design",
        "thesis"
    ]):
        return "Research/Capstone"

    return "Other"


def build_graph(courses):
    graph = nx.DiGraph()

    for course in courses:
        course_code = course["course_code"]
        title = course["title"]
        credits = course["credits"]
        category = categorize_course(title)

        graph.add_node(
            course_code,
            node_type="course",
            title=title,
            credits=credits,
            category=category
        )

        graph.add_node(category, node_type="category")
        graph.add_edge(course_code, category, relation="belongs_to_category")

        for fmt in course.get("formats", []):
            graph.add_node(fmt, node_type="format")
            graph.add_edge(course_code, fmt, relation="offered_as")

    return graph


def list_courses(graph):
    results = []

    for node, data in graph.nodes(data=True):
        if data.get("node_type") == "course":
            results.append({
                "course_code": node,
                "title": data.get("title"),
                "credits": data.get("credits"),
                "category": data.get("category")
            })

    return sorted(results, key=lambda item: item["course_code"])


def search_courses(graph, keyword):
    keyword = keyword.lower()
    results = []

    for node, data in graph.nodes(data=True):
        if data.get("node_type") == "course":
            title = data.get("title", "").lower()
            course_code = node.lower()

            if keyword in title or keyword in course_code:
                results.append({
                    "course_code": node,
                    "title": data.get("title"),
                    "category": data.get("category")
                })

    return sorted(results, key=lambda item: item["course_code"])


def filter_by_format(graph, target_format):
    results = []

    for node, data in graph.nodes(data=True):
        if data.get("node_type") == "course":
            for neighbor in graph.neighbors(node):
                edge_data = graph.edges[node, neighbor]

                if edge_data.get("relation") == "offered_as" and neighbor.lower() == target_format.lower():
                    results.append({
                        "course_code": node,
                        "title": data.get("title"),
                        "format": neighbor
                    })

    return sorted(results, key=lambda item: item["course_code"])


def filter_by_category(graph, category):
    results = []

    for node, data in graph.nodes(data=True):
        if data.get("node_type") == "course":
            if data.get("category", "").lower() == category.lower():
                results.append({
                    "course_code": node,
                    "title": data.get("title"),
                    "category": data.get("category")
                })

    return sorted(results, key=lambda item: item["course_code"])


def get_course_details(graph, course_code):
    course_code = course_code.upper().strip()

    if course_code not in graph:
        return {"error": f"{course_code} not found"}

    data = graph.nodes[course_code]

    relationships = []
    for neighbor in graph.neighbors(course_code):
        relationships.append({
            "target": neighbor,
            "relation": graph.edges[course_code, neighbor].get("relation")
        })

    return {
        "course_code": course_code,
        "title": data.get("title"),
        "credits": data.get("credits"),
        "category": data.get("category"),
        "relationships": relationships
    }


def save_results(results):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print(f"\nSaved latest query result to {OUTPUT_FILE}")


def print_json(data):
    print(json.dumps(data, indent=2))


def show_help():
    print("""
Available commands:

  list
    Show all courses.

  search <keyword>
    Search courses by title or course code.
    Example: search machine

  format <Online Course | Face to Face>
    Filter courses by delivery format.
    Example: format Online Course

  category <category name>
    Filter courses by category.
    Example: category AI/ML
    Example: category Cybersecurity

  details <course code>
    Show detailed graph relationships for one course.
    Example: details CS 3311

  summary
    Show graph node and edge count.

  help
    Show this help menu.

  exit
    Quit the program.
""")


def interactive_loop(graph):
    print("\nASU CS Knowledge Graph Interactive Query Tool")
    print("Type 'help' to see available commands.")
    print("Type 'exit' to quit.\n")

    while True:
        command = input("query> ").strip()

        if not command:
            continue

        if command.lower() == "exit":
            print("Goodbye.")
            break

        if command.lower() == "help":
            show_help()
            continue

        if command.lower() == "list":
            result = {
                "query_type": "list_courses",
                "results": list_courses(graph)
            }
            print_json(result)
            save_results(result)
            continue

        if command.lower() == "summary":
            result = {
                "query_type": "graph_summary",
                "nodes": graph.number_of_nodes(),
                "edges": graph.number_of_edges()
            }
            print_json(result)
            save_results(result)
            continue

        if command.lower().startswith("search "):
            keyword = command[7:].strip()
            result = {
                "query_type": "search",
                "keyword": keyword,
                "results": search_courses(graph, keyword)
            }
            print_json(result)
            save_results(result)
            continue

        if command.lower().startswith("format "):
            target_format = command[7:].strip()
            result = {
                "query_type": "filter_by_format",
                "format": target_format,
                "results": filter_by_format(graph, target_format)
            }
            print_json(result)
            save_results(result)
            continue

        if command.lower().startswith("category "):
            category = command[9:].strip()
            result = {
                "query_type": "filter_by_category",
                "category": category,
                "results": filter_by_category(graph, category)
            }
            print_json(result)
            save_results(result)
            continue

        if command.lower().startswith("details "):
            course_code = command[8:].strip()
            result = {
                "query_type": "course_details",
                "course_code": course_code,
                "result": get_course_details(graph, course_code)
            }
            print_json(result)
            save_results(result)
            continue

        print("Unknown command. Type 'help' to see available commands.")


def main():
    courses = load_courses()
    graph = build_graph(courses)
    interactive_loop(graph)


if __name__ == "__main__":
    main()