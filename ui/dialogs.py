from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QTimeEdit, QDialogButtonBox
from PyQt6.QtCore import QTime
import datetime

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