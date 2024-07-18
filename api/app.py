from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)
load_dotenv()
con = sqlite3.connect(os.getenv("OL_DB"), check_same_thread=False)
cur = con.cursor()

@app.route("/v1/search/<query>")
def search(query):
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
        "name": "openlibrary-qnk-search-api",
        "version": "1.0.0"
    }