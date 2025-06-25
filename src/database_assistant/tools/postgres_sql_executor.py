from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import psycopg2
import os
import re

class PostgresSQLExecutorInput(BaseModel):
    query: str = Field(..., description="SQL query to execute.")
    confirm_update: bool = Field(False, description="Set True to allow UPDATE queries.")
    allow_dangerous: bool = Field(False, description="Set True to allow DROP/DELETE queries (not recommended).")

class PostgresSQLExecutor(BaseTool):
    name: str = "Postgres SQL Executor"
    description: str = (
        "Executes safe SQL queries (SELECT by default, UPDATE with confirmation, DROP/DELETE only if explicitly allowed) on local Postgres."
    )
    args_schema: Type[BaseModel] = PostgresSQLExecutorInput

    def _run(self, query: str, confirm_update: bool = False, allow_dangerous: bool = False) -> str:
        q = query.strip().lower()
        if q.startswith('select'):
            pass
        elif q.startswith('update'):
            if not confirm_update:
                return "UPDATE queries require confirm_update=True."
        elif q.startswith('drop') or q.startswith('delete'):
            if not allow_dangerous:
                return "DROP/DELETE queries are not allowed unless allow_dangerous=True."
        else:
            return "Only SELECT, UPDATE, DROP, and DELETE queries are supported."
        try:
            conn = psycopg2.connect(
                dbname=os.getenv('PGDATABASE', 'postgres'),
                user=os.getenv('PGUSER', 'postgres'),
                password=os.getenv('PGPASSWORD', ''),
                host=os.getenv('PGHOST', 'localhost'),
                port=os.getenv('PGPORT', '5432'),
            )
            cur = conn.cursor()
            cur.execute(query)
            if q.startswith('select'):
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                result = [dict(zip(columns, row)) for row in rows]
            else:
                conn.commit()
                result = f"Query executed: {cur.rowcount} rows affected."
            cur.close()
            conn.close()
            return result
        except Exception as e:
            return f"SQL execution error: {e}" 