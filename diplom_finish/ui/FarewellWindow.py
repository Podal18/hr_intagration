from PyQt6 import QtWidgets, QtCore, QtGui

class ThankYouWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Спасибо!")
        self.setFixedSize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4)
            }
        """)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        label = QtWidgets.QLabel("Мы ценим ваш вклад и надеемся на сотрудничество в будущем!")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2d3436;")
        layout.addWidget(label)

        animation = QtGui.QMovie("heart.gif")
        anim_label = QtWidgets.QLabel()
        anim_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        anim_label.setMovie(animation)
        animation.start()
        layout.addWidget(anim_label)

        btn = QtWidgets.QPushButton("Вернуться к авторизации")
        btn.clicked.connect(self.return_to_login)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #6c5ce7;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 14px;
            }
        """)
        layout.addWidget(btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

    def return_to_login(self):
        from main import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
