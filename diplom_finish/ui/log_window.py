from PyQt6 import QtWidgets, QtCore
from db.db import get_connection


class LogWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Журнал действий")
        self.setFixedSize(1000, 600)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # Основной фон
        self.background = QtWidgets.QFrame(self.centralwidget)
        self.background.setGeometry(0, 0, 1000, 600)
        self.background.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
                border-radius: 10px;}
        """)

        # Заголовок
        self.title_label = QtWidgets.QLabel("Журнал действий пользователей", self.background)
        self.title_label.setGeometry(30, 20, 600, 40)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

        # Фильтрация
        self.filter_frame = QtWidgets.QFrame(self.background)
        self.filter_frame.setGeometry(30, 70, 940, 60)
        self.filter_frame.setStyleSheet("background-color: rgba(255,255,255,0.9); border-radius: 10px;")

        self.user_input = QtWidgets.QLineEdit(self.filter_frame)
        self.user_input.setPlaceholderText("Поиск по логину / описанию")
        self.user_input.setGeometry(20, 10, 250, 40)

        self.search_button = QtWidgets.QPushButton("🔍 Найти", self.filter_frame)
        self.search_button.setGeometry(310, 10, 100, 40)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #fcb1b6;
                color: white;
                border-radius: 20px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #7ddf94;
            }
            
            
        """)

        # Таблица
        self.table = QtWidgets.QTableWidget(self.background)
        self.table.setGeometry(30, 150, 940, 360)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Дата", "Пользователь", "Действие", "Описание"])
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

        # Назад
        self.back_button = QtWidgets.QPushButton("← Назад", self.background)
        self.back_button.setGeometry(30, 540, 100, 40)
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
        self.back_button.clicked.connect(self.close)

        # ✕ Закрыть
        self.exit_button = QtWidgets.QPushButton("✕", self)
        self.exit_button.setGeometry(960, 10, 30, 30)
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
        self.exit_button.clicked.connect(self.close)

        # Логика
        self.setup_table()
        self.setup_connections()
        self.load_logs()

    def setup_connections(self):
        self.search_button.clicked.connect(self.apply_filters)
        self.user_input.textChanged.connect(self.apply_filters)


    def setup_table(self):
        self.table.setColumnWidth(0, 150)  # Дата
        self.table.setColumnWidth(1, 200)  # Пользователь
        self.table.setColumnWidth(2, 150)  # Действие
        self.table.setColumnWidth(3, 400)  # Описание

    def load_logs(self):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        l.created_at,
                        u.login,
                        l.action,
                        l.description
                    FROM logs l
                    LEFT JOIN users u ON l.user_id = u.id
                    ORDER BY l.created_at DESC
                """)
                self.all_logs = cursor.fetchall()
                self.apply_filters()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки: {str(e)}")
            print(e)
        finally:
            connection.close()

    def apply_filters(self):
        search_text = self.user_input.text().lower()

        filtered = []

        for log in self.all_logs:
            if search_text:
                if (search_text not in (log["login"] or "").lower() and
                        search_text not in (log["description"] or "").lower()):
                    continue


            filtered.append(log)

        self.update_table(filtered)

    def update_table(self, logs):
        self.table.setRowCount(0)

        for row_idx, log in enumerate(logs):
            self.table.insertRow(row_idx)
            created_at = log["created_at"].strftime("%d.%m.%Y %H:%M")
            self.table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(created_at))
            self.table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(log["login"] or "Система"))
            self.table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(log["action"]))
            self.table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(log["description"] or "-"))


# Тестовый запуск
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = LogWindow()
    window.show()
    sys.exit(app.exec())
