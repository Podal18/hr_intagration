from PyQt6 import QtCore, QtWidgets



class Ui_AdminMainWindow(object):
    def setupUi(self, AdminMainWindow, full_name=None):
        AdminMainWindow.setObjectName("AdminMainWindow")
        AdminMainWindow.setFixedSize(1000, 600)
        AdminMainWindow.setWindowTitle("Администратор")
        AdminMainWindow.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        AdminMainWindow.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)


        self.centralwidget = QtWidgets.QWidget(AdminMainWindow)
        AdminMainWindow.setCentralWidget(self.centralwidget)

        # Фон
        self.background = QtWidgets.QFrame(self.centralwidget)
        self.background.setGeometry(0, 0, 1000, 600)
        self.background.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d4fc79, stop:1 #96e6a1);
                border-radius: 10px;
            }
        """)

        # Навигационная панель
        self.nav_panel = QtWidgets.QFrame(self.background)
        self.nav_panel.setGeometry(0, 0, 200, 600)
        self.nav_panel.setStyleSheet("background-color: rgba(255, 255, 255, 0.95); border-top-left-radius: 10px; border-bottom-left-radius: 10px;")

        self.title = QtWidgets.QLabel("Навигация", self.nav_panel)
        self.title.setGeometry(20, 20, 160, 30)
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")



        self.exit_btn = self.create_button(self.nav_panel, "Выход", 530)

        # Центральная панель
        self.main_area = QtWidgets.QFrame(self.background)
        self.main_area.setGeometry(200, 0, 800, 600)
        self.main_area.setStyleSheet("background-color: rgba(255, 255, 255, 0.95); border-top-right-radius: 10px; border-bottom-right-radius: 10px;")

        self.welcome_label = QtWidgets.QLabel(self.main_area)
        self.welcome_label.setGeometry(40, 20, 700, 40)
        self.welcome_label.setStyleSheet("font-size: 22px; font-weight: 500;")
        self.welcome_label.setText(f"Добро пожаловать, Администратор")

        self.create_dashboard_card("Всего пользователей", self.get_total_users(), 60, "#caffbf")
        self.create_dashboard_card("Неактивных сотрудников", self.get_inactive_employees(), 300, "#ffadad")

        self.users_btn = self.create_button(self.nav_panel, "Сотрудники", 70)
        self.users_btn.clicked.connect(self.open_user_window)
        self.vacancies_btn = self.create_button(self.nav_panel, "Вакансии", 125)
        self.vacancies_btn.clicked.connect(self.open_vacancy_window)
        self.log_btn = self.create_button(self.nav_panel, "История", 180)
        self.log_btn.clicked.connect(self.open_logo_window)


        # ✕ Кнопка
        self.exit_button = QtWidgets.QPushButton(parent=AdminMainWindow)
        self.exit_button.setGeometry(QtCore.QRect(960, 10, 30, 30))
        self.exit_button.setObjectName("exit_button")
        self.exit_button.setText("✕")
        self.exit_button.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                font-size: 18px;
                color: #ff9a9e;
            }
            QPushButton:hover {
                color: #ffdddd;
            }
        """)
        self.exit_button.clicked.connect(AdminMainWindow.close)

    def get_total_users(self):
        from db.db import get_connection
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM users")
                return str(cursor.fetchone()["total"])
        finally:
            conn.close()

    def get_inactive_employees(self):
        from db.db import get_connection
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM employees WHERE is_active = 0")
                return str(cursor.fetchone()["total"])
        finally:
            conn.close()

    def create_button(self, parent, text, y):
        button = QtWidgets.QPushButton(text, parent)
        button.setGeometry(20, y, 160, 40)
        button.setStyleSheet("""
            QPushButton {
                background-color: #ff6f61;
                color: white;
                border-radius: 20px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e55b50;
                color: #fff0f0;
            }
        """)
        return button

    def create_dashboard_card(self, title, value, x, color):
        card = QtWidgets.QFrame(self.main_area)
        card.setGeometry(x, 100, 180, 120)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 15px;
            }}
        """)
        label_title = QtWidgets.QLabel(title, card)
        label_title.setGeometry(10, 10, 160, 30)
        label_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        label_value = QtWidgets.QLabel(value, card)
        label_value.setGeometry(10, 50, 160, 50)
        label_value.setStyleSheet("font-size: 32px; font-weight: bold; color: #222;")

    def open_user_window(self):
        from ui.user_window import EmployeeWindow
        self.user_ui = EmployeeWindow()
        self.user_ui.show()

    def open_logo_window(self):
        from ui.log_window import LogWindow
        self.ui_log = LogWindow()
        self.ui_log.show()

    def open_vacancy_window(self):
        from ui.vacancy_admin import VacancyWindow
        self.vacancy_ui = VacancyWindow()
        self.vacancy_ui.show()


# Пример запуска
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = Ui_AdminMainWindow()
    ui.setupUi(window, full_name="")
    window.show()
    sys.exit(app.exec())
