""" 
This script processes the bulk download data from the Open Library project.
Adapted from: https://github.com/LibrariesHacked/openlibrary-search
"""

import csv
import ctypes as ct
import os
import json

INPUT_PATH = "./data/unprocessed/"
OUTPUT_PATH = "./data/processed/"

filesforprocessing = [
    "ol_dump_editions_2024-07-07.txt",
]

# Example editions data structure
# 
# TYPE          ID             UNKNOWN INTEGER    DATE              JSON
# /type/edition	/books/OL10000346M	3	2011-04-27T19:07:26.894492	{...}

# See https://stackoverflow.com/a/54517228 for more info on this
csv.field_size_limit(int(ct.c_ulong(-1).value // 2))

for file in filesforprocessing:
    with open(os.path.join(OUTPUT_PATH, file), "w", newline="", encoding="utf-8") as csv_out:
        csvwriter = csv.writer(
            csv_out, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        csvwriter.writerow(["ol_id", "title", "isbn", "covers", "json"])

        with open(os.path.join(INPUT_PATH, file), "r", encoding="utf-8") as csv_in:
            csvreader = csv.reader(csv_in, delimiter="\t")
            for row in csvreader:
                if len(row) > 4: # Some rows in the original dataset have an inconsistent number of columns, this ensures that we only save the rows that we know are good and have more 5 columns.
                    data = json.loads(row[4])
                    isbn = "None"
                    covers = "None"
                    title = "None"
                    if "isbn_13" in data:
                        if len(data["isbn_13"]) > 0:
                            isbn = data["isbn_13"][0]
                    
                    if "covers" in data:
                        if len(data["covers"]) == 1:
                            covers = data["covers"][0]
                        elif len(data["covers"]) > 1:
                            covers = str(data["covers"]).replace("[", "").replace("]", "")

                    if "title" in data:
                        title = data["title"]

                    csvwriter.writerow(
                        [row[1].replace("/books/", ""), title, isbn, covers])

