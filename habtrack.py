import sys
import os
import sqlite3
import datetime
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, 
    QLabel, QCalendarWidget, QTimeEdit, QMessageBox, QFileDialog
)
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtGui import QPixmap, QTextCharFormat, QColor
from PyQt6.QtCore import QTimer, QTime
from plyer import notification

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "habits.db")

class HabitTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
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

        self.edit_button = QPushButton("Edit Habit", self)
        self.edit_button.clicked.connect(self.edit_habit)
        layout.addWidget(self.edit_button)

        # Tombol Hapus Habit
        self.delete_button = QPushButton("Hapus Habit", self)
        self.delete_button.clicked.connect(self.delete_habit)
        layout.addWidget(self.delete_button)
        
        # Tombol Tambah Habit
        self.add_button = QPushButton("Tambah Habit", self)
        self.add_button.clicked.connect(self.add_habit)
        layout.addWidget(self.add_button)

        # Tombol Upload Screenshot
        self.upload_button = QPushButton("Upload Bukti (Screenshot)", self)
        self.upload_button.clicked.connect(self.upload_screenshot)
        layout.addWidget(self.upload_button)

        self.setLayout(layout)
        
        # Load data awal
        self.init_db()
        self.load_habits()
        self.load_completed_habits()

        # Timer untuk Reminder (Cek setiap menit)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(60000)  # Cek tiap 60 detik
        self.start_scheduler()

    def start_scheduler(self):
        """Menjalankan scheduler untuk reminder di latar belakang"""
        def run_reminder():
            while True:
                self.check_reminders()
                threading.Event().wait(60)  # Cek setiap 60 detik

        reminder_thread = threading.Thread(target=run_reminder, daemon=True)
        reminder_thread.start()

    def init_db(self):
        """Inisialisasi Database"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            remind_time TEXT NOT NULL,
                            description TEXT)''')  # Tambahkan kolom deskripsi
        cursor.execute('''CREATE TABLE IF NOT EXISTS habit_log (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            habit_name TEXT NOT NULL,
                            date TEXT NOT NULL,
                            evidence TEXT)''')
        conn.commit()
        conn.close()

    def load_habits(self):
        """Memuat daftar habit dari database"""
        self.habit_list.clear()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, remind_time, description FROM habits")
        habits = cursor.fetchall()
        for habit in habits:
            self.habit_list.addItem(f"{habit[0]} - {habit[1]} - {habit[2]}")  # Tampilkan deskripsi
        conn.close()

    def add_habit(self):
        """Menambahkan habit baru"""
        dialog = HabitDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            habit_name, remind_time, description = dialog.get_data()

            # Validasi input
            if not habit_name or not remind_time or not description:
                QMessageBox.warning(self, "Error", "Semua field harus diisi!")
                return

            if not dialog.validate_time():
                QMessageBox.warning(self, "Error", "Format waktu harus HH:MM (24-hour format)!")
                return

            # Simpan ke database
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO habits (name, remind_time, description) VALUES (?, ?, ?)", 
                        (habit_name, remind_time, description))
            conn.commit()
            conn.close()
            self.load_habits()
            self.mark_completed_days()  # Tambahkan ini

    def edit_habit(self):
        """Mengedit habit yang dipilih"""
        selected_item = self.habit_list.currentItem()
        if selected_item:
            habit_name = selected_item.text().split(" - ")[0]
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT remind_time, description FROM habits WHERE name = ?", (habit_name,))
            habit = cursor.fetchone()
            conn.close()

            if habit:
                dialog = HabitDialog(self, habit_name, habit[0], habit[1])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    new_name, new_remind_time, new_description = dialog.get_data()

                    # Validasi input
                    if not new_name or not new_remind_time or not new_description:
                        QMessageBox.warning(self, "Error", "Semua field harus diisi!")
                        return

                    if not dialog.validate_time():
                        QMessageBox.warning(self, "Error", "Format waktu harus HH:MM (24-hour format)!")
                        return

                    # Update database
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE habits SET name = ?, remind_time = ?, description = ? WHERE name = ?", 
                                   (new_name, new_remind_time, new_description, habit_name))
                    conn.commit()
                    conn.close()
                    self.load_habits()
        else:
            QMessageBox.warning(self, "Error", "Pilih habit yang ingin diedit!")

    def delete_habit(self):
        """Menghapus habit yang dipilih"""
        selected_item = self.habit_list.currentItem()
        if selected_item:
            habit_name = selected_item.text().split(" - ")[0]
            confirm = QMessageBox.question(
                self,
                "Konfirmasi",
                f"Apakah Anda yakin ingin menghapus habit '{habit_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM habits WHERE name = ?", (habit_name,))
                conn.commit()
                conn.close()
                self.load_habits()
        else:
            QMessageBox.warning(self, "Error", "Pilih habit yang ingin dihapus!")


    def mark_completed_days(self):
        """Menandai hari di kalender dengan highlight hijau jika semua habit selesai"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Ambil semua tanggal di mana semua habit selesai dengan bukti screenshot
        cursor.execute("""
            SELECT date
            FROM habit_log
            WHERE evidence IS NOT NULL
            GROUP BY date
            HAVING COUNT(DISTINCT habit_name) = (SELECT COUNT(*) FROM habits)
        """)
        completed_dates = cursor.fetchall()
        conn.close()

        # Format untuk highlight hijau
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("lightgreen"))

        # Tandai tanggal di kalender
        for date in completed_dates:
            date_obj = datetime.datetime.strptime(date[0], "%Y-%m-%d").date()
            self.calendar.setDateTextFormat(date_obj, highlight_format)

    def check_reminders(self):
        """Memeriksa dan menampilkan notifikasi reminder"""
        now = datetime.datetime.now().strftime("%H:%M")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM habits WHERE remind_time = ?", (now,))
        habits = cursor.fetchall()
        conn.close()

        for habit in habits:
            habit_name = habit[0]
            notification.notify(
                title="Habit Reminder",
                message=f"Waktunya melakukan: {habit_name}",
                timeout=10,
                app_name="Habit Tracker",
                app_icon=None  # Tambahkan ikon aplikasi jika ada
            )

            # Simpan habit yang diingatkan untuk digunakan saat notifikasi diklik
            self.open_and_prompt_upload(habit_name)

    def open_and_prompt_upload(self, habit_name):
        """Membuka aplikasi dan meminta pengguna mengunggah bukti untuk habit tertentu"""
        self.show()  # Membuka jendela aplikasi jika diminimalkan
        self.raise_()  # Membawa jendela ke depan
        self.activateWindow()  # Mengaktifkan jendela aplikasi

        # Pilih habit di daftar
        items = self.habit_list.findItems(habit_name, Qt.MatchFlag.MatchStartsWith)
        if items:
            self.habit_list.setCurrentItem(items[0])
            QMessageBox.information(
                self,
                "Upload Bukti",
                f"Silakan unggah bukti untuk habit '{habit_name}' agar dianggap selesai."
            )
        else:
            QMessageBox.warning(self, "Error", f"Habit '{habit_name}' tidak ditemukan!")

    def upload_screenshot(self):
        """Mengunggah bukti screenshot sebelum habit dianggap selesai"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih Screenshot", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            selected_item = self.habit_list.currentItem()
            if selected_item:
                habit_name = selected_item.text().split(" - ")[0]
                date = self.calendar.selectedDate().toString("yyyy-MM-dd")

                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO habit_log (habit_name, date, evidence) VALUES (?, ?, ?)", 
                               (habit_name, date, file_path))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Success", "Bukti berhasil diunggah dan habit ditandai selesai!")
                self.load_completed_habits()
            else:
                QMessageBox.warning(self, "Error", "Pilih habit sebelum mengunggah bukti!")

    def load_completed_habits(self):
        """Menampilkan habit yang sudah selesai di kalender"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT habit_name, date FROM habit_log WHERE evidence IS NOT NULL")
        completed_habits = cursor.fetchall()
        conn.close()

        for habit_name, date in completed_habits:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            fmt_date = date_obj.strftime("%d %b %Y")
            self.habit_list.addItem(f"✅ {habit_name} - {fmt_date}")

class HabitDialog(QDialog):
    """Dialog untuk menambahkan atau mengedit habit"""
    def __init__(self, parent=None, habit_name="", remind_time="", description=""):
        super().__init__(parent)
        self.setWindowTitle("Habit Details")
        self.setModal(True)

        # Layout form
        layout = QFormLayout(self)

        # Input fields
        self.name_input = QLineEdit(self)
        self.name_input.setText(habit_name)
        layout.addRow("Nama Habit:", self.name_input)

        self.remind_time_input = QTimeEdit(self)
        if remind_time:
            hours, minutes = map(int, remind_time.split(":"))
            self.remind_time_input.setTime(QTime(hours, minutes))
        layout.addRow("Waktu Pengingat:", self.remind_time_input)

        self.description_input = QLineEdit(self)
        self.description_input.setText(description)
        layout.addRow("Deskripsi:", self.description_input)

        # Tombol OK dan Cancel
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_data(self):
        """Mengembalikan data dari input"""
        return self.name_input.text(), self.remind_time_input.text(), self.description_input.text()

    def validate_time(self):
        """Validasi format waktu HH:MM"""
        time = self.remind_time_input.text()
        try:
            datetime.datetime.strptime(time, "%H:%M")
            return True
        except ValueError:
            return False
        
# Menjalankan Aplikasi
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HabitTrackerApp()
    window.show()

    # Menjalankan Thread untuk Notifikasi di Latar Belakang
    def run_reminder():
        while True:
            window.check_reminders()
            threading.Event().wait(60)  # Cek setiap 60 detik

    reminder_thread = threading.Thread(target=run_reminder, daemon=True)
    reminder_thread.start()

    sys.exit(app.exec())
