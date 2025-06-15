from PyQt6 import QtWidgets, QtCore, QtGui
from db.db import get_connection
from PyQt6.QtGui import  QIcon

class VacancyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вакансии")
        self.setFixedSize(800, 600)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
            }
        """)
        self.setWindowIcon(QIcon("icon.jpg"))

        self.layout = QtWidgets.QVBoxLayout(self)
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.container = QtWidgets.QWidget()
        self.vacancy_layout = QtWidgets.QVBoxLayout(self.container)
        self.vacancy_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.container)

        self.layout.addWidget(self.scroll_area)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.add_btn = self.create_button("➕ Добавить вакансию", "#fcb1b6")
        self.add_btn.clicked.connect(self.add_vacancy)
        self.back_btn = self.create_button("🔙 Назад", "#b0c4de")
        self.button_layout.addWidget(self.add_btn)


        self.back_btn.clicked.connect(self.close)
        self.button_layout.addWidget(self.back_btn)
        self.layout.addLayout(self.button_layout)

        self.load_vacancies()

    def create_button(self, text, color):
        btn = QtWidgets.QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #ff6f61;
            }}
        """)
        return btn

    def load_vacancies(self):
        self.clear_layout(self.vacancy_layout)
        conn = get_connection()

        with conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, title FROM vacancies WHERE is_active = 1")
                vacancies = cursor.fetchall()
                for v in vacancies:
                    cursor.execute("SELECT COUNT(*) AS count FROM applications WHERE vacancy_id = %s", (v['id'],))
                    count = cursor.fetchone()["count"]
                    self.add_vacancy_card(v["id"], v["title"], count)

    def add_vacancy_card(self, vacancy_id, title, application_count):
        card = QtWidgets.QFrame()
        card.setFixedHeight(80)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                margin: 5px;
            }
        """)
        h_layout = QtWidgets.QHBoxLayout(card)

        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        h_layout.addWidget(title_label)

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        h_layout.addItem(spacer)

        badge = QtWidgets.QLabel(str(application_count))
        badge.setFixedSize(30, 30)
        badge.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet("""
            background-color: #ff4d4f;
            color: white;
            border-radius: 15px;
            font-weight: bold;
        """)
        h_layout.addWidget(badge)

        card.mousePressEvent = lambda event: self.open_candidates(vacancy_id)
        self.vacancy_layout.addWidget(card)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def open_candidates(self, vacancy_id):
        self.cand_window = CandidatesWindow(vacancy_id, self)
        self.cand_window.show()



    def add_vacancy(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Добавить вакансию")
        dialog.resize(400, 300)
        layout = QtWidgets.QFormLayout(dialog)

        title_input = QtWidgets.QLineEdit()
        city_input = QtWidgets.QLineEdit()
        salary_input = QtWidgets.QLineEdit()
        type_combo = QtWidgets.QComboBox()
        type_combo.addItems(["ТК", "ГПХ", "Самозанятый"])
        experience_input = QtWidgets.QSpinBox()
        experience_input.setRange(0, 50)

        layout.addRow("Название:", title_input)
        layout.addRow("Город:", city_input)
        layout.addRow("Зарплата:", salary_input)
        layout.addRow("Тип занятости:", type_combo)
        layout.addRow("Опыт (лет):", experience_input)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        layout.addRow(buttons)

        def save():
            title = title_input.text()
            city = city_input.text()
            try:
                salary = float(salary_input.text())
            except ValueError:
                QtWidgets.QMessageBox.warning(dialog, "Ошибка", "Некорректная зарплата.")
                return

            employment_type = type_combo.currentText()
            experience = experience_input.value()

            conn = get_connection()
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO vacancies (title, city, salary, employment_type, required_experience, is_active)
                        VALUES (%s, %s, %s, %s, %s, 1)
                    """, (title, city, salary, employment_type, experience))
                    conn.commit()

            QtWidgets.QMessageBox.information(self, "Успешно", "Вакансия добавлена.")
            dialog.accept()
            self.load_vacancies()

        buttons.accepted.connect(save)
        buttons.rejected.connect(dialog.reject)
        dialog.exec()


class CandidatesWindow(QtWidgets.QWidget):
    def __init__(self, vacancy_id, parent=None):
        super().__init__(parent)
        self.vacancy_id = vacancy_id
        self.setWindowTitle("Кандидаты на вакансию")
        self.resize(700, 500)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
            }
            QLabel {
                font-size: 14px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.container = QtWidgets.QWidget()
        self.container_layout = QtWidgets.QVBoxLayout(self.container)
        self.container_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

        self.back_btn = QtWidgets.QPushButton("🔙 Назад")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #b0c4de;
                border-radius: 20px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
        """)
        self.back_btn.clicked.connect(self.close)
        layout.addWidget(self.back_btn)

        self.load_candidates()

    def load_candidates(self):
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT a.id, a.resume_text, u.login, a.user_id
                    FROM applications a
                    JOIN users u ON u.id = a.user_id
                    WHERE a.vacancy_id = %s AND a.status = 'new'
                """, (self.vacancy_id,))
                candidates = cursor.fetchall()

        for cand in candidates:
            self.add_candidate_card(cand)

    def add_candidate_card(self, cand):
        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
                border-radius: 10px;}
        """)
        card.setFixedHeight(100)
        h_layout = QtWidgets.QHBoxLayout(card)

        name_label = QtWidgets.QLabel(f"👤 {cand['login']}")
        name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        h_layout.addWidget(name_label)

        h_layout.addStretch()

        resume_btn = QtWidgets.QPushButton("📄 Резюме")
        resume_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        border-radius: 20px;
                        color: white;
                        padding: 10px 20px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #66bb6a;
                    }
                """)
        # Передаем user_id в обработчик
        resume_btn.clicked.connect(lambda _, uid=cand["user_id"]: self.show_resume(uid))
        h_layout.addWidget(resume_btn)

        self.container_layout.addWidget(card)

    def show_resume(self, user_id):
        # Проверяем, не открыто ли уже окно резюме
        if hasattr(self, 'resume_window') and self.resume_window.isVisible():
            self.resume_window.close()

        self.resume_window = ResumeWindow(user_id)
        self.resume_window.show()


class ResumeWindow(QtWidgets.QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Просмотр резюме")
        self.resize(700, 600)
        self.setStyleSheet("""
            QWidget {
                background: #f0f8ff;
            }
            QTextEdit {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        self.title_label = QtWidgets.QLabel("Резюме кандидата")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
            }
        """)
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Область для отображения резюме
        self.resume_text = QtWidgets.QTextEdit()
        self.resume_text.setReadOnly(True)
        layout.addWidget(self.resume_text, 1)

        # Кнопки действий
        self.button_layout = QtWidgets.QHBoxLayout()

        self.hire_btn = QtWidgets.QPushButton("✅ Нанять")
        self.hire_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 15px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.hire_btn.clicked.connect(lambda: self.process_application(2))

        self.reject_btn = QtWidgets.QPushButton("❌ Отказ")
        self.reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 15px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.reject_btn.clicked.connect(lambda: self.process_application(5))

        self.close_btn = QtWidgets.QPushButton("Закрыть")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 15px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.close_btn.clicked.connect(self.close)

        self.button_layout.addWidget(self.hire_btn)
        self.button_layout.addWidget(self.reject_btn)
        self.button_layout.addWidget(self.close_btn)
        layout.addLayout(self.button_layout)

        self.load_resume_data()

    def process_application(self, role_id):
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cursor:
                    # Обновляем роль пользователя
                    cursor.execute("UPDATE users SET role = %s WHERE id = %s",
                                   (role_id, self.user_id))

                    # Определяем статус заявки
                    status = 'approved' if role_id == 2 else 'rejected'

                    # Обновляем статус заявки
                    cursor.execute("""
                        UPDATE applications 
                        SET status = %s, 
                            reviewed_by = (SELECT id FROM users WHERE role = 3 LIMIT 1),
                            reviewed_at = NOW()
                        WHERE user_id = %s
                    """, (status, self.user_id))

                    # Если нанимаем - добавляем в сотрудники
                    if role_id == 2:
                        # Получаем данные пользователя
                        cursor.execute("SELECT login FROM users WHERE id = %s", (self.user_id,))
                        user_data = cursor.fetchone()

                        # Получаем название вакансии
                        cursor.execute("""
                            SELECT v.title 
                            FROM applications a
                            JOIN vacancies v ON v.id = a.vacancy_id
                            WHERE a.user_id = %s
                            LIMIT 1
                        """, (self.user_id,))
                        vacancy_data = cursor.fetchone()

                        profession = vacancy_data['title'] if vacancy_data else "Сотрудник"

                        # Добавляем в сотрудники
                        cursor.execute("""
                            INSERT INTO employees (full_name, profession, is_active, user_id)
                            VALUES (%s, %s, 1, %s)
                        """, (user_data['login'], profession, self.user_id))

                    conn.commit()

                    # Показываем сообщение об успехе
                    msg = QtWidgets.QMessageBox(self)
                    msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
                    msg.setWindowTitle("Решение принято")

                    if role_id == 2:
                        msg.setText("Кандидат принят на работу!")
                        msg.setInformativeText("Данные добавлены в систему сотрудников.")
                    else:
                        msg.setText("Кандидату отказано.")
                        msg.setInformativeText("Статус заявки обновлен.")

                    msg.exec()

                    # Обновляем данные в окне
                    self.load_resume_data()

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось обновить данные: {str(e)}"
            )
            print(e)


    def load_resume_data(self):
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                            SELECT a.full_name, a.age, a.experience, a.resume_text, 
                                   v.title AS vacancy_title
                            FROM applications a
                            JOIN vacancies v ON v.id = a.vacancy_id
                            WHERE a.user_id = %s
                            ORDER BY a.applied_at DESC 
                            LIMIT 1
                        """, (self.user_id,))
                    resume_data = cursor.fetchone()

            if resume_data:
                # Форматируем текст резюме с структурированными данными
                formatted_text = (
                    f"<b>ФИО:</b> {resume_data['full_name']}<br>"
                    f"<b>Возраст:</b> {resume_data['age']}<br>"
                    f"<b>Опыт работы:</b> {resume_data['experience']} лет<br>"
                    f"<b>Вакансия:</b> {resume_data['vacancy_title']}<br><br>"
                    f"<b>О себе:</b><br>{resume_data['resume_text'].replace('\n', '<br>')}"
                )
                self.resume_text.setHtml(formatted_text)
            else:
                self.resume_text.setPlainText("Резюме не найдено")

        except Exception as e:
            self.resume_text.setPlainText(f"Ошибка загрузки данных: {str(e)}")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = VacancyWindow()
    ui.show()
    sys.exit(app.exec())