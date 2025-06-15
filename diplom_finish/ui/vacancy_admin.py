from PyQt6 import QtCore, QtWidgets
from db.db import get_connection


class VacancyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление вакансиями")
        self.resize(1000, 600)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)



        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # Главный слой для центрального виджета
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.background = QtWidgets.QFrame(self.centralwidget)
        self.background.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
                border-radius: 10px;}
        """)
        main_layout.addWidget(self.background)

        # Слой для фона
        bg_layout = QtWidgets.QVBoxLayout(self.background)
        bg_layout.setContentsMargins(30, 20, 30, 20)
        bg_layout.setSpacing(20)

        # Заголовок
        self.title_label = QtWidgets.QLabel("Управление вакансиями")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        bg_layout.addWidget(self.title_label)

        # Таблица (растягивается на всё доступное пространство)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Должность", "Город", "Зарплата", "Опыт", "Статус", "Действия"])
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
        # Автоматическое растягивание колонок
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        bg_layout.addWidget(self.table, 1)  # Коэффициент растяжения 1

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

        # Контейнер для кнопки с выравниванием влево
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.back_button)
        button_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        bg_layout.addLayout(button_layout)

        self.load_vacancies()

    def load_vacancies(self):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, title, city, salary, required_experience, is_active 
                    FROM vacancies
                """)
                vacancies = cursor.fetchall()
                self.table.setRowCount(len(vacancies))
                for row, vac in enumerate(vacancies):
                    self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(vac["title"]))
                    self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(vac["city"] or "—"))
                    self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{vac['salary']:,.2f} ₽"))
                    self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(
                        f"{vac['required_experience']} лет" if vac['required_experience'] > 0 else "Без опыта"))

                    status_text = "Активна" if vac["is_active"] else "Неактивна"
                    status_item = QtWidgets.QTableWidgetItem(status_text)
                    status_item.setData(QtCore.Qt.ItemDataRole.UserRole, vac["id"])
                    self.table.setItem(row, 4, status_item)

                    # Добавляем кнопки действий
                    widget = QtWidgets.QWidget()
                    layout = QtWidgets.QHBoxLayout(widget)

                    # Кнопка активации/деактивации
                    toggle_btn = QtWidgets.QPushButton("Активировать" if not vac["is_active"] else "Деактивировать")
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
                    toggle_btn.clicked.connect(lambda _, r=row: self.toggle_vacancy_status(r))

                    # Кнопка удаления (только для неактивных)
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
                    delete_btn.setEnabled(not vac["is_active"])
                    delete_btn.clicked.connect(lambda _, r=row: self.delete_vacancy(r))

                    layout.addWidget(toggle_btn)
                    layout.addWidget(delete_btn)
                    layout.setContentsMargins(5, 5, 5, 5)

                    self.table.setCellWidget(row, 5, widget)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки: {str(e)}")
        finally:
            connection.close()

    def toggle_vacancy_status(self, row):
        vacancy_id = self.table.item(row, 4).data(QtCore.Qt.ItemDataRole.UserRole)
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT is_active FROM vacancies WHERE id = %s
                """, (vacancy_id,))
                current_status = cursor.fetchone()["is_active"]

                new_status = not current_status
                cursor.execute("""
                    UPDATE vacancies SET is_active = %s WHERE id = %s
                """, (new_status, vacancy_id))
                connection.commit()

                # Обновляем отображение
                status_text = "Активна" if new_status else "Неактивна"
                self.table.item(row, 4).setText(status_text)

                # Обновляем кнопки
                widget = self.table.cellWidget(row, 5)
                toggle_btn = widget.layout().itemAt(0).widget()
                delete_btn = widget.layout().itemAt(1).widget()

                toggle_btn.setText("Деактивировать" if new_status else "Активировать")
                delete_btn.setEnabled(not new_status)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка обновления: {str(e)}")
        finally:
            connection.close()

    def delete_vacancy(self, row):
        vacancy_id = self.table.item(row, 4).data(QtCore.Qt.ItemDataRole.UserRole)
        reply = QtWidgets.QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить эту вакансию?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            connection = get_connection()
            try:
                with connection.cursor() as cursor:
                    # Удаляем связанные заявки
                    cursor.execute("DELETE FROM applications WHERE vacancy_id = %s", (vacancy_id,))

                    # Удаляем вакансию
                    cursor.execute("DELETE FROM vacancies WHERE id = %s", (vacancy_id,))
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
    win = VacancyWindow()
    win.show()
    sys.exit(app.exec())