import sqlite3
import os
import datetime

DB_NAME = "notes.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS documents
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  filename TEXT,
                  filepath TEXT,
                  upload_date TIMESTAMP)''')
    conn.commit()
    conn.close()

def add_document(filename, filepath):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO documents (filename, filepath, upload_date) VALUES (?, ?, ?)",
              (filename, filepath, datetime.datetime.now()))
    conn.commit()
    conn.close()

def get_documents():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, filename, filepath, upload_date FROM documents")
    docs = c.fetchall()
    conn.close()
    return docs

def delete_document(doc_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT filepath FROM documents WHERE id=?", (doc_id,))
    result = c.fetchone()
    if result:
        filepath = result[0]
        if os.path.exists(filepath):
            os.remove(filepath)
    c.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()

def clear_all_documents():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT filepath FROM documents")
    results = c.fetchall()
    for result in results:
        filepath = result[0]
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass
    c.execute("DELETE FROM documents")
    conn.commit()
    conn.close()
