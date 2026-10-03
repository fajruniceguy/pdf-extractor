"""Postgres connection with pgvector types registered."""
from __future__ import annotations

import os

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector


def connect() -> psycopg.Connection:
    load_dotenv()
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set (see .env.example)")
    conn = psycopg.connect(url, autocommit=True)
    register_vector(conn)
    return conn
