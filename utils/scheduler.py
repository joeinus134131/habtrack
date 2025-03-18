import os
import platform

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "..", "data", "habits.db")

def schedule_task():
    """Menjadwalkan aplikasi untuk berjalan setiap hari"""
    if platform.system() == "Windows":
        os.system("schtasks /create /sc daily /tn HabitTracker /tr %cd%\\HabitTracker.exe /st 08:00")
    else:
        os.system("(crontab -l; echo '0 8 * * * python3 {}/habtrack.py') | crontab -".format(BASE_DIR))