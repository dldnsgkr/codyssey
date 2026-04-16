import json       # 딕셔너리를 JSON 형식 문자열로 변환하여 출력할 때 사용
import platform   # 운영체계, CPU 타입 등 시스템 기본 정보를 가져올 때 사용
import threading  # 센서 출력과 키 입력 감지를 동시에 처리하기 위한 쓰레드 모듈
import time       # 5초 대기(sleep)를 위해 사용

import psutil  # CPU 코어 수, 메모리 크기 등 상세 시스템 정보 수집용 외부 라이브러리

from problem_3.mars_mission_computer import DummySensor  # 화성 환경 센서 시뮬레이터


class MissionComputer:
    """화성 기지의 환경 데이터 및 시스템 정보를 관리하는 클래스."""

    def __init__(self):
        # 센서로부터 읽어온 환경 값을 저장하는 딕셔너리 (초기값 0.0)
        self.env_values = {
            'mars_base_internal_temperature': 0.0,  # 기지 내부 온도 (°C)
            'mars_base_external_temperature': 0.0,  # 기지 외부 온도 (°C)
            'mars_base_internal_humidity': 0.0,     # 기지 내부 습도 (%)
            'mars_base_external_illuminance': 0.0,  # 외부 조도 (W/m²)
            'mars_base_internal_co2': 0.0,          # 내부 CO₂ 농도 (%)
            'mars_base_internal_oxygen': 0.0,       # 내부 산소 농도 (%)
        }

        # 화성 환경 센서 시뮬레이터 인스턴스 생성
        self.ds = DummySensor()

        # 5분 평균 계산을 위해 수집된 데이터를 순서대로 저장하는 리스트
        self.history = []

        # 프로그램 실행 여부를 제어하는 플래그 (False 로 바뀌면 루프 종료)
        self.running = True

    def stop_listener(self):
        """
        별도 쓰레드에서 실행되며 사용자 키 입력을 감지한다.
        'q' 를 입력하면 running 플래그를 False 로 바꿔 메인 루프를 종료시킨다.
        """
        while True:
            user_input = input()

            # 소문자 변환 후 'q' 여부 확인 → 대소문자 모두 허용
            if user_input.lower() == 'q':
                self.running = False
                print('\nSystem stopped...')
                break

    def get_sensor_data(self):
        """
        5초 간격으로 센서 데이터를 읽어 JSON 형태로 출력한다.
        데이터가 60회 누적되면(= 5분 경과) 평균값을 출력하고 기록을 초기화한다.
        """
        print('실행 중... (종료하려면 q 입력)')

        # 키 입력 감지를 위한 보조 쓰레드 시작
        # daemon=True: 메인 프로그램 종료 시 자동으로 함께 종료
        input_thread = threading.Thread(target=self.stop_listener, daemon=True)
        input_thread.start()

        while self.running:
            # 센서 값을 새로운 난수로 갱신
            self.ds.set_env()

            # 갱신된 센서 값을 딕셔너리로 가져와 저장 (.copy() 로 참조가 아닌 복사본 저장)
            self.env_values = self.ds.get_env().copy()

            # 현재 센서 값을 JSON 형식으로 출력
            print(json.dumps(self.env_values, indent=4))

            # 평균 계산용 히스토리에 현재 값을 추가
            self.history.append(self.env_values.copy())

            # 60회(5분) 누적 시 평균 출력 후 기록 초기화
            if len(self.history) >= 60:
                self.print_average()
                self.history.clear()

            # 다음 측정까지 5초 대기
            time.sleep(5)

    def print_average(self):
        """
        history 에 저장된 데이터를 기반으로 각 항목의 평균값을 계산하고
        JSON 형태로 출력한다.
        """
        avg_values = {}

        # 각 센서 항목별로 전체 합산 후 개수로 나눠 평균 산출
        for key in self.env_values:
            total = sum(item[key] for item in self.history)
            avg_values[key] = round(total / len(self.history), 2)

        print('\n===== 5분 평균 값 =====')
        print(json.dumps(avg_values, indent=4))
        print('=====================\n')

    def get_mission_computer_info(self, settings=None):
        """
        미션 컴퓨터의 시스템 정보를 수집하여 JSON 형식으로 출력한다.
        각 항목은 독립적으로 예외처리되어, 수집 실패 시 오류 메시지를 대신 출력한다.

        수집 항목:
            os           - 운영체계 이름 (예: Darwin, Windows, Linux)
            os_version   - 운영체계 세부 버전 문자열
            cpu_type     - CPU 아키텍처/모델명
            cpu_cores    - CPU 물리 코어 수
            memory_total - 전체 메모리 크기 (GB 단위)

        Args:
            settings: 출력할 항목 키 목록. None 이면 전체 항목을 출력한다.
        """
        all_info = {}

        # 운영체계 이름 수집 (예: 'Darwin', 'Windows', 'Linux')
        try:
            all_info['os'] = platform.system()
        except Exception as e:
            all_info['os'] = f'Error: {e}'

        # 운영체계 세부 버전 문자열 수집
        try:
            all_info['os_version'] = platform.version()
        except Exception as e:
            all_info['os_version'] = f'Error: {e}'

        # CPU 아키텍처 또는 모델명 수집
        try:
            all_info['cpu_type'] = platform.processor()
        except Exception as e:
            all_info['cpu_type'] = f'Error: {e}'

        # CPU 물리 코어 수 수집 (논리 코어 제외)
        try:
            all_info['cpu_cores'] = psutil.cpu_count(logical=False)
        except Exception as e:
            all_info['cpu_cores'] = f'Error: {e}'

        # 전체 메모리 크기 수집 후 바이트 → GB 단위로 변환
        try:
            total_bytes = psutil.virtual_memory().total
            all_info['memory_total'] = f'{total_bytes / (1024 ** 3):.2f} GB'
        except Exception as e:
            all_info['memory_total'] = f'Error: {e}'

        # settings 가 None 이면 전체 출력, 아니면 settings 에 있는 키만 필터링
        if settings is None:
            info = all_info
        else:
            info = {k: v for k, v in all_info.items() if k in settings}

        print(json.dumps(info, indent=4, ensure_ascii=False))

    def get_mission_computer_load(self, settings=None):
        """
        미션 컴퓨터의 실시간 부하 정보를 수집하여 JSON 형식으로 출력한다.
        각 항목은 독립적으로 예외처리되어, 수집 실패 시 오류 메시지를 대신 출력한다.

        수집 항목:
            cpu_usage    - CPU 실시간 사용률 (%)
            memory_usage - 메모리 실시간 사용률 (%)

        Args:
            settings: 출력할 항목 키 목록. None 이면 전체 항목을 출력한다.
        """
        all_load = {}

        # CPU 사용률 수집 (interval=1: 1초 간격으로 측정한 평균값)
        try:
            all_load['cpu_usage'] = f'{psutil.cpu_percent(interval=1):.1f} %'
        except Exception as e:
            all_load['cpu_usage'] = f'Error: {e}'

        # 메모리 사용률 수집 (사용 중인 메모리 / 전체 메모리 × 100)
        try:
            all_load['memory_usage'] = f'{psutil.virtual_memory().percent:.1f} %'
        except Exception as e:
            all_load['memory_usage'] = f'Error: {e}'

        # settings 가 None 이면 전체 출력, 아니면 settings 에 있는 키만 필터링
        if settings is None:
            load = all_load
        else:
            load = {k: v for k, v in all_load.items() if k in settings}

        print(json.dumps(load, indent=4, ensure_ascii=False))


# 이 파일을 직접 실행할 때만 아래 코드가 동작한다 (모듈로 import 시에는 실행되지 않음)
if __name__ == '__main__':
    run_computer = MissionComputer()
    run_computer.get_sensor_data()
