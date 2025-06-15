from PyQt6 import QtCore, QtWidgets
from db.db import get_connection


class EmployeeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сотрудники")
        self.resize(1000, 600)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)



        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # Главный слой
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.background = QtWidgets.QFrame(self.centralwidget)
        self.background.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(self.background)

        # Слой для фона
        bg_layout = QtWidgets.QVBoxLayout(self.background)
        bg_layout.setContentsMargins(30, 20, 30, 20)
        bg_layout.setSpacing(20)

        # Заголовок
        self.title_label = QtWidgets.QLabel("Список сотрудников")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        bg_layout.addWidget(self.title_label)

        # Таблица
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ФИО", "Должность", "Статус", "Действия"])
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 10px;
            }
            QHeaderView::section {
                background-color: #fcb1b6;
                padding: 4px;
                font-weight: bold;
                border: 1px solid white;
            }
        """)
        # Растягиваем колонки
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        bg_layout.addWidget(self.table, 1)  # Коэффициент растяжения

        # Кнопка "Назад"
        self.back_button = QtWidgets.QPushButton("← Назад")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333;
                font-size: 14px;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.back_button.setFixedSize(100, 40)
        self.back_button.clicked.connect(self.close)

        # Контейнер для кнопки
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.back_button)
        button_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        bg_layout.addLayout(button_layout)

        self.load_employees()

    def load_employees(self):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                # ИСПРАВЛЕНО: добавлен id в запрос
                cursor.execute("SELECT id, full_name, profession, is_active FROM employees")
                employees = cursor.fetchall()
                self.table.setRowCount(len(employees))
                for row, emp in enumerate(employees):
                    self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(emp["full_name"]))
                    self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(emp["profession"] or "—"))
                    status_text = "Активен" if emp["is_active"] else "Неактивен"
                    status_item = QtWidgets.QTableWidgetItem(status_text)
                    status_item.setData(QtCore.Qt.ItemDataRole.UserRole, emp["id"])
                    self.table.setItem(row, 2, status_item)

                    # Кнопки действий
                    widget = QtWidgets.QWidget()
                    layout = QtWidgets.QHBoxLayout(widget)

                    toggle_btn = QtWidgets.QPushButton("Активировать" if not emp["is_active"] else "Деактивировать")
                    toggle_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #81c784;
                            color: white;
                            border-radius: 5px;
                            padding: 5px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #66bb6a;
                        }
                    """)
                    toggle_btn.clicked.connect(lambda _, r=row: self.toggle_employee_status(r))

                    delete_btn = QtWidgets.QPushButton("Удалить")
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e57373;
                            color: white;
                            border-radius: 5px;
                            padding: 5px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #ef5350;
                        }
                    """)
                    delete_btn.setEnabled(not emp["is_active"])
                    delete_btn.clicked.connect(lambda _, r=row: self.delete_employee(r))

                    layout.addWidget(toggle_btn)
                    layout.addWidget(delete_btn)
                    layout.setContentsMargins(5, 5, 5, 5)

                    self.table.setCellWidget(row, 3, widget)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки: {str(e)}")
        finally:
            connection.close()

    def toggle_employee_status(self, row):
        employee_id = self.table.item(row, 2).data(QtCore.Qt.ItemDataRole.UserRole)
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT is_active FROM employees WHERE id = %s
                """, (employee_id,))
                current_status = cursor.fetchone()["is_active"]

                new_status = not current_status
                cursor.execute("""
                    UPDATE employees SET is_active = %s WHERE id = %s
                """, (new_status, employee_id))
                connection.commit()

                # Обновляем отображение
                status_text = "Активен" if new_status else "Неактивен"
                self.table.item(row, 2).setText(status_text)

                # Обновляем кнопки
                widget = self.table.cellWidget(row, 3)
                toggle_btn = widget.layout().itemAt(0).widget()
                delete_btn = widget.layout().itemAt(1).widget()

                toggle_btn.setText("Деактивировать" if new_status else "Активировать")
                delete_btn.setEnabled(not new_status)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка обновления: {str(e)}")
        finally:
            connection.close()

    def delete_employee(self, row):
        employee_id = self.table.item(row, 2).data(QtCore.Qt.ItemDataRole.UserRole)
        reply = QtWidgets.QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить этого сотрудника?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            connection = get_connection()
            try:
                with connection.cursor() as cursor:
                    # Удаляем связанные данные
                    cursor.execute(
                        "DELETE FROM applications WHERE user_id = (SELECT user_id FROM employees WHERE id = %s)",
                        (employee_id,))
                    cursor.execute("DELETE FROM attendance WHERE employee_id = %s", (employee_id,))
                    cursor.execute("DELETE FROM firings WHERE employee_id = %s", (employee_id,))
                    cursor.execute("DELETE FROM motivation_actions WHERE employee_id = %s", (employee_id,))

                    # Удаляем сотрудника
                    cursor.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
                    connection.commit()

                    # Удаляем строку из таблицы
                    self.table.removeRow(row)

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")
            finally:
                connection.close()

# Тестовое открытие
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = EmployeeWindow()
    win.show()
    sys.exit(app.exec())
