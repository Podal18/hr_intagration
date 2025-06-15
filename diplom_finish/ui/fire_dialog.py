from PyQt6 import QtCore, QtGui, QtWidgets
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from db.db import get_connection
from datetime import datetime, timedelta


class Ui_ReportWindow(object):
    def setupUi(self, ReportWindow):
        ReportWindow.setObjectName("ReportWindow")
        ReportWindow.setFixedSize(1000, 600)
        ReportWindow.setWindowTitle("Отчёты")
        ReportWindow.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        ReportWindow.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.centralwidget = QtWidgets.QWidget(ReportWindow)
        ReportWindow.setCentralWidget(self.centralwidget)

        self.background = QtWidgets.QFrame(self.centralwidget)
        self.background.setGeometry(0, 0, 1000, 600)
        self.background.setStyleSheet("""
            QFrame {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
                border-radius: 0px;
            }
        """)

        self.exit_button = QtWidgets.QPushButton(parent=ReportWindow)
        self.exit_button.setGeometry(QtCore.QRect(960, 10, 30, 30))
        self.exit_button.setText("✕")
        self.exit_button.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                font-size: 18px;
                color: white;
            }
            QPushButton:hover {
                color: #ffdddd;
            }
        """)
        self.exit_button.clicked.connect(ReportWindow.close)

        self.back_button = QtWidgets.QPushButton("←", self.background)
        self.back_button.setGeometry(30, 540, 60, 40)
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
        self.back_button.clicked.connect(ReportWindow.close)

        self.title_label = QtWidgets.QLabel(self.background)
        self.title_label.setGeometry(30, 20, 600, 40)
        self.title_label.setText("Аналитика и отчёты")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

        self.filter_frame = QtWidgets.QFrame(self.background)
        self.filter_frame.setGeometry(30, 70, 940, 60)
        self.filter_frame.setStyleSheet("background-color: rgba(255,255,255,0.9); border-radius: 10px;")

        self.report_type_combo = QtWidgets.QComboBox(self.filter_frame)
        self.report_type_combo.setGeometry(20, 10, 200, 40)
        self.report_type_combo.addItems(["Выберите тип отчёта", "По опозданиям"])

        self.plot_button = QtWidgets.QPushButton("📈 График", self.filter_frame)
        self.plot_button.setGeometry(320, 10, 120, 40)
        self.plot_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4caf50;
                        color: white;
                        border-radius: 20px;
                        font-size: 15px;
                    }
                    QPushButton:hover {
                        background-color: #66bb6a;
                    }
                """)
        self.plot_button.setEnabled(False)

        self.generate_button = QtWidgets.QPushButton("📊 Список", self.filter_frame)
        self.generate_button.setGeometry(460, 10, 140, 40)

        self.export_button = QtWidgets.QPushButton("⬇️ Экспорт", self.filter_frame)
        self.export_button.setGeometry(620, 10, 120, 40)

        self.fire_button = QtWidgets.QPushButton("🔥 Уволить", self.filter_frame)
        self.fire_button.setGeometry(760, 10, 120, 40)
        self.fire_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border-radius: 20px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #ff8e8e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)
        self.fire_button.setEnabled(False)

        for btn in [self.generate_button, self.export_button, self.fire_button, self.plot_button]:
            btn.setStyleSheet(btn.styleSheet() + """
                QPushButton {
                    border-radius: 20px;
                    font-size: 15px;
                }
            """)

        self.report_area = QtWidgets.QFrame(self.background)
        self.report_area.setGeometry(30, 150, 940, 370)
        self.report_area.setStyleSheet("background-color: white; border-radius: 10px;")
        self.report_placeholder = QtWidgets.QLabel("Здесь будет отображаться отчёт...", self.report_area)
        self.report_placeholder.setGeometry(0, 0, 940, 370)
        self.report_placeholder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_placeholder.setStyleSheet("font-size: 16px; color: #888;")


class FireDialog(QtWidgets.QMainWindow):
    def __init__(self, current_user_id):
        super().__init__()
        super().__init__()
        self.ui = Ui_ReportWindow()
        self.ui.setupUi(self)
        self.current_user_id = current_user_id
        self.selected_employee_id = None
        self.personal_report_exported = False
        self.setup_connections()

    def setup_connections(self):
        self.ui.generate_button.clicked.connect(self.generate_report)
        self.ui.export_button.clicked.connect(self.export_report)
        self.ui.back_button.clicked.connect(self.close)
        self.ui.fire_button.clicked.connect(self.fire_employee)
        self.ui.plot_button.clicked.connect(self.plot_lateness_graph)

    def generate_report(self):
        report_type = self.ui.report_type_combo.currentText()

        try:
            if report_type == "По опозданиям":
                data = self.load_lateness_report()
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите тип отчёта")
                return

            self.display_report(data, report_type)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка формирования отчёта: {str(e)}")

    def calculate_fire_chance(self, emp_id):
        """Вычисляет шанс увольнения для сотрудника"""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # Получаем данные о посещаемости
                cursor.execute("SELECT status FROM attendance WHERE employee_id = %s", (emp_id,))
                attendance = cursor.fetchall()
                absents = sum(1 for a in attendance if a["status"] == "absent")
                lates = sum(1 for a in attendance if a["status"] == "late")
                score = absents * 10 + lates * 5

                # Проверяем мотивацию за последние 90 дней
                ninety_days_ago = datetime.now() - timedelta(days=90)
                cursor.execute("""
                    SELECT COUNT(*) AS cnt FROM motivation_actions
                    WHERE employee_id = %s AND created_at >= %s
                """, (emp_id, ninety_days_ago))
                if cursor.fetchone()["cnt"] == 0:
                    score += 15

                # Проверяем наличие повышений
                cursor.execute("""
                    SELECT COUNT(*) AS cnt FROM motivation_actions
                    WHERE employee_id = %s AND action_type = 'promotion'
                """, (emp_id,))
                if cursor.fetchone()["cnt"] == 0:
                    score += 10

                return min(100, score)
        finally:
            conn.close()

    def load_lateness_report(self):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                # Получаем всех активных сотрудников
                cursor.execute("SELECT id, full_name FROM employees WHERE is_active = 1")
                employees = cursor.fetchall()

                # Рассчитываем шанс увольнения для каждого
                high_risk_employees = []
                for emp in employees:
                    chance = self.calculate_fire_chance(emp['id'])
                    if chance > 50:  # Фильтруем по шансу >50%
                        emp['fire_chance'] = chance
                        high_risk_employees.append(emp)

                # Сортируем по убыванию шанса
                high_risk_employees.sort(key=lambda x: x["fire_chance"], reverse=True)
                return high_risk_employees
        finally:
            connection.close()

    def display_report(self, data, report_type):
        try:
            for child in self.ui.report_area.children():
                if isinstance(child, QtWidgets.QWidget):
                    child.deleteLater()

            if not data:
                raise ValueError("Нет сотрудников с высоким риском увольнения")

            container = QtWidgets.QWidget(self.ui.report_area)
            container.setGeometry(10, 10, 920, 350)
            layout = QtWidgets.QVBoxLayout(container)

            table = QtWidgets.QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["ID", "Сотрудник", "Шанс увольнения"])
            table.setRowCount(len(data))

            # Скрываем столбец с ID
            table.setColumnHidden(0, True)

            for row_idx, row in enumerate(data):
                table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(row['id'])))
                table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(row['full_name'])))

                # Добавляем шанс увольнения с цветовой индикацией
                chance_item = QtWidgets.QTableWidgetItem(f"{row['fire_chance']}%")

                # Цветовая индикация в зависимости от уровня риска
                if row['fire_chance'] > 70:
                    chance_item.setBackground(QtGui.QColor(255, 100, 100))  # Красный
                elif row['fire_chance'] > 50:
                    chance_item.setBackground(QtGui.QColor(255, 255, 100))  # Желтый

                table.setItem(row_idx, 2, chance_item)

            table.resizeColumnsToContents()
            table.itemSelectionChanged.connect(lambda: self.handle_table_selection(table))
            layout.addWidget(table)
            container.show()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка отображения: {str(e)}")

    def handle_table_selection(self, table):
        selected_items = table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.selected_employee_id = int(table.item(row, 0).text())
            employee_name = table.item(row, 1).text()
            self.ui.fire_button.setEnabled(True)
            self.ui.fire_button.setText(f"🔥 Уволить {employee_name}")
            self.ui.plot_button.setEnabled(True)
            self.personal_report_exported = False  # reset flag on new selection
        else:
            self.selected_employee_id = None
            self.ui.fire_button.setEnabled(False)
            self.ui.fire_button.setText("🔥 Уволить")
            self.ui.plot_button.setEnabled(False)

    def export_report(self):
        try:
            container = self.ui.report_area.findChild(QtWidgets.QWidget)
            if not container:
                raise ValueError("Отчёт не сгенерирован")

            table = container.findChild(QtWidgets.QTableWidget)
            if not table:
                raise ValueError("Таблица не найдена")

            if table.rowCount() == 0:
                raise ValueError("Таблица пуста")

            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Экспорт", "", "CSV Files (*.csv)")

            if not filename:
                return

            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=';')

                headers = []
                for col in range(table.columnCount()):
                    if not table.isColumnHidden(col):
                        headers.append(table.horizontalHeaderItem(col).text())
                writer.writerow(headers)

                for row in range(table.rowCount()):
                    row_data = []
                    for col in range(table.columnCount()):
                        if not table.isColumnHidden(col):
                            item = table.item(row, col)
                            row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QtWidgets.QMessageBox.information(self, "Успех", "Экспорт завершён")
            self.personal_report_exported = True

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка экспорта", f"{str(e)}")

    def fire_employee(self):
        if not self.selected_employee_id:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Сотрудник не выбран")
            return

        if not self.personal_report_exported:
            QtWidgets.QMessageBox.warning(self, "Внимание", "Сначала экспортируйте отчёт по опозданиям/неявкам сотрудника.")
            return

        reason, ok = QtWidgets.QInputDialog.getText(
            self,
            "Увольнение сотрудника",
            "Укажите причину увольнения:",
            QtWidgets.QLineEdit.EchoMode.Normal
        )

        if not ok or not reason.strip():
            return

        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE employees 
                    SET is_active = 0 
                    WHERE id = %s
                """, (self.selected_employee_id,))

                cursor.execute("""
                    INSERT INTO firings (employee_id, reason, fired_by, fired_at)
                    VALUES (%s, %s, %s, NOW())
                """, (self.selected_employee_id, reason, self.current_user_id))

                connection.commit()

            QtWidgets.QMessageBox.information(
                self,
                "Успех",
                f"Сотрудник успешно уволен. Причина: {reason}"
            )
            self.generate_report()

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось уволить сотрудника: {str(e)}"
            )

    def show_lateness_table_for_employee(self):
        """Отображает таблицу опозданий выбранного сотрудника"""
        if not self.selected_employee_id:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Сотрудник не выбран")
            return

        try:
            con = get_connection()
            with con.cursor() as cursor:
                cursor.execute("""
                    SELECT date, status
                    FROM attendance
                    WHERE employee_id = %s
                    ORDER BY date ASC
                """, (self.selected_employee_id,))
                data = cursor.fetchall()
                con.close()
        except Exception as e:
            print(e)

        if not data:
            QtWidgets.QMessageBox.information(self, "Нет данных", "Нет опозданий у сотрудника.")
            return

        for child in self.ui.report_area.children():
            if isinstance(child, QtWidgets.QWidget):
                child.deleteLater()

        table = QtWidgets.QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Дата", "Примечание"])
        table.setRowCount(len(data))

        for i, row in enumerate(data):
            table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(row["date"])))
            table.setItem(i, 1, QtWidgets.QTableWidgetItem(row["status"] or ""))

        table.resizeColumnsToContents()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(table)

        container = QtWidgets.QWidget(self.ui.report_area)
        container.setGeometry(10, 10, 920, 350)
        container.setLayout(layout)
        container.show()

    def plot_lateness_graph(self):
        if not self.selected_employee_id:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Сотрудник не выбран")
            return

        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT date
                    FROM attendance
                    WHERE employee_id = %s AND status = 'late'
                    ORDER BY date ASC
                """, (self.selected_employee_id,))
                rows = cursor.fetchall()
        finally:
            connection.close()

        if not rows:
            QtWidgets.QMessageBox.information(self, "Нет данных", "У выбранного сотрудника нет опозданий.")
            return

        # Подсчёт количества опозданий по датам
        from collections import Counter
        date_counts = Counter([row["date"].strftime("%d.%m") for row in rows])
        dates = sorted(date_counts.keys())
        counts = [date_counts[date] for date in dates]

        # Очистка предыдущего отчёта
        for child in self.ui.report_area.children():
            if isinstance(child, QtWidgets.QWidget):
                child.deleteLater()

        # Построение графика
        fig, ax = plt.subplots()
        ax.plot(dates, counts, marker='o', linestyle='-', color='blue')
        ax.set_title("Опоздания сотрудника по датам")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Кол-во опозданий")
        ax.grid(True)

        canvas = FigureCanvas(fig)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(canvas)

        container = QtWidgets.QWidget(self.ui.report_area)
        container.setGeometry(10, 10, 920, 350)
        container.setLayout(layout)
        container.show()
        self.show_lateness_table_for_employee()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = FireDialog(current_user_id=1)  # Передаем ID текущего пользователя
    window.show()
    sys.exit(app.exec())