import os
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text

app = Flask(__name__)

DB_URL = os.environ["DATABASE_URL"]
engine = create_engine(DB_URL, pool_pre_ping=True)

@app.get("/health")
def health():
    return{"status": "ok"}

@app.get("/print")
def test_print():
    return{"output": "output"}


@app.get("/notes")
def get_notes():
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, body, created_at FROM notes ORDER BY id DESC")
        ).mappings().all()

    return jsonify([dict(r) for r in rows])

@app.post("/notes")
def add_note():
    data = request.get_json(force=True)
    body = data.get("body", "").strip()
    if not body:
        return{"error": "body is required"}, 400
    
    with engine.begin() as conn:
        row = conn.execute(
            text("INSERT INTO notes (body) VALUES (:body) RETURNING id, body, created_at"),
            {"body": body},
        ).mappings().one()
    return jsonify(dict(row)), 201