from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel
import psycopg2
import os
import json

class EmptyInput(BaseModel):
    pass

class PostgresSchemaTool(BaseTool):
    name: str = "Postgres Schema Fetcher"
    description: str = (
        "Fetches schema, table names, and column metadata from a local Postgres database."
    )
    args_schema: Type[BaseModel] = EmptyInput

    def _run(self) -> str:
        conn = psycopg2.connect(
            dbname=os.getenv('PGDATABASE', 'postgres'),
            user=os.getenv('PGUSER', 'postgres'),
            password=os.getenv('PGPASSWORD', ''),
            host=os.getenv('PGHOST', 'localhost'),
            port=os.getenv('PGPORT', '5432'),
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT table_schema, table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name, ordinal_position;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Structure as dict: {schema: {table: [columns...]}}
        schema = {}
        for sch, tbl, col, typ in rows:
            schema.setdefault(sch, {}).setdefault(tbl, []).append({"column": col, "type": typ})
        return json.dumps(schema, indent=2) 