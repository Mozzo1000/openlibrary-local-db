import csv
import ctypes as ct
import os
import json

INPUT_PATH = "./data/unprocessed/"
OUTPUT_PATH = "./data/processed/"

processing_tasks = {
    "ol_dump_editions_2026-03-31.txt": [
        "ol_id", "title", "subtitle", "publish_date", "number_of_pages", 
        "physical_format", "publishers", "isbn_10", "isbn_13", 
        "subjects", "languages", "authors"
    ],
    "ol_dump_authors_2026-03-31.txt": [
        "ol_id", "name", "birth_date", "death_date", "alternate_names", "bio", "photos"
    ]
}

csv.field_size_limit(int(ct.c_ulong(-1).value // 2))

def format_list(data_list):
    """Returns None string if list is empty, else returns JSON string."""
    if not data_list or len(data_list) == 0:
        return "None"
    return json.dumps(data_list)

for filename, fieldnames in processing_tasks.items():
    input_file = os.path.join(INPUT_PATH, filename)
    output_file = os.path.join(OUTPUT_PATH, filename.replace(".txt", ".csv"))
    
    if not os.path.exists(input_file):
        continue

    with open(output_file, "w", newline="", encoding="utf-8") as csv_out:
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames, delimiter=";", quotechar="|")
        writer.writeheader()

        with open(input_file, "r", encoding="utf-8") as csv_in:
            reader = csv.reader(csv_in, delimiter="\t")
            
            for row in reader:
                if len(row) > 4:
                    try:
                        data = json.loads(row[4])
                        out_row = {}

                        if "editions" in filename:
                            out_row = {
                                "ol_id": row[1].replace("/books/", ""),
                                "title": data.get("title", "None"),
                                "subtitle": data.get("subtitle", "None"),
                                "publish_date": data.get("publish_date", "None"),
                                "number_of_pages": data.get("number_of_pages", "None"),
                                "physical_format": data.get("physical_format", "None"),
                                "publishers": format_list(data.get("publishers")),
                                "isbn_10": format_list(data.get("isbn_10")),
                                "isbn_13": format_list(data.get("isbn_13")),
                                "subjects": format_list(data.get("subjects")),
                                # Cleaned languages and authors prefixes
                                "languages": format_list([l.get("key", "").replace("/languages/", "") for l in data.get("languages", []) if isinstance(l, dict) and l.get("key")]),
                                "authors": format_list([a.get("key", "").replace("/authors/", "") for a in data.get("authors", []) if isinstance(a, dict) and a.get("key")])
                            }

                        elif "authors" in filename:
                            bio_data = data.get("bio", "")
                            bio_text = bio_data.get("value", "") if isinstance(bio_data, dict) else bio_data

                            out_row = {
                                "ol_id": row[1].replace("/authors/", ""),
                                "name": data.get("name", "None"),
                                "birth_date": data.get("birth_date", "None"),
                                "death_date": data.get("death_date", "None"),
                                "alternate_names": format_list(data.get("alternate_names")),
                                "bio": bio_text if bio_text else "None",
                                "photos": format_list(data.get("photos"))
                            }

                        writer.writerow(out_row)
                    except (json.JSONDecodeError, TypeError):
                        continue