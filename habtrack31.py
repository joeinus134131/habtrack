import sys
import sqlite3
import os
import platform
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QListWidget, QTimeEdit, QMessageBox, QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import QAction 
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer, QTime

# Struktur Folder
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
    conn.commit()
    conn.close()

class HabitTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        create_db()
        self.load_habits()
        self.check_reminders()
        self.init_tray_icon()
    
    def initUI(self):
        self.setWindowTitle("Habit Tracker")
        self.setGeometry(100, 100, 400, 400)
        layout = QVBoxLayout()
        
        self.habit_input = QLineEdit(self)
        self.habit_input.setPlaceholderText("Nama Habit")
        layout.addWidget(self.habit_input)
        
        self.time_input = QTimeEdit(self)
        layout.addWidget(self.time_input)
        
        self.add_button = QPushButton("Tambah Habit", self)
        self.add_button.clicked.connect(self.add_habit)
        layout.addWidget(self.add_button)
        
        self.habit_list = QListWidget(self)
        layout.addWidget(self.habit_list)
        
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
    
    def load_habits(self):
        self.habit_list.clear()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, remind_time FROM habits")
        habits = cursor.fetchall()
        conn.close()
        for habit in habits:
            self.habit_list.addItem(f"{habit[0]} - {habit[1]}")
    
    def check_reminders(self):
        timer = QTimer(self)
        timer.timeout.connect(self.show_reminder)
        timer.start(60000)  # Cek setiap menit
    
    def show_reminder(self):
        current_time = QTime.currentTime().toString("HH:mm")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM habits WHERE remind_time = ?", (current_time,))
        habits = cursor.fetchall()
        conn.close()

        for habit in habits:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Habit Reminder")
            msg_box.setText(f"Saatnya untuk: {habit[0]}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            # Jika user klik "OK", maka aplikasi akan terbuka
            if msg_box.exec() == QMessageBox.StandardButton.Ok:
                self.showNormal()  # Membuka kembali aplikasi
                self.raise_()      # Membawa jendela ke depan
                self.activateWindow()  # Fokus ke aplikasi

    
    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))
        
        menu = QMenu()
        restore_action = QAction("Buka Habit Tracker", self)
        restore_action.triggered.connect(self.show)
        menu.addAction(restore_action)
        
        exit_action = QAction("Keluar", self)
        exit_action.triggered.connect(self.close_app)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.tray_icon_clicked)
        self.tray_icon.show()
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("Habit Tracker", "Aplikasi berjalan di latar belakang", QSystemTrayIcon.MessageIcon.Information, 2000)
    
    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()
    
    def close_app(self):
        self.tray_icon.hide()
        QApplication.quit()

def schedule_task():
    if platform.system() == "Windows":
        os.system("schtasks /create /sc daily /tn HabitTracker /tr %cd%\\HabitTracker.exe /st 08:00")
    else:
        os.system("(crontab -l; echo '0 8 * * * python3 {}/habit_tracker.py') | crontab -".format(BASE_DIR))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HabitTrackerApp()
    window.show()
    sys.exit(app.exec())