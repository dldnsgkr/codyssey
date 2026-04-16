import os  # setting.txt 경로를 동적으로 구성할 때 사용

# problem_4 에서 완성한 MissionComputer 클래스를 가져온다
# (시스템 정보 메서드 get_mission_computer_info, get_mission_computer_load 포함)
from problem_4.mars_mission_computer import MissionComputer


# setting.txt 가 없거나 비어 있을 때 사용할 기본 출력 항목
DEFAULT_INFO_KEYS = ['os', 'os_version', 'cpu_type', 'cpu_cores', 'memory_total']
DEFAULT_LOAD_KEYS = ['cpu_usage', 'memory_usage']


def load_settings():
    """
    이 파일과 같은 폴더에 있는 setting.txt 를 읽어 출력 항목 키 목록을 반환한다.

    규칙:
        - '#' 으로 시작하는 줄은 주석으로 간주하고 무시한다.
        - 빈 줄도 무시한다.
        - 파일이 존재하지 않거나 유효한 항목이 없으면 기본값(전체 항목)을 반환한다.

    Returns:
        list: 출력할 항목 키 문자열의 리스트
    """
    # 이 스크립트가 위치한 폴더를 기준으로 setting.txt 경로를 구성
    setting_path = os.path.join(os.path.dirname(__file__), 'setting.txt')

    try:
        with open(setting_path, 'r', encoding='utf-8') as f:
            # 주석과 빈 줄을 제거한 항목만 추출
            keys = [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith('#')
            ]

        # 유효한 항목이 하나라도 있으면 그 목록을 반환
        if keys:
            return keys

    except FileNotFoundError:
        # setting.txt 가 없을 경우 기본값으로 폴백
        pass

    # 파일이 없거나 항목이 비어 있을 경우 전체 항목을 기본값으로 반환
    return DEFAULT_INFO_KEYS + DEFAULT_LOAD_KEYS


# 이 파일을 직접 실행할 때만 아래 코드가 동작한다 (모듈로 import 시에는 실행되지 않음)
if __name__ == '__main__':
    # MissionComputer 인스턴스 생성
    runComputer = MissionComputer()

    # setting.txt 에서 출력할 항목 목록을 불러옴
    settings = load_settings()

    # 시스템 정보 출력 (운영체계, CPU 타입/코어, 메모리 등)
    print('===== 시스템 정보 =====')
    runComputer.get_mission_computer_info(settings)

    # 실시간 부하 출력 (CPU 사용률, 메모리 사용률)
    print('\n===== 시스템 부하 =====')
    runComputer.get_mission_computer_load(settings)
