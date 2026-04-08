import time  # 시간 제어 (5초 대기)
import json  # JSON 형태 출력
import threading  # 사용자 입력을 별도로 받기 위한 쓰레드

from problem_3.mars_mission_computer import DummySensor

"""
📌 Thread(쓰레드)란?

쓰레드는 하나의 프로그램 안에서 여러 작업을 동시에 실행하기 위한 기술이다.
기본적으로 Python 프로그램은 한 번에 하나의 작업만 순차적으로 실행된다.

하지만 이 코드에서는 두 가지 작업이 동시에 필요하다:
1. 센서 데이터를 5초마다 계속 출력하는 작업
2. 사용자 입력(q)을 받아 프로그램을 종료하는 작업

만약 input()을 메인 루프에서 사용하면,
사용자 입력을 기다리는 동안 센서 데이터 출력이 멈추는 문제가 발생한다.

이를 해결하기 위해 쓰레드를 사용한다.

---

📌 현재 코드에서의 쓰레드 역할

- 메인 쓰레드:
  → 센서 데이터를 5초마다 계속 출력

- 보조 쓰레드 (stop_listener):
  → 사용자 입력을 계속 대기하다가 'q' 입력 시 프로그램 종료

---

📌 daemon=True 옵션

쓰레드를 생성할 때 daemon=True로 설정하면,
메인 프로그램이 종료될 때 해당 쓰레드도 함께 종료된다.

즉, 프로그램 종료 시 별도로 쓰레드를 정리하지 않아도 된다.

---

📌 정리

쓰레드를 사용함으로써
"출력 작업"과 "입력 감지 작업"을 동시에 수행할 수 있게 된다.
"""

class MissionComputer:
    """
    화성 기지의 환경 데이터를 관리하고 출력하는 클래스
    """

    def __init__(self):
        # 🔹 현재 환경 값 저장용 딕셔너리
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0,
        }

        # 🔹 DummySensor 인스턴스 생성 (센서 역할)
        self.ds = DummySensor()

        # 🔹 최근 데이터 저장 (5분 평균 계산용)
        self.history = []

        # 🔹 프로그램 실행 상태 (True: 실행, False: 종료)
        self.running = True

    def stop_listener(self):
        """
        사용자 입력을 감지하는 함수 (별도 쓰레드에서 실행)
        특정 키(q)를 입력하면 프로그램 종료
        """
        while True:
            user_input = input()

            # 'q' 입력 시 프로그램 종료
            if user_input.lower() == 'q':
                self.running = False
                print('\nSystem stopped...')
                break

    def get_sensor_data(self):
        """
        센서 데이터를 주기적으로 가져와 출력하는 메소드
        - 5초마다 실행
        - JSON 형태로 출력
        - 5분마다 평균값 출력
        """

        print('실행 중... (종료하려면 q 입력)')

        # 🔹 사용자 입력을 별도로 받기 위한 쓰레드 실행
        input_thread = threading.Thread(target=self.stop_listener, daemon=True)
        input_thread.start()

        # 🔹 프로그램이 실행 중일 때 반복
        while self.running:
            # 1️⃣ 센서 값 업데이트
            self.ds.set_env()

            # 2️⃣ 센서 값 가져오기
            sensor_data = self.ds.get_env()

            # 3️⃣ env_values에 저장 (깊은 복사)
            self.env_values = sensor_data.copy()

            # 4️⃣ JSON 형태로 출력
            print(json.dumps(self.env_values, indent=4))

            # 5️⃣ 평균 계산을 위해 데이터 저장
            self.history.append(self.env_values.copy())

            # 6️⃣ 5분(5초 * 60회)마다 평균 출력
            if len(self.history) >= 60:
                self.print_average()
                self.history.clear()

            # 7️⃣ 5초 대기
            time.sleep(5)

    def print_average(self):
        """
        최근 5분간의 평균값을 계산하여 출력하는 함수
        """
        avg_values = {}

        # 🔹 각 환경 값에 대해 평균 계산
        for key in self.env_values:
            total = 0
            for item in self.history:
                total += item[key]

            avg_values[key] = round(total / len(self.history), 2)

        # 🔹 평균값 출력
        print('\n===== 5분 평균 값 =====')
        print(json.dumps(avg_values, indent=4))
        print('=====================\n')


# 🔹 프로그램 실행 진입점
if __name__ == '__main__':
    # MissionComputer 인스턴스 생성
    run_computer = MissionComputer()

    # 센서 데이터 출력 시작
    run_computer.get_sensor_data()