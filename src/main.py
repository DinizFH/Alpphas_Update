import sys
import _mysql_connector
from PySide6.QtWidgets import QApplication

from style import ESTILO_GLOBAL
from dashboard_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(ESTILO_GLOBAL)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
