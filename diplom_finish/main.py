# main.py
from PyQt6 import QtWidgets, QtCore
from ui.vhod import Ui_login_widget
from ui.registration_window import Ui_registration_widget
from ui.password_reset_window import Ui_PasswordResetWindow
from ui.admin_main_window import Ui_AdminMainWindow
from ui.hr_main_window import Ui_HRMainWindow
from db.db import get_connection, get_connection_for_auth
from datetime import datetime
from ui.candidate_main_window import CandidateWindow

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_login_widget()
        self.ui.setupUi(self)
        self.ui.to_register_button.clicked.connect(self.open_registration)
        self.ui.forgot_password_button.clicked.connect(self.open_password_reset)
        self.ui.login_button.clicked.connect(self.show_main_window)

    def open_registration(self):
        self.registration_window = RegistrationWindow()
        self.registration_window.show()
        self.hide()

    def open_password_reset(self):
        self.password_reset_window = PasswordResetWindow()
        self.password_reset_window.show()
        self.hide()

    def show_main_window(self):
        login = self.ui.login_email_input.text().strip()
        password = self.ui.login_password_input.text().strip()

        try:
            con = get_connection_for_auth()
            cur = con.cursor()
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            cur.execute("SELECT id, password_hash, role FROM users WHERE login = %s", (login,))
            result = cur.fetchone()

            if not result:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
                return

            user_id, stored_hash, role = result

            # Сравниваем хэши
            if password_hash != stored_hash:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
                return

                # Получаем выбранное время из виджета
            qtime = self.ui.time_input.time()
            timestamp = f"{datetime.now().date()} {qtime.hour():02d}:{qtime.minute():02d}:00"

            # Логирование входа с указанием времени
            from utils.logger import log_action
            log_action(
                user_id=user_id,
                action="Вход",
                description=f"Пользователь с ID {user_id} вошёл в систему",
                timestamp=timestamp
            )

            # Открытие окна по роли
            if role == 3:  # HR
                self.current_window = HR_Window()
            elif role == 1:  # Admin
                self.current_window = Adm_Window()
            elif role == 4:  # Кандидат
                self.current_window = CandidateWindow(user_id=user_id)
            elif role == 2:  # Employee
                try:
                    conn = get_connection()
                    with conn.cursor() as cursor:
                        # Получаем ID сотрудника
                        cursor.execute("SELECT id FROM employees WHERE user_id = %s", (user_id,))
                        employee_id = cursor.fetchone()[0]

                        # Получаем время из виджета
                        qtime = self.ui.time_input.time()
                        login_time = f"{qtime.hour():02d}:{qtime.minute():02d}:00"
                        current_date = datetime.now().date()

                        # Проверяем, есть ли уже запись за сегодня
                        cursor.execute("""
                                        SELECT id FROM attendance 
                                        WHERE employee_id = %s AND date = %s
                                    """, (employee_id, current_date))

                        if not cursor.fetchone():
                            # Определяем статус на основе времени
                            status = 'absent'  # по умолчанию
                            if qtime < QtCore.QTime(9, 0):
                                status = 'present'
                            elif qtime < QtCore.QTime(10, 0):
                                status = 'late'

                            # Добавляем запись о посещении
                            cursor.execute("""
                                            INSERT INTO attendance (employee_id, date, login_time, status, notes)
                                            VALUES (%s, %s, %s, %s, 'Автоматически создано при входе')
                                        """, (employee_id, current_date, login_time, status))
                            conn.commit()
                        conn.close()
                except Exception as e:
                    print(f"Ошибка при записи посещения: {e}")

                from ui.employee_account_window import EmployeeAccountWindow
                self.current_window = EmployeeAccountWindow(user_id=user_id)
            elif role == 5:
                from ui.FarewellWindow import ThankYouWindow
                self.current_window = ThankYouWindow()

            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Неизвестная роль")
                return

            self.current_window.show()
            self.hide()
            con.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"{e}")
            print(e)


class RegistrationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_registration_widget()
        self.ui.setupUi(self)
        self.ui.back_button.clicked.connect(self.return_to_login)

    def return_to_login(self):
        self.parent_window = LoginWindow()
        self.parent_window.show()
        self.close()


class PasswordResetWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_PasswordResetWindow()
        self.ui.setupUi(self)
        self.ui.back_button.clicked.connect(self.return_to_login)

    def return_to_login(self):
        self.parent_window = LoginWindow()
        self.parent_window.show()
        self.close()


class Adm_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AdminMainWindow()
        self.ui.setupUi(self)
        self.ui.exit_btn.clicked.connect(self.return_to_login)

    def return_to_login(self):
        self.parent_window = LoginWindow()
        self.parent_window.show()
        self.close()

class HR_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_HRMainWindow()
        self.ui.setupUi(self)
        self.ui.exit_btn.clicked.connect(self.return_to_login)

    def return_to_login(self):
        self.parent_window = LoginWindow()
        self.parent_window.show()
        self.close()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
