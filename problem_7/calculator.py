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


class Calculator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.current = '0'
        self.operator = None
        self.operand = None
        self.waiting_for_new = False

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError
        return a / b

    def percent(self):
        try:
            self.current = str(float(self.current) / 100)
        except Exception:
            self.current = 'Error'

    def negative_positive(self):
        if self.current.startswith('-'):
            self.current = self.current[1:]
        else:
            if self.current != '0':
                self.current = '-' + self.current

    def input_number(self, num):
        if self.waiting_for_new:
            self.current = num
            self.waiting_for_new = False
        else:
            if self.current == '0':
                self.current = num
            else:
                self.current += num

    def input_dot(self):
        if '.' not in self.current:
            self.current += '.'

    def set_operator(self, op):
        if self.operator and not self.waiting_for_new:
            self.equal()

        self.operand = float(self.current)
        self.operator = op
        self.waiting_for_new = True

    def equal(self):
        if self.operator is None or self.operand is None:
            return

        try:
            a = self.operand
            b = float(self.current)

            if self.operator == '+':
                result = self.add(a, b)
            elif self.operator == '-':
                result = self.subtract(a, b)
            elif self.operator == '*':
                result = self.multiply(a, b)
            elif self.operator == '/':
                result = self.divide(a, b)

            # 소수점 6자리 반올림
            result = round(result, 6)

            self.current = str(result)
            self.operator = None
            self.operand = None

        except Exception:
            self.current = 'Error'

    def get_display(self):
        return self.current


class CalculatorUI(QWidget):
    def __init__(self):
        super().__init__()

        self.calc = Calculator()

        self.setWindowTitle('Calculator')
        self.setFixedSize(300, 400)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(60)

        main_layout.addWidget(self.display)

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

        self.update_display()

    def on_click(self):
        sender = self.sender()
        text = sender.text()

        if text.isdigit():
            self.calc.input_number(text)

        elif text == '.':
            self.calc.input_dot()

        elif text in ['+', '-', '*', '/']:
            self.calc.set_operator(text)

        elif text == '=':
            self.calc.equal()

        elif text == 'AC':
            self.calc.reset()

        elif text == '+/-':
            self.calc.negative_positive()

        elif text == '%':
            self.calc.percent()

        self.update_display()

    def update_display(self):
        text = self.calc.get_display()

        # 길이에 따라 폰트 크기 조정 (보너스)
        length = len(text)
        if length <= 6:
            size = 24
        elif length <= 10:
            size = 18
        else:
            size = 14

        self.display.setStyleSheet(f'font-size: {size}px;')
        self.display.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = CalculatorUI()
    ui.show()
    sys.exit(app.exec())