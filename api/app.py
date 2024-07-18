from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from dotenv import load_dotenv
import os
from flasgger import Swagger

app = Flask(__name__)
CORS(app)

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
cur = con.cursor()

@app.route("/v1/search/<query>")
def search(query):
    """
        Search books by title or isbn
        ---
        parameters:
            - name: query
              in: path
              type: string
              required: true
        responses:
          200:
            description: Results found, returning title and isbn.

          404:
            description: No results found.


    """

    limit = request.args.get("limit", default=10, type=int)

    sql_search ="""
        with original as (
            select
                rowid,
                [title],
                [isbn]
            from [oldata]
        )
        select
            [original].[title],
            [original].[isbn]
        from
            [original]
            join [oldata_fts] on [original].rowid = [oldata_fts].rowid
        where
            [oldata_fts] match ?
        order by
            [oldata_fts].rank
        limit ?
        """
    results = cur.execute(sql_search, (query,limit,)).fetchall()
    if results:
        json_output = []
        for i in results:
            json_output.append({"title": i[0], "isbn": i[1]})

        return json_output
    else:
        return jsonify({"message": "Not found"}), 404


@app.route("/")
def index():
    return {
        "name": "openlibrary-local-db-api",
        "version": "1.0.0",
        "docs": request.base_url + "docs",
        "oldump_date": os.getenv("OLDUMP_DATE")
    }