from PyQt6 import QtWidgets, QtCore
from db.db import get_connection

class CandidateWindow(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Кандидат: вакансии")
        self.setFixedSize(900, 700)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4)
            }
        """)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        title_label = QtWidgets.QLabel("Доступные вакансии")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        self.layout.addWidget(title_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.vacancy_container = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.vacancy_container)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(20)

        self.refresh_btn = QtWidgets.QPushButton("Обновить список")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_vacancies)
        button_layout.addWidget(self.refresh_btn)

        self.exit_btn = QtWidgets.QPushButton("Выход")
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.exit_btn.clicked.connect(self.return_to_login)
        button_layout.addWidget(self.exit_btn)

        self.layout.addLayout(button_layout)

        self.load_vacancies()
        self.vacancy_data = {}

    def load_vacancies(self):
        while self.vacancy_container.count():
            child = self.vacancy_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, title FROM vacancies WHERE is_active = 1")
                vacancies = cursor.fetchall()

                if not vacancies:
                    empty_label = QtWidgets.QLabel("На данный момент нет доступных вакансий")
                    empty_label.setStyleSheet("font-size: 16px; color: #7f8c8d;")
                    self.vacancy_container.addWidget(empty_label)
                    return

                for vac in vacancies:
                    self.add_vacancy_row(vac)

    def add_vacancy_row(self, vacancy):
        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 10, 10, 10)

        title_label = QtWidgets.QLabel(vacancy["title"])
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        row_layout.addWidget(title_label)

        apply_btn = QtWidgets.QPushButton("Откликнуться")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 10px;
                padding: 6px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        apply_btn.clicked.connect(lambda _, v_id=vacancy["id"]: self.open_resume_form(v_id))
        row_layout.addWidget(apply_btn)

        self.vacancy_container.addWidget(row_widget)

    def open_resume_form(self, vacancy_id):
        self.resume_dialog = ResumeFormDialog(self.user_id, vacancy_id)
        self.resume_dialog.exec()

    def return_to_login(self):
        from main import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

class ResumeFormDialog(QtWidgets.QDialog):
    def __init__(self, user_id, vacancy_id):
        super().__init__()
        self.user_id = user_id
        self.vacancy_id = vacancy_id
        self.setWindowTitle("Отклик на вакансию")
        self.resize(500, 400)
        self.setStyleSheet("background-color: #f8f9fa;")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QtWidgets.QLabel("Заполните данные для отклика")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2980b9;")
        layout.addWidget(title, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        form_layout = QtWidgets.QFormLayout()
        form_layout.setVerticalSpacing(10)

        self.name_input = QtWidgets.QLineEdit()
        self.age_input = QtWidgets.QSpinBox()
        self.age_input.setRange(16, 70)
        self.exp_input = QtWidgets.QSpinBox()
        self.exp_input.setRange(0, 50)
        self.resume_text = QtWidgets.QTextEdit()

        form_layout.addRow("ФИО:", self.name_input)
        form_layout.addRow("Возраст:", self.age_input)
        form_layout.addRow("Опыт (лет):", self.exp_input)
        form_layout.addRow("Резюме:", self.resume_text)

        layout.addLayout(form_layout)

        btn_layout = QtWidgets.QHBoxLayout()

        submit_btn = QtWidgets.QPushButton("Отправить")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        submit_btn.clicked.connect(self.submit)

        cancel_btn = QtWidgets.QPushButton("Отмена")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(submit_btn)
        layout.addLayout(btn_layout)

    def submit(self):
        full_name = self.name_input.text().strip()
        age = self.age_input.value()
        experience = self.exp_input.value()
        resume = self.resume_text.toPlainText()

        if not full_name or not resume:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO applications (user_id, full_name, age, experience, vacancy_id, resume_text, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'new')
                """, (self.user_id, full_name, age, experience, self.vacancy_id, resume))
                conn.commit()

        QtWidgets.QMessageBox.information(self, "Успешно", "Отклик отправлен.")
        self.accept()

class VacancyDetailDialog(QtWidgets.QDialog):
    def __init__(self, vacancy):
        super().__init__()
        self.setWindowTitle("Информация о вакансии")
        self.resize(400, 300)
        self.setStyleSheet("background-color: #f9f9f9;")

        layout = QtWidgets.QVBoxLayout(self)

        fields = [
            ("Название", vacancy.get("title")),
            ("Город", vacancy.get("city") or "Не указан"),
            ("Зарплата", f"{vacancy.get('salary')} ₽" if vacancy.get("salary") else "Не указана"),
            ("Тип занятости", vacancy.get("employment_type") or "Не указан"),
            ("Требуемый опыт", f"{vacancy.get('required_experience')} лет" if vacancy.get("required_experience") else "Не указан")
        ]

        for label, value in fields:
            row = QtWidgets.QHBoxLayout()
            lbl = QtWidgets.QLabel(f"{label}:")
            val = QtWidgets.QLabel(str(value))
            lbl.setStyleSheet("font-weight: bold;")
            row.addWidget(lbl)
            row.addWidget(val)
            layout.addLayout(row)

        btn_close = QtWidgets.QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = CandidateWindow(user_id=1)
    ui.show()
    sys.exit(app.exec())
