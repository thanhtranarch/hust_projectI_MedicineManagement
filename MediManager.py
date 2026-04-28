import sys
from PyQt6.QtWidgets import QApplication
from app_context import AppContext
from screens.auth import AuthDialog
from screens.maindashboard import MainWindow

def main():
    app = QApplication(sys.argv)
    context = AppContext()

    login_dialog = AuthDialog(context)
    if login_dialog.exec() == AuthDialog.DialogCode.Accepted:
        main_window = MainWindow(context)
        main_window.show()
        sys.exit(app.exec())

if __name__ == '__main__':
    main()
