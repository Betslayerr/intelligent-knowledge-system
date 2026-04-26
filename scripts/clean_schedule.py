import json
import re
from pathlib import Path


RAW_FILE = Path("data/raw/asu_cs_schedule_2026_fall.txt")
OUTPUT_FILE = Path("data/processed/asu_cs_courses.json")


def parse_courses(text: str):
    """
    Extract unique CS courses from pasted ASU schedule text.
    We look for patterns like:
    CS 2336 010 Face to Face 3 Data Structures and Algorithms
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    courses = {}
    
    pattern = re.compile(
        r"^\d+\s+CS\s+(\d{4})\s+([A-Z0-9]+)\s+(.+?)\s+(\d)\s+(.+?)\s+(FULL:|[0-9]+ of|None|Time Conflict!)"
    )

    for line in lines:
        match = pattern.search(line)
        if match:
            course_number = match.group(1)
            section = match.group(2)
            format_type = match.group(3).strip()
            credits = match.group(4)
            title = match.group(5).strip()
            title = title.split("\t")[0].strip()
            title = title.replace("\u00a0", " ")

            course_code = f"CS {course_number}"

            if course_code not in courses:
                courses[course_code] = {
                    "course_code": course_code,
                    "title": title,
                    "credits": int(credits),
                    "formats": set(),
                    "sections": []
                }

            courses[course_code]["formats"].add(format_type)
            courses[course_code]["sections"].append(section)

    # convert sets to sorted lists
    cleaned = []
    for course in courses.values():
        course["formats"] = sorted(course["formats"])
        course["sections"] = sorted(course["sections"])
        cleaned.append(course)

    cleaned.sort(key=lambda x: x["course_code"])
    return cleaned


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Raw file not found: {RAW_FILE}")

    text = RAW_FILE.read_text(encoding="utf-8")
    cleaned_courses = parse_courses(text)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(cleaned_courses, indent=2), encoding="utf-8")

    print(f"Saved {len(cleaned_courses)} unique courses to {OUTPUT_FILE}")
    for course in cleaned_courses[:10]:
        print(course)


if __name__ == "__main__":
    main()