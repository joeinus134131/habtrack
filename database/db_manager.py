import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "..", "data", "habits.db")

def init_db():
    """Inisialisasi Database"""
    os.makedirs(os.path.join(BASE_DIR, "..", "data"), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        remind_time TEXT NOT NULL,
                        description TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS habit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        habit_name TEXT NOT NULL,
                        date TEXT NOT NULL,
                        evidence TEXT)''')
    conn.commit()
    conn.close()

def fetch_habits():
    """Mengambil semua habit dari database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, remind_time, description FROM habits")
    habits = cursor.fetchall()
    conn.close()
    return habits

def add_habit(name, remind_time, description):
    """Menambahkan habit baru ke database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (name, remind_time, description) VALUES (?, ?, ?)", 
                   (name, remind_time, description))
    conn.commit()
    conn.close()

# Tambahkan fungsi lain seperti `delete_habit`, `update_habit`, dll.