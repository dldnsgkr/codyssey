import sys
# PyQt6에서 UI 구성에 필요한 위젯들 import
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QPushButton,
    QLineEdit,
    QVBoxLayout
)
# 정렬 옵션 등을 위한 Qt 모듈 import
from PyQt6.QtCore import Qt


# 계산기 UI를 구성하는 클래스
class Calculator(QWidget):
    def __init__(self):
        super().__init__()

        # 창 제목 설정
        self.setWindowTitle('Calculator')
        # 창 크기 고정
        self.setFixedSize(300, 400)

        # 사용자가 입력한 수식을 저장하는 변수
        self.expression = ''

        # UI 초기화 함수 호출
        self.init_ui()

    # UI 구성 함수
    def init_ui(self):
        # 전체 레이아웃 (세로)
        main_layout = QVBoxLayout()

        # -------------------------
        # 디스플레이 영역 (숫자 출력)
        # -------------------------
        self.display = QLineEdit()
        # 텍스트를 오른쪽 정렬 (아이폰 계산기처럼)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        # 사용자가 직접 입력하지 못하도록 설정
        self.display.setReadOnly(True)
        # 높이 설정
        self.display.setFixedHeight(60)

        # 메인 레이아웃에 디스플레이 추가
        main_layout.addWidget(self.display)

        # -------------------------
        # 버튼 영역 (Grid Layout)
        # -------------------------
        grid = QGridLayout()

        # 버튼 리스트 (텍스트, 행, 열, [옵션: 행span, 열span])
        buttons = [
            ('AC', 0, 0), ('+/-', 0, 1), ('%', 0, 2), ('/', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('*', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            # 0 버튼은 가로로 2칸 차지
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3)
        ]

        # 버튼 생성 및 배치
        for btn in buttons:
            # 일반 버튼 (행, 열만 있는 경우)
            if len(btn) == 3:
                text, row, col = btn
                button = QPushButton(text)
                # 버튼 클릭 시 on_click 함수 실행
                button.clicked.connect(self.on_click)
                grid.addWidget(button, row, col)
            # span이 있는 버튼 (0 버튼)
            else:
                text, row, col, rowspan, colspan = btn
                button = QPushButton(text)
                button.clicked.connect(self.on_click)
                grid.addWidget(button, row, col, rowspan, colspan)

        # 메인 레이아웃에 버튼 그리드 추가
        main_layout.addLayout(grid)
        self.setLayout(main_layout)

    # 버튼 클릭 시 실행되는 함수
    def on_click(self):
        # 어떤 버튼이 눌렸는지 확인
        sender = self.sender()
        text = sender.text()

        # 전체 초기화
        if text == 'AC':
            self.expression = ''
            self.display.setText('')

        # '=' 버튼 (계산 실행)
        elif text == '=':
            try:
                # eval을 사용하여 수식 계산
                result = str(eval(self.expression))
                self.display.setText(result)
                # 결과를 다시 expression에 저장
                self.expression = result
            except Exception:
                # 잘못된 수식 처리
                self.display.setText('Error')
                self.expression = ''

        # +/- 버튼 (부호 변경)
        elif text == '+/-':
            if self.expression:
                if self.expression.startswith('-'):
                    self.expression = self.expression[1:]
                else:
                    self.expression = '-' + self.expression
                self.display.setText(self.expression)

        # % 버튼 (백분율 계산)
        elif text == '%':
            try:
                self.expression = str(float(self.expression) / 100)
                self.display.setText(self.expression)
            except Exception:
                self.display.setText('Error')
                self.expression = ''

        # 숫자 및 연산자 입력
        else:
            self.expression += text
            self.display.setText(self.expression)


# 프로그램 실행 진입점
if __name__ == '__main__':
    # QApplication 객체 생성
    app = QApplication(sys.argv)
    # 계산기 인스턴스 생성
    calc = Calculator()
    # 화면에 표시
    calc.show()
    # 이벤트 루프 실행
    sys.exit(app.exec())