from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QMessageBox, QFrame, QSizePolicy
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from db.db import get_connection
from PyQt6 import QtCore


class MotivationWindow(QWidget):
    def __init__(self, employee_id: int, employee_name: str, created_by: int):
        super().__init__()
        self.setWindowTitle(f"Мотивация: {employee_name}")
        self.setFixedSize(600, 500)  # Увеличено для лучшего размещения элементов
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
            }
        """)

        self.employee_id = employee_id
        self.employee_name = employee_name
        self.created_by = created_by
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Карточка с белым фоном
        self.card = QFrame()
        self.card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            QLabel {
                color: #2c3e50;
            }
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(20)

        # Заголовок
        title = QLabel(f"Мотивация: {self.employee_name}")
        title.setFont(QFont("Arial", 18, weight=QFont.Weight.Bold))
        title.setStyleSheet("color: #ff6b6b; margin-bottom: 5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #ffe8e8;")
        separator.setFixedHeight(2)
        card_layout.addWidget(separator)

        # Тип мотивации
        type_layout = QVBoxLayout()
        type_layout.setSpacing(8)

        label_type = QLabel("Тип мотивации:")
        label_type.setFont(QFont("Arial", 12))
        label_type.setStyleSheet("color: #444; font-weight: bold;")
        type_layout.addWidget(label_type)

        self.motivation_type = QComboBox()
        self.motivation_type.setFixedHeight(40)
        self.motivation_type.setStyleSheet("""
            QComboBox {
                background-color: #fff;
                border: 1px solid #ff9a9e;
                border-radius: 8px;
                padding: 0 10px;
                color: #444;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.type_map = {
            "Премия (10%)": "bonus",
            "Обучение за счёт компании": "training",
            "Карьерный рост (повышение)": "promotion"
        }
        self.motivation_type.addItems(self.type_map.keys())
        type_layout.addWidget(self.motivation_type)
        card_layout.addLayout(type_layout)

        # Комментарий
        comment_layout = QVBoxLayout()
        comment_layout.setSpacing(8)

        comment_label = QLabel("Комментарий:")
        comment_label.setFont(QFont("Arial", 12))
        comment_label.setStyleSheet("color: #444; font-weight: bold;")
        comment_layout.addWidget(comment_label)

        self.comment = QTextEdit()
        self.comment.setPlaceholderText("Например: 'Выдана премия за досрочную сдачу проекта'")
        self.comment.setStyleSheet("""
            QTextEdit {
                background-color: #fff;
                border: 1px solid #ff9a9e;
                border-radius: 8px;
                padding: 10px;
                color: #444;
            }
        """)
        self.comment.setFixedHeight(120)
        comment_layout.addWidget(self.comment)
        card_layout.addLayout(comment_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.submit_btn = self.create_button("💾 Сохранить", "#ff6b6b", "#ff8e8e")
        self.cancel_btn = self.create_button("❌ Отмена", "#fad0c4", "#ffd6d6")

        self.submit_btn.clicked.connect(self.save_motivation)
        self.cancel_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.cancel_btn)
        card_layout.addLayout(btn_layout)

        main_layout.addWidget(self.card)

    def create_button(self, text, color, hover_color):
        btn = QPushButton(text)
        btn.setFont(QFont("Arial", 12, weight=QFont.Weight.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                color: #ff6b6b;
            }}
        """)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setFixedHeight(45)
        return btn

    def save_motivation(self):
        action_type = self.type_map[self.motivation_type.currentText()]
        reason = self.comment.toPlainText().strip()

        if not reason:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, укажите комментарий.")
            return

        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO motivation_actions (employee_id, action_type, reason, created_by)
                        VALUES (%s, %s, %s, %s)
                    """, (self.employee_id, action_type, reason, self.created_by))
                    conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить мотивацию:\n{e}")
            return

        QMessageBox.information(self, "Успешно", f"Мотивация для {self.employee_name} сохранена.")
        self.close()