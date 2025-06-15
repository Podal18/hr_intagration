from PyQt6 import QtWidgets, QtCore
import pymysql

class HRMainWindow(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.ui = Ui_HRMainWindow()
        self.ui.setupUi(self, full_name="HR", user_id=user_id)


class Ui_HRMainWindow(object):
    def setupUi(self, HRMainWindow, full_name="HR", user_id=None):
        self.user_id = user_id
        HRMainWindow.setObjectName("HRMainWindow")
        HRMainWindow.setFixedSize(1000, 600)
        HRMainWindow.setWindowTitle("HR Панель")
        HRMainWindow.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        HRMainWindow.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.centralwidget = QtWidgets.QWidget(HRMainWindow)
        HRMainWindow.setCentralWidget(self.centralwidget)

        self.background = QtWidgets.QFrame(self.centralwidget)
        self.background.setGeometry(0, 0, 1000, 600)
        self.background.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
                border-radius: 10px;
            }
        """)

        self.nav_panel = QtWidgets.QFrame(self.background)
        self.nav_panel.setGeometry(0, 0, 200, 600)
        self.nav_panel.setStyleSheet("background-color: rgba(255, 255, 255, 0.95); border-top-left-radius: 10px; border-bottom-left-radius: 10px;")

        self.title = QtWidgets.QLabel("Навигация", self.nav_panel)
        self.title.setGeometry(20, 20, 160, 30)
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.employee_btn = self.create_button(self.nav_panel, "Сотрудники", 70)
        self.vacancy_btn = self.create_button(self.nav_panel, "Вакансии", 125)
        self.exit_btn = self.create_button(self.nav_panel, "Выход", 530)

        self.employee_btn.clicked.connect(self.open_employees)
        self.vacancy_btn.clicked.connect(self.open_vacancies)

        self.main_area = QtWidgets.QFrame(self.background)
        self.main_area.setGeometry(200, 0, 800, 600)
        self.main_area.setStyleSheet("background-color: rgba(255, 255, 255, 0.95); border-top-right-radius: 10px; border-bottom-right-radius: 10px;")

        self.welcome_label = QtWidgets.QLabel(self.main_area)
        self.welcome_label.setGeometry(40, 20, 700, 40)
        self.welcome_label.setStyleSheet("font-size: 22px; font-weight: 500;")
        self.welcome_label.setText(f"Добро пожаловать, HR")

        self.dashboard_cards = []

        employee_count, app_count, fire_count, vacancy_count = self.load_dashboard_data()

        self.create_dashboard_card("Сотрудников", str(employee_count), 60, "#ffb6b9")
        self.create_dashboard_card("Отклики", str(app_count), 230, "#fcd5ce")
        self.create_dashboard_card("Уволенные", str(fire_count), 400, "#b5ead7")
        self.create_dashboard_card("Вакансии", str(vacancy_count), 570, "#f9dc5c")

        self.exit_button = QtWidgets.QPushButton(parent=HRMainWindow)
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
        self.exit_button.clicked.connect(HRMainWindow.close)

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
        self.dashboard_cards.append(card)

    def load_dashboard_data(self):
        try:
            conn = pymysql.connect(host='localhost', user='root', password='', database='diplom', port=3312, charset='utf8mb4')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM employees WHERE is_active=1")
            employee_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM applications")
            app_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM firings")
            fire_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM vacancies WHERE is_active=1")
            vacancy_count = cursor.fetchone()[0]
            conn.close()
            return employee_count, app_count, fire_count, vacancy_count
        except Exception as e:
            print("Ошибка подключения к базе данных:", e)
            return 0, 0, 0, 0

    def open_employees(self):
        from ui.employee_window import EmployeeCardWindow
        self.employee_window = EmployeeCardWindow(current_user_id=self.user_id)
        self.employee_window.show()

    def open_vacancies(self):
        from ui.vacancy_window import VacancyWindow
        self.vacancy_window = VacancyWindow()
        self.vacancy_window.show()
