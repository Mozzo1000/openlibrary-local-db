https://sqlite-utils.datasette.io/en/stable/cli.html#creating-indexes

# Insert csv into database
sqlite-utils insert test.db oldata data\processed\ol_dump_editions_2024-07-07.txt --csv --delimiter=";" --quotechar="|"

# Create full text search
sqlite-utils enable-fts test.db oldata title isbn

# Executing search
sqlite-utils search test.db oldata SEARCHTERM -c title -c isbn --limit 5

## Get sql from search
sqlite-utils search test.db oldata SEARCHTERM -c title -c isbn --sql


# Pipeline flow
This should be able to be dockerized, from start to finish.

## Getting ol dump (we only need editions)

## Processing editions file

## Inserting into db
could this be the same step as processing? Yes, we really don't need to be creating a separate csv file before inserting into db.

## Creating FTS

## Optimize database
`sqlite-utils optimize test.db`

## Serve up the search API with Flask