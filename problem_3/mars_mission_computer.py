import random  # 랜덤 값 생성을 위한 모듈
from datetime import datetime  # 현재 날짜/시간을 가져오기 위한 모듈


class DummySensor:
    def __init__(self):
        # 센서 데이터를 저장할 딕셔너리 초기화
        # 각 키는 센서 항목, 값은 초기값(0.0)
        self.env_values = {
            "mars_base_internal_temperature": 0.0,   # 내부 온도
            "mars_base_external_temperature": 0.0,   # 외부 온도
            "mars_base_internal_humidity": 0.0,      # 내부 습도
            "mars_base_external_illuminance": 0.0,   # 외부 광량
            "mars_base_internal_co2": 0.0,           # 내부 CO2 농도
            "mars_base_internal_oxygen": 0.0,        # 내부 산소 농도
        }

    def set_env(self):
        # 각 센서 값들을 지정된 범위 내에서 랜덤으로 생성하여 저장

        # 내부 온도 (18 ~ 30도)
        self.env_values["mars_base_internal_temperature"] = round(random.uniform(18, 30), 2)

        # 외부 온도 (0 ~ 21도)
        self.env_values["mars_base_external_temperature"] = round(random.uniform(0, 21), 2)

        # 내부 습도 (50 ~ 60%)
        self.env_values["mars_base_internal_humidity"] = round(random.uniform(50, 60), 2)

        # 외부 광량 (500 ~ 715 W/m2)
        self.env_values["mars_base_external_illuminance"] = round(random.uniform(500, 715), 2)

        # 내부 CO2 농도 (0.02 ~ 0.1%)
        self.env_values["mars_base_internal_co2"] = round(random.uniform(0.02, 0.1), 4)

        # 내부 산소 농도 (4 ~ 7%)
        self.env_values["mars_base_internal_oxygen"] = round(random.uniform(4, 7), 2)

    def get_env(self):
        # 현재 시간을 문자열 형태로 가져옴 (로그 기록용)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 센서 데이터를 한 줄의 문자열(log)로 생성
        log_line = (
            f"{now}, "  # 날짜 및 시간
            f"{self.env_values['mars_base_internal_temperature']}°C, "  # 내부 온도
            f"{self.env_values['mars_base_external_temperature']}°C, "  # 외부 온도
            f"{self.env_values['mars_base_internal_humidity']}%, "      # 내부 습도
            f"{self.env_values['mars_base_external_illuminance']} W/m2, "  # 외부 광량
            f"{self.env_values['mars_base_internal_co2']}%, "           # CO2 농도
            f"{self.env_values['mars_base_internal_oxygen']}%\n"        # 산소 농도 + 줄바꿈
        )

        # 로그 파일에 기록 (append 모드 → 기존 내용 유지 + 뒤에 추가)
        with open("./problem_3/mars_log.txt", "a") as file:
            file.write(log_line)

        # 현재 센서 값 반환
        return self.env_values


# 이 파일을 직접 실행했을 때만 아래 코드 실행
if __name__ == "__main__":
    # DummySensor 객체 생성
    ds = DummySensor()

    # 랜덤 환경 값 설정
    ds.set_env()

    # 환경 값 가져오기 (동시에 로그 파일에도 기록됨)
    env = ds.get_env()

    # 콘솔에 출력
    print("현재 환경 값:")
    for key, value in env.items():
        print(f"{key}: {value}")