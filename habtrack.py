import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import HabitTrackerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HabitTrackerApp()
    window.show()
    sys.exit(app.exec())
