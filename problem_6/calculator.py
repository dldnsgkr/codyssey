import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QPushButton,
    QLineEdit,
    QVBoxLayout
)
from PyQt6.QtCore import Qt


class Calculator(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Calculator')
        self.setFixedSize(300, 400)

        self.expression = ''

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 디스플레이
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(60)

        main_layout.addWidget(self.display)

        # 버튼 레이아웃
        grid = QGridLayout()

        buttons = [
            ('AC', 0, 0), ('+/-', 0, 1), ('%', 0, 2), ('/', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('*', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3)
        ]

        for btn in buttons:
            if len(btn) == 3:
                text, row, col = btn
                button = QPushButton(text)
                button.clicked.connect(self.on_click)
                grid.addWidget(button, row, col)
            else:
                text, row, col, rowspan, colspan = btn
                button = QPushButton(text)
                button.clicked.connect(self.on_click)
                grid.addWidget(button, row, col, rowspan, colspan)

        main_layout.addLayout(grid)
        self.setLayout(main_layout)

    def on_click(self):
        sender = self.sender()
        text = sender.text()

        if text == 'AC':
            self.expression = ''
            self.display.setText('')

        elif text == '=':
            try:
                result = str(eval(self.expression))
                self.display.setText(result)
                self.expression = result
            except Exception:
                self.display.setText('Error')
                self.expression = ''

        elif text == '+/-':
            if self.expression:
                if self.expression.startswith('-'):
                    self.expression = self.expression[1:]
                else:
                    self.expression = '-' + self.expression
                self.display.setText(self.expression)

        elif text == '%':
            try:
                self.expression = str(float(self.expression) / 100)
                self.display.setText(self.expression)
            except Exception:
                self.display.setText('Error')
                self.expression = ''

        else:
            self.expression += text
            self.display.setText(self.expression)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())