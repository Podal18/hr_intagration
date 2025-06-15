from PyQt6 import QtWidgets, QtCore, QtGui
from db.db import get_connection
import os
from datetime import datetime, timedelta
from ui.fire_dialog import FireDialog, Ui_ReportWindow
from PyQt6.QtGui import QIcon


class EmployeeDetailsDialog(QtWidgets.QDialog):
    def __init__(self, employee):
        super().__init__()
        self.setWindowTitle("Информация о сотруднике")
        self.setFixedSize(500, 600)

        # Стилизация окна
        self.setStyleSheet("""
            QDialog {
                background: #f5f7fa;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: #333;
                font-size: 14px;
                margin: 5px 0;
            }
            QGroupBox {
                border: 1px solid #dcdfe6;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px 0;
                font-weight: bold;
                color: #409eff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background: #409eff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #66b1ff;
            }
        """)

        main_layout = QtWidgets.QVBoxLayout(self)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        scroll_area.setWidget(container)

        # Заголовок с фото
        header_layout = QtWidgets.QHBoxLayout()
        if employee.get("photo_path") and os.path.exists(employee["photo_path"]):
            pixmap = QtGui.QPixmap(employee["photo_path"]).scaled(120, 160,
                                                                  QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                                  QtCore.Qt.TransformationMode.SmoothTransformation)
            photo_label = QtWidgets.QLabel()
            photo_label.setPixmap(pixmap)
            photo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            photo_label.setStyleSheet("border: 2px solid #dcdfe6; border-radius: 4px;")
            header_layout.addWidget(photo_label)
        else:
            no_photo = QtWidgets.QLabel("Нет фото")
            no_photo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            no_photo.setStyleSheet("""
                background: #ebeef5; 
                border: 2px dashed #dcdfe6; 
                border-radius: 4px;
                min-width: 120px;
                min-height: 160px;
            """)
            header_layout.addWidget(no_photo)

        info_layout = QtWidgets.QVBoxLayout()
        name_label = QtWidgets.QLabel(f"<h2>{employee['full_name']}</h2>")
        name_label.setStyleSheet("color: #303133;")
        info_layout.addWidget(name_label)

        # Получаем возраст из таблицы applications
        age = self.get_employee_age(employee.get("user_id"))
        if age is not None:
            age_label = QtWidgets.QLabel(f"<b>Возраст:</b> {age} лет")
            info_layout.addWidget(age_label)

        if employee.get("profession"):
            prof_label = QtWidgets.QLabel(f"<b>Должность:</b> {employee['profession']}")
            info_layout.addWidget(prof_label)

        status = "Активен" if employee.get("is_active", 1) else "Уволен"
        status_label = QtWidgets.QLabel(f"<b>Статус:</b> {status}")
        status_label.setStyleSheet("color: #67c23a;" if status == "Активен" else "color: #f56c6c;")
        info_layout.addWidget(status_label)

        header_layout.addLayout(info_layout)
        layout.addLayout(header_layout)

        # Основная информация
        info_group = QtWidgets.QGroupBox("Дополнительная информация")
        info_layout = QtWidgets.QFormLayout(info_group)

        # Получаем опыт работы из таблицы applications
        experience = self.get_employee_experience(employee.get("user_id"))
        if experience is not None:
            exp_label = QtWidgets.QLabel(f"{experience} лет")
            info_layout.addRow("Опыт работы:", exp_label)

        # Получаем дату приема из заявки
        hire_date = self.get_hire_date(employee.get("user_id"))
        if hire_date:
            hire_label = QtWidgets.QLabel(hire_date.strftime("%d.%m.%Y"))
            info_layout.addRow("Дата приема:", hire_label)

        layout.addWidget(info_group)

        # Паспортные данные
        passport_group = QtWidgets.QGroupBox("Паспортные данные")
        passport_layout = QtWidgets.QVBoxLayout(passport_group)

        if employee.get("passport_scan_path") and os.path.exists(employee["passport_scan_path"]):
            pixmap = QtGui.QPixmap(employee["passport_scan_path"])
            img_label = QtWidgets.QLabel()
            img_label.setPixmap(pixmap.scaled(450, 300,
                                              QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                              QtCore.Qt.TransformationMode.SmoothTransformation))
            img_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            passport_layout.addWidget(img_label)
        else:
            no_scan = QtWidgets.QLabel("Скан паспорта отсутствует")
            no_scan.setStyleSheet("color: #909399; font-style: italic;")
            no_scan.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            passport_layout.addWidget(no_scan)

        layout.addWidget(passport_group)
        layout.addStretch()

        # Кнопка закрытия
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QtWidgets.QPushButton("Закрыть")
        close_btn.setFixedWidth(150)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def get_employee_age(self, user_id):
        """Получаем возраст сотрудника из таблицы applications"""
        if not user_id:
            return None

        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT age FROM applications WHERE user_id = %s ORDER BY applied_at DESC LIMIT 1",
                    (user_id,)
                )
                result = cursor.fetchone()
                return result["age"] if result else None

    def get_employee_experience(self, user_id):
        """Получаем опыт работы сотрудника из таблицы applications"""
        if not user_id:
            return None

        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT experience FROM applications WHERE user_id = %s ORDER BY applied_at DESC LIMIT 1",
                    (user_id,)
                )
                result = cursor.fetchone()
                return result["experience"] if result else None

    def get_hire_date(self, user_id):
        """Получаем дату приема сотрудника из таблицы applications"""
        if not user_id:
            return None

        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT applied_at FROM applications WHERE user_id = %s ORDER BY applied_at DESC LIMIT 1",
                    (user_id,)
                )
                result = cursor.fetchone()
                return result["applied_at"] if result else None


class EmployeeCardWindow(QtWidgets.QWidget):
    def __init__(self, current_user_id):
        super().__init__()
        self.current_user_id = current_user_id
        self.setWindowTitle("Сотрудники")
        self.setWindowIcon(QIcon("icon.jpg"))
        self.setFixedSize(900, 600)

        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
            }
        """)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.sort_box = QtWidgets.QComboBox()
        self.sort_box.addItems(["Сортировать по шансу (по убыванию)", "Сортировать по шансу (по возрастанию)"])
        self.sort_box.currentIndexChanged.connect(self.load_employees_from_db)
        self.layout.addWidget(self.sort_box)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.container = QtWidgets.QWidget()
        self.card_layout = QtWidgets.QVBoxLayout(self.container)
        self.card_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.container)
        self.layout.addWidget(self.scroll_area)

        self.fire_btn = self.create_button("\U0001F525 Уволить сотрудника", "#ff4d4f")
        self.fire_btn.clicked.connect(self.fire_employee_dialog)
        self.layout.addWidget(self.fire_btn)

        self.back_btn = self.create_button("\ud83d\udd19 Назад", "#b0c4de")
        self.back_btn.clicked.connect(self.close)
        self.layout.addWidget(self.back_btn)

        self.load_employees_from_db()

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

    def load_employees_from_db(self):
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM employees WHERE is_active = 1")
                employees = cursor.fetchall()

                for emp in employees:
                    emp["fire_chance"] = self.calculate_fire_chance(cursor, emp["id"])

                if self.sort_box.currentIndex() == 0:
                    employees.sort(key=lambda x: x["fire_chance"], reverse=True)
                else:
                    employees.sort(key=lambda x: x["fire_chance"])

                self.all_employees = employees
                self.render_employees()

    def render_employees(self):
        self.clear_layout(self.card_layout)
        for emp in self.all_employees:
            self.add_employee_card(emp)

    def add_employee_card(self, emp):
        card = QtWidgets.QFrame()
        card.setFixedHeight(150)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                margin: 10px;
            }
        """)
        h_layout = QtWidgets.QHBoxLayout(card)

        photo_label = QtWidgets.QLabel()
        photo_label.setFixedSize(100, 100)
        if emp["photo_path"] and os.path.exists(emp["photo_path"]):
            pixmap = QtGui.QPixmap(emp["photo_path"]).scaled(100, 100, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            photo_label.setPixmap(pixmap)
        else:
            photo_label.setText("Нет фото")
            photo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        h_layout.addWidget(photo_label)

        info_layout = QtWidgets.QVBoxLayout()
        info_layout.addWidget(QtWidgets.QLabel(f"<b>{emp['full_name']}</b>"))
        info_layout.addWidget(QtWidgets.QLabel(f"Должность: {emp['profession']}"))
        info_layout.addWidget(QtWidgets.QLabel(f"Шанс на увольнение: {emp['fire_chance']}%"))
        h_layout.addLayout(info_layout)

        button_layout = QtWidgets.QVBoxLayout()
        motivate_btn = self.create_button("Мотивировать", "#4CAF50")
        motivate_btn.clicked.connect(lambda: self.open_motivation(emp['id'], emp['full_name']))
        details_btn = self.create_button("Подробнее", "#3f51b5")
        details_btn.clicked.connect(lambda: self.open_details(emp))
        button_layout.addWidget(motivate_btn)
        button_layout.addWidget(details_btn)
        h_layout.addLayout(button_layout)

        self.card_layout.addWidget(card)

    def open_details(self, employee):
        dialog = EmployeeDetailsDialog(employee)
        dialog.exec()

    def fire_employee_dialog(self):
        self.fire_dialog = FireDialog(self.current_user_id)
        self.fire_dialog.show()

    def commit_firing(self, employee_id, reason):
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE employees SET is_active = 0 WHERE id = %s", (employee_id,))
                cursor.execute("INSERT INTO firings (employee_id, reason, fired_by) VALUES (%s, %s, %s)",
                               (employee_id, reason, self.current_user_id))
                conn.commit()

        QtWidgets.QMessageBox.information(self, "Успешно", "Сотрудник уволен.")
        self.load_employees_from_db()

    def calculate_fire_chance(self, cursor, emp_id):
        cursor.execute("SELECT status FROM attendance WHERE employee_id = %s", (emp_id,))
        attendance = cursor.fetchall()
        absents = sum(1 for a in attendance if a["status"] == "absent")
        lates = sum(1 for a in attendance if a["status"] == "late")
        score = absents * 10 + lates * 5

        ninety_days_ago = datetime.now() - timedelta(days=90)
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM motivation_actions
            WHERE employee_id = %s AND created_at >= %s
        """, (emp_id, ninety_days_ago))
        if cursor.fetchone()["cnt"] == 0:
            score += 15

        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM motivation_actions
            WHERE employee_id = %s AND action_type = 'promotion'
        """, (emp_id,))
        if cursor.fetchone()["cnt"] == 0:
            score += 10

        return min(100, score)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def open_motivation(self, emp_id, emp_name):
        from ui.motivation_window import MotivationWindow
        self.motivation_win = MotivationWindow(emp_id, emp_name, self.current_user_id)
        self.motivation_win.show()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = EmployeeCardWindow(current_user_id=1)
    ui.show()
    sys.exit(app.exec())
