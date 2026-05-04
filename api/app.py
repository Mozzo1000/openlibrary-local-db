from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from dotenv import load_dotenv
import os
from flasgger import Swagger
import json

app = Flask(__name__)
CORS(app)

# Use row_factory to get results as dictionaries automatically
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

app.config['SWAGGER'] = {
  "openapi": "3.0.0",
  "info": {
    "title": "openlibrary-local-db API",
    "description": "API for accessing a dumped version of OpenLibrary",
    "contact": {
      "responsibleDeveloper": "Andreas Backström",
      "url": "https://github.com/mozzo1000/openlibrary-local-db",
    },
    "version": "1.0.0"
  },
    "specs_route": "/api/docs"
}
swagger = Swagger(app)


load_dotenv()
con = sqlite3.connect(os.getenv("OL_DB"), check_same_thread=False)
con.row_factory = dict_factory
cur = con.cursor()

@app.route("/v1/search/<query>")
def search(query):
    """
    Search books with advanced filtering and sorting
    ---
    parameters:
      - name: query
        in: path
        type: string
        required: true
      - name: limit
        in: query
        type: integer
        default: 10
      - name: lang
        in: query
        type: string
        description: Language code (e.g., 'eng')
      - name: sort
        in: query
        type: string
        enum: [relevance, newest, oldest]
        default: relevance
    """
    # 1. Get Parameters
    limit = request.args.get("limit", default=10, type=int)
    lang = request.args.get("lang", type=str)
    sort_mode = request.args.get("sort", default="relevance", type=str)

    words = query.split()
    safe_query = " AND ".join([f'"{word.replace('"', '""')}"' for word in words if word])

    # 2. Build Query Components
    base_sql = """
        SELECT e.title, e.isbn_10, e.isbn_13, e.publish_date, e.author_names, e.languages
        FROM editions e
        JOIN editions_fts f ON e.rowid = f.rowid
        WHERE f.editions_fts MATCH ?
    """
    
    # 2.5 Ensure at least one ISBN is present
    # We check that the JSON array is not empty
    base_sql += " AND (e.isbn_10 != '[]' OR e.isbn_13 != '[]')"

    params = [safe_query]

    # 3. Add Language Filtering
    if lang:
        base_sql += " AND EXISTS (SELECT 1 FROM json_each(e.languages) WHERE value = ?)"
        params.append(lang)

    # 4. Add Sorting Logic
    if sort_mode == "newest":
        base_sql += " ORDER BY e.publish_year DESC"
    elif sort_mode == "oldest":
        # Push year 0 (missing) to the bottom
        base_sql += " ORDER BY e.publish_year = 0, e.publish_year ASC"
    else:
        base_sql += """ 
            ORDER BY (
                f.rank - (CASE WHEN json_array_length(e.author_names) > 0 THEN 0.5 ELSE 0 END)
            ) DESC
        """

    # 5. Add Limit
    base_sql += " LIMIT ?"
    params.append(limit)

    # 6. Execute and Return
    try:
        results = cur.execute(base_sql, params).fetchall()
        if results:
            for row in results:
                json_fields = ['author_names', 'languages', 'isbn_13', 'isbn_10']
                for field in json_fields:
                    if isinstance(row.get(field), str):
                        try:
                            row[field] = json.loads(row[field])
                        except json.JSONDecodeError:
                            row[field] = [] # Fallback if data is corrupted
            return jsonify(results)
        return jsonify({"message": "Not found"}), 404
    except sqlite3.OperationalError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/v1/edition/<identifier>")
def get_edition(identifier):
    """
    Get full details of a specific edition by OLID, ISBN-10, or ISBN-13
    ---
    parameters:
      - name: identifier
        in: path
        type: string
        required: true
        description: The Open Library ID (e.g., OL27348000M) or an ISBN string.
    responses:
      200:
        description: Edition details found.
      404:
        description: Edition not found.
    """
    # We use json() functions here so the API returns clean arrays/objects 
    # instead of strings with backslashes.
    sql = """
        SELECT 
            ol_id, title, subtitle, publish_date, publish_year,
            number_of_pages, physical_format,
            json(publishers) as publishers,
            json(isbn_10) as isbn_10,
            json(isbn_13) as isbn_13,
            json(subjects) as subjects,
            json(languages) as languages,
            json(authors) as author_ids,
            json(author_names) as author_names,
            json(works) as work_ids
        FROM editions
        WHERE ol_id = ? 
           OR EXISTS (SELECT 1 FROM json_each(isbn_10) WHERE value = ?)
           OR EXISTS (SELECT 1 FROM json_each(isbn_13) WHERE value = ?)
        LIMIT 1
    """
    
    # We pass the identifier three times to cover all three columns
    result = cur.execute(sql, (identifier, identifier, identifier)).fetchone()

    if result:
        return jsonify(result)
    
    return jsonify({"message": f"Edition {identifier} not found"}), 404

@app.route("/v1/work/<ol_id>")
def get_work(ol_id):
    """
    Get full details of a work by OLID
    ---
    parameters:
      - name: ol_id
        in: path
        type: string
        required: true
        description: The Open Library Work ID (e.g., OL17352669W)
    """
    sql = """
        SELECT 
            ol_id, title, description,
            json(authors) as authors,
            json(subjects) as subjects,
            json(subject_people) as subject_people,
            json(subject_places) as subject_places,
            json(covers) as covers,
            json(series) as series
        FROM works
        WHERE ol_id = ?
        LIMIT 1
    """
    # Strip the prefix if the user includes it by accident
    clean_id = ol_id.replace("/works/", "")
    result = cur.execute(sql, (clean_id,)).fetchone()

    if result:
        return jsonify(result)
    return jsonify({"message": f"Work {ol_id} not found"}), 404


@app.route("/v1/author/<ol_id>")
def get_author(ol_id):
    """
    Get full details of an author by OLID
    ---
    parameters:
      - name: ol_id
        in: path
        type: string
        required: true
        description: The Open Library Author ID (e.g., OL7115219A)
    """
    sql = """
        SELECT 
            ol_id, name, birth_date, death_date, bio,
            json(alternate_names) as alternate_names,
            json(photos) as photos
        FROM authors
        WHERE ol_id = ?
        LIMIT 1
    """
    # Strip the prefix if the user includes it by accident
    clean_id = ol_id.replace("/authors/", "")
    result = cur.execute(sql, (clean_id,)).fetchone()

    if result:
        return jsonify(result)
    return jsonify({"message": f"Author {ol_id} not found"}), 404

@app.route("/")
def index():
    return {
        "name": "openlibrary-local-db-api",
        "version": "1.0.0",
        "docs": request.base_url + "docs",
        "oldump_date": os.getenv("OLDUMP_DATE")
    }