import sys
import sqlite3
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QListWidget, QTimeEdit, QMessageBox, QCalendarWidget
)
from PyQt6.QtCore import QDate, Qt

# Struktur Folder dan Database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "data", "habits.db")

def create_db():
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            remind_time TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_name TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

class HabitTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        create_db()
        self.load_habits()
        self.load_completed_habits()

    def initUI(self):
        self.setWindowTitle("Habit Tracker")
        self.setGeometry(100, 100, 500, 500)
        layout = QVBoxLayout()

        # Input Habit
        self.habit_input = QLineEdit(self)
        self.habit_input.setPlaceholderText("Nama Habit")
        layout.addWidget(self.habit_input)

        # Input Waktu Pengingat
        self.time_input = QTimeEdit(self)
        layout.addWidget(self.time_input)

        # Tombol Tambah Habit
        self.add_button = QPushButton("Tambah Habit", self)
        self.add_button.clicked.connect(self.add_habit)
        layout.addWidget(self.add_button)

        # List Habit
        self.habit_list = QListWidget(self)
        layout.addWidget(self.habit_list)

        # Tombol "Selesai" untuk menandai habit
        self.complete_button = QPushButton("Selesai", self)
        self.complete_button.clicked.connect(self.mark_completed)
        layout.addWidget(self.complete_button)

        # **Tampilan Kalender**
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.load_completed_habits)
        layout.addWidget(self.calendar)

        self.setLayout(layout)

    def add_habit(self):
        habit = self.habit_input.text().strip()
        remind_time = self.time_input.time().toString("HH:mm")
        if habit:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO habits (name, remind_time) VALUES (?, ?)", (habit, remind_time))
            conn.commit()
            conn.close()
            self.habit_list.addItem(f"{habit} - {remind_time}")
            self.habit_input.clear()
        else:
            QMessageBox.warning(self, "Input Error", "Nama habit tidak boleh kosong!")

    def mark_completed(self):
        selected_item = self.habit_list.currentItem()
        if selected_item:
            habit_name = selected_item.text().split(" - ")[0]  # Ambil nama habit
            date = self.calendar.selectedDate().toString("yyyy-MM-dd")  # Ambil tanggal dipilih user
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO habit_log (habit_name, date) VALUES (?, ?)", (habit_name, date))
            conn.commit()
            conn.close()
            self.load_completed_habits()
        else:
            QMessageBox.warning(self, "Input Error", "Pilih habit yang ingin ditandai selesai!")

    def load_habits(self):
        self.habit_list.clear()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, remind_time FROM habits")
        habits = cursor.fetchall()
        conn.close()
        for habit in habits:
            self.habit_list.addItem(f"{habit[0]} - {habit[1]}")

    def load_completed_habits(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT date FROM habit_log")
        completed_dates = cursor.fetchall()
        conn.close()

        for date in completed_dates:
            date_obj = QDate.fromString(date[0], "yyyy-MM-dd")
            self.calendar.setDateTextFormat(date_obj, self.get_checklist_format())

    def get_checklist_format(self):
        from PyQt6.QtGui import QTextCharFormat
        fmt = QTextCharFormat()
        fmt.setFontWeight(75)  # Bold
        fmt.setForeground(Qt.GlobalColor.blue)  # Warna biru
        fmt.setToolTip("Habit selesai")
        return fmt

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HabitTrackerApp()
    window.show()
    sys.exit(app.exec())
