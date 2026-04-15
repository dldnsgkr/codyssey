import json
import os
import platform
import time
import threading

import psutil

from problem_4.mars_mission_computer import MissionComputer as MissionComputerBase


# setting.txt에서 출력 항목을 불러오는 기본 키 목록
DEFAULT_INFO_KEYS = ['os', 'os_version', 'cpu_type', 'cpu_cores', 'memory_total']
DEFAULT_LOAD_KEYS = ['cpu_usage', 'memory_usage']


class MissionComputer(MissionComputerBase):
    """
    화성 기지 미션 컴퓨터 관리 클래스.
    기존 센서 데이터 수집 기능에 더해 시스템 정보 및 부하 조회 기능을 추가한다.
    """

    def __init__(self):
        super().__init__()
        self.settings = self._load_settings()

    def _load_settings(self):
        """
        setting.txt 파일에서 출력 항목 키 목록을 불러온다.
        파일이 없거나 비어 있으면 기본값을 반환한다.
        """
        setting_path = os.path.join(os.path.dirname(__file__), 'setting.txt')
        try:
            with open(setting_path, 'r', encoding='utf-8') as f:
                keys = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith('#')
                ]
            if keys:
                return keys
        except FileNotFoundError:
            pass
        return DEFAULT_INFO_KEYS + DEFAULT_LOAD_KEYS

    def get_mission_computer_info(self):
        """
        미션 컴퓨터의 시스템 정보를 수집하여 JSON 형식으로 출력한다.

        수집 항목 (setting.txt 에서 선택 가능):
            - os           : 운영체계
            - os_version   : 운영체계 버전
            - cpu_type     : CPU 타입
            - cpu_cores    : CPU 코어 수
            - memory_total : 메모리 크기 (GB)
        """
        info = {}

        if 'os' in self.settings:
            try:
                info['os'] = platform.system()
            except Exception as e:
                info['os'] = f'Error: {e}'

        if 'os_version' in self.settings:
            try:
                info['os_version'] = platform.version()
            except Exception as e:
                info['os_version'] = f'Error: {e}'

        if 'cpu_type' in self.settings:
            try:
                info['cpu_type'] = platform.processor()
            except Exception as e:
                info['cpu_type'] = f'Error: {e}'

        if 'cpu_cores' in self.settings:
            try:
                info['cpu_cores'] = psutil.cpu_count(logical=False)
            except Exception as e:
                info['cpu_cores'] = f'Error: {e}'

        if 'memory_total' in self.settings:
            try:
                total_bytes = psutil.virtual_memory().total
                info['memory_total'] = f'{total_bytes / (1024 ** 3):.2f} GB'
            except Exception as e:
                info['memory_total'] = f'Error: {e}'

        print(json.dumps(info, indent=4, ensure_ascii=False))

    def get_mission_computer_load(self):
        """
        미션 컴퓨터의 실시간 부하 정보를 수집하여 JSON 형식으로 출력한다.

        수집 항목 (setting.txt 에서 선택 가능):
            - cpu_usage    : CPU 실시간 사용량 (%)
            - memory_usage : 메모리 실시간 사용량 (%)
        """
        load = {}

        if 'cpu_usage' in self.settings:
            try:
                load['cpu_usage'] = f'{psutil.cpu_percent(interval=1):.1f} %'
            except Exception as e:
                load['cpu_usage'] = f'Error: {e}'

        if 'memory_usage' in self.settings:
            try:
                load['memory_usage'] = f'{psutil.virtual_memory().percent:.1f} %'
            except Exception as e:
                load['memory_usage'] = f'Error: {e}'

        print(json.dumps(load, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    runComputer = MissionComputer()

    print('===== 시스템 정보 =====')
    runComputer.get_mission_computer_info()

    print('\n===== 시스템 부하 =====')
    runComputer.get_mission_computer_load()
