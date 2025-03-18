from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, 
    QLabel, QCalendarWidget, QTimeEdit, QMessageBox, QFileDialog, 
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QInputDialog,
    QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import QPixmap, QTextCharFormat, QColor, QAction, QIcon
from PyQt6.QtCore import QTimer
from database.db_manager import init_db, fetch_habits, add_habit
from ui.dialogs import HabitDialog

class HabitTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUi()
        init_db()
        self.load_habits()

    def initUi(self):
        self.setWindowTitle("Habit Tracker")
        self.setGeometry(100, 100, 400, 500)
        
        # Layout
        layout = QVBoxLayout()
        
        # Kalender
        self.calendar = QCalendarWidget(self)
        layout.addWidget(self.calendar)

        # Daftar Habit
        self.habit_list = QListWidget(self)
        layout.addWidget(self.habit_list)

        # Tombol Tambah Habit
        self.add_button = QPushButton("Tambah Habit", self)
        self.add_button.clicked.connect(self.add_habit)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def load_habits(self):
        """Memuat daftar habit dari database"""
        self.habit_list.clear()
        habits = fetch_habits()
        for habit in habits:
            self.habit_list.addItem(f"{habit[0]} - {habit[1]} - {habit[2]}")

    def add_habit(self):
        """Menambahkan habit baru"""
        dialog = HabitDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            habit_name, remind_time, description = dialog.get_data()
            add_habit(habit_name, remind_time, description)
            self.load_habits()