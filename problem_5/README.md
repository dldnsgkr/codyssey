# Problem 5 - 미션 컴퓨터 시스템 정보 조회

## 개요

화성 기지 미션 컴퓨터가 원인 불명으로 간헐적 다운 현상을 일으키고 있다.  
컴퓨터는 완전 밀봉 상태로 물리적 점검이 불가능하기 때문에,  
**Python 코드로 시스템 상태를 읽어내는 기능**을 구현하여 문제를 진단한다.

---

## 파일 구조

```
problem_5/
├── mars_mission_computer.py   # 실행 진입점 — setting.txt 로드 후 시스템 정보 출력
├── setting.txt                # 출력할 항목을 직접 설정하는 설정 파일
├── __init__.py                # 이 폴더를 Python 패키지로 인식시키는 파일
├── __pycache__/               # Python 이 자동 생성하는 컴파일 캐시 폴더
└── README.md                  # 현재 문서

problem_4/
├── mars_mission_computer.py   # MissionComputer 클래스 본체 (시스템 정보 메서드 포함)
├── __init__.py                # 이 폴더를 Python 패키지로 인식시키는 파일
└── __pycache__/               # Python 이 자동 생성하는 컴파일 캐시 폴더
```

> **역할 분리 구조**  
> - `problem_4` : `MissionComputer` 클래스에 시스템 정보 메서드를 직접 추가  
> - `problem_5` : `problem_4` 의 클래스를 `import` 해서 `setting.txt` 설정에 따라 출력

---

## `__init__.py` 와 `__pycache__` 가 생겨난 이유

### `__init__.py`

Python 은 특정 폴더를 **패키지(Package)** 로 취급하려면 그 폴더 안에  
`__init__.py` 파일이 존재해야 한다.

이 프로젝트에서는 problem_5 가 problem_4 의 코드를 아래와 같이 `import` 한다.

```python
from problem_4.mars_mission_computer import MissionComputer
```

Python 이 `problem_4` 를 **패키지**로 인식하지 못하면 위 import 가 실패한다.  
따라서 `problem_4/` 와 `problem_5/` 양쪽에 `__init__.py` 를 만들어  
**각 폴더가 패키지임을 Python 에게 알려주는 역할**을 한다.

| 파일 | 역할 |
|---|---|
| `problem_4/__init__.py` | `problem_4` 폴더를 패키지로 등록 → `from problem_4.xxx import ...` 가능 |
| `problem_5/__init__.py` | `problem_5` 폴더를 패키지로 등록 → `python3 -m problem_5.xxx` 실행 가능 |

> `__init__.py` 의 내용이 비어 있어도 된다.  
> 파일이 **존재하는 것 자체**가 "이 폴더는 패키지다" 라는 선언이다.

---

### `__pycache__`

Python 코드(`.py`)를 처음 실행하거나 `import` 하면  
Python 인터프리터는 해당 파일을 **바이트코드(`.pyc`)** 로 컴파일하여  
`__pycache__/` 폴더 안에 자동으로 저장한다.

```
__pycache__/
└── mars_mission_computer.cpython-311.pyc   # 컴파일된 바이트코드 파일
```

**생겨나는 이유와 역할**

| 항목 | 설명 |
|---|---|
| 생성 시점 | `.py` 파일을 처음 실행하거나 다른 파일에서 `import` 할 때 자동 생성 |
| 저장 내용 | `.py` 소스 코드를 Python 가상머신이 바로 실행할 수 있는 바이트코드로 변환한 결과 |
| 목적 | 다음번 실행 시 `.py` 를 다시 컴파일하지 않고 `.pyc` 를 바로 불러와 **실행 속도를 높임** |
| 파일명 규칙 | `파일명.cpython-버전.pyc` (예: `mars_mission_computer.cpython-311.pyc`) |
| 자동 갱신 | `.py` 파일이 수정되면 Python 이 자동으로 `.pyc` 를 재생성함 |
| 삭제해도 무관 | 삭제하면 다음 실행 시 Python 이 자동으로 다시 생성하므로 문제 없음 |

> `__pycache__` 는 Python 이 **자동으로 관리**하는 폴더이므로  
> 개발자가 직접 수정하거나 신경 쓸 필요가 없다.  
> Git 등 버전 관리 시스템에서는 보통 `.gitignore` 에 추가하여 추적 대상에서 제외한다.

---

## 사용 라이브러리

### 표준 라이브러리 (Python 기본 제공)

| 라이브러리 | 사용 위치 | 역할 |
|---|---|---|
| `json` | problem_4 | 딕셔너리를 JSON 형식 문자열로 변환하여 출력 |
| `platform` | problem_4 | 운영체계 이름·버전, CPU 아키텍처 수집 |
| `threading` | problem_4 | 센서 출력 루프와 키 입력 감지를 동시에 처리 |
| `time` | problem_4 | 센서 측정 사이 5초 대기(sleep) |
| `os` | problem_5 | `setting.txt` 의 절대 경로를 동적으로 구성 |

### 외부 라이브러리 (시스템 정보 수집 목적으로만 허용)

| 라이브러리 | 버전 | 사용 위치 | 역할 |
|---|---|---|---|
| `psutil` | 최신 안정 버전 | problem_4 | CPU 물리 코어 수, 메모리 전체 크기·사용률, CPU 사용률 수집 |

> `platform` 만으로는 메모리 크기와 실시간 CPU/메모리 사용률을 가져올 수 없어  
> 시스템 정보 전용으로 `psutil` 을 사용했다.  
> 그 외 모든 곳에서는 Python 표준 라이브러리만 사용하여 제약조건을 준수했다.

---

## 클래스 및 함수 설명

### `MissionComputer` 클래스 (problem_4)

problem_4 에서 완성된 클래스에 시스템 정보 관련 메서드 2개를 추가했다.

#### `__init__(self)`

| 속성 | 타입 | 설명 |
|---|---|---|
| `env_values` | `dict` | 센서에서 읽어온 환경값 저장 (온도/습도/조도/CO₂/산소) |
| `ds` | `DummySensor` | 화성 환경 센서 시뮬레이터 인스턴스 |
| `history` | `list` | 5분 평균 계산을 위해 측정값을 순서대로 누적하는 리스트 |
| `running` | `bool` | 메인 루프 실행 여부를 제어하는 플래그 |

---

#### `get_sensor_data(self)`

5초마다 센서 데이터를 읽어 JSON 형태로 출력한다.  
60회(5분) 누적되면 평균값을 출력하고 기록을 초기화한다.

```
실행 중... (종료하려면 q 입력)
{
    "mars_base_internal_temperature": 23.4,
    "mars_base_external_temperature": -60.1,
    ...
}
```

- 쓰레드(`threading.Thread`)를 사용해 **출력 루프**와 **키 입력 감지**를 동시에 처리
- `daemon=True` 설정으로 메인 프로그램 종료 시 보조 쓰레드도 자동 종료

---

#### `stop_listener(self)`

보조 쓰레드에서 실행되며, `q` (대소문자 무관) 입력 시  
`self.running = False` 로 바꿔 메인 루프를 안전하게 종료시킨다.

---

#### `print_average(self)`

`history` 리스트에 누적된 60개의 데이터를 항목별로 합산하여 평균을 구한 뒤  
JSON 형태로 출력한다.

---

#### `get_mission_computer_info(self, settings=None)`

미션 컴퓨터의 **정적 시스템 정보**를 수집하여 JSON 형식으로 출력한다.

| 키 | 수집 방법 | 출력 예시 |
|---|---|---|
| `os` | `platform.system()` | `"Darwin"` |
| `os_version` | `platform.version()` | `"Darwin Kernel Version 25.4.0 ..."` |
| `cpu_type` | `platform.processor()` | `"arm"` |
| `cpu_cores` | `psutil.cpu_count(logical=False)` | `14` |
| `memory_total` | `psutil.virtual_memory().total` | `"24.00 GB"` |

- `settings` 파라미터에 키 목록을 넘기면 해당 항목만 필터링하여 출력
- `settings=None` 이면 전체 항목 출력
- 각 항목마다 **독립적으로 `try/except`** 처리 → 특정 항목 실패 시 나머지는 정상 출력

---

#### `get_mission_computer_load(self, settings=None)`

미션 컴퓨터의 **실시간 부하 정보**를 수집하여 JSON 형식으로 출력한다.

| 키 | 수집 방법 | 출력 예시 |
|---|---|---|
| `cpu_usage` | `psutil.cpu_percent(interval=1)` | `"14.1 %"` |
| `memory_usage` | `psutil.virtual_memory().percent` | `"79.4 %"` |

- `cpu_percent(interval=1)` : 1초 동안 측정한 CPU 사용률 평균값을 반환
- `settings` 파라미터로 출력 항목 필터링 가능 (동일 구조)
- 각 항목마다 독립적으로 예외처리

---

### `load_settings()` 함수 (problem_5)

`setting.txt` 파일을 읽어 출력할 항목의 키 목록을 반환한다.

| 상황 | 동작 |
|---|---|
| 파일 정상 | 주석(`#`)과 빈 줄을 제거한 키 목록 반환 |
| 파일 없음 | `FileNotFoundError` 를 잡아 기본값(전체 항목) 반환 |
| 파일 내용이 전부 주석 | 유효 항목이 없으므로 기본값(전체 항목) 반환 |

---

## setting.txt 설정 방법

출력에 포함할 항목을 직접 제어할 수 있다.

```
# [시스템 정보 항목] get_mission_computer_info()
os
os_version
cpu_type
cpu_cores
memory_total

# [시스템 부하 항목] get_mission_computer_load()
cpu_usage
memory_usage
```

- 줄 앞에 `#` 을 붙이면 해당 항목이 출력에서 제외된다
- 줄을 삭제해도 동일하게 제외된다
- 파일 자체를 삭제하면 전체 항목이 출력된다 (기본값 자동 적용)

**예시 — `os_version` 과 `memory_usage` 를 제외하고 싶을 때**

```
os
# os_version
cpu_type
cpu_cores
memory_total
cpu_usage
# memory_usage
```

---

## 실행 방법

```bash
python3 -m problem_5.mars_mission_computer
```

### `-m` 옵션을 붙이는 이유

`python3 파일.py` 와 `python3 -m 패키지.모듈` 은 비슷해 보이지만 동작 방식이 다르다.

**`-m` 없이 직접 실행할 경우**

```bash
python3 problem_5/mars_mission_computer.py
```

Python 은 `problem_5/mars_mission_computer.py` 를 단독 스크립트로 실행한다.  
이때 Python 의 모듈 탐색 기준이 **파일이 있는 폴더(`problem_5/`)** 가 되기 때문에  
아래 import 문에서 `problem_4` 를 찾지 못해 오류가 발생한다.

```
ModuleNotFoundError: No module named 'problem_4'
```

**`-m` 을 붙여 실행할 경우**

```bash
python3 -m problem_5.mars_mission_computer
```

`-m` 은 Python 에게 **"현재 작업 디렉토리(프로젝트 루트)를 기준으로 패키지를 찾아라"** 고 지시한다.  
그 결과 Python 의 모듈 탐색 기준이 **프로젝트 루트 폴더**가 되어  
`problem_4` 와 `problem_5` 를 모두 패키지로 인식하고 정상적으로 import 할 수 있다.

| 실행 방식 | 모듈 탐색 기준 | `from problem_4 import ...` |
|---|---|---|
| `python3 problem_5/mars_mission_computer.py` | `problem_5/` 폴더 | 실패 (ModuleNotFoundError) |
| `python3 -m problem_5.mars_mission_computer` | 프로젝트 루트 폴더 | 성공 |

> 정리하면, `-m` 옵션은 **여러 폴더(패키지)가 서로를 import 하는 구조**에서  
> 반드시 필요한 실행 방식이다.  
> `__init__.py` 로 패키지를 선언하고, `-m` 으로 루트 기준 실행을 보장하는 것이  
> 이 프로젝트의 import 구조가 올바르게 동작하는 핵심이다.

**출력 예시**

```json
===== 시스템 정보 =====
{
    "os": "Darwin",
    "os_version": "Darwin Kernel Version 25.4.0 ...",
    "cpu_type": "arm",
    "cpu_cores": 14,
    "memory_total": "24.00 GB"
}

===== 시스템 부하 =====
{
    "cpu_usage": "14.1 %",
    "memory_usage": "79.4 %"
}
```

---

## 제약조건 준수 내용

| 제약조건 | 준수 방법 |
|---|---|
| Python 표준 라이브러리만 사용 | `json`, `platform`, `threading`, `time`, `os` 사용 |
| 시스템 정보 수집에 한해 외부 라이브러리 허용 | `psutil` 을 시스템 정보/부하 수집 목적으로만 사용 |
| 시스템 정보 수집 부분 예외처리 필수 | 수집 항목마다 독립적 `try/except` 적용 |
| 모든 라이브러리 최신 안정 버전 사용 | `psutil` 최신 안정 버전 설치 |
| PEP 8 코딩 스타일 준수 | 문자열 `' '` 기본 사용, 들여쓰기 공백 4칸, 변수명 snake_case |

---

## 추가로 고려한 사항

### 1. 항목별 독립 예외처리

시스템 정보를 한 번에 수집하다가 특정 항목에서 오류가 나면  
나머지 항목까지 전부 출력되지 않는 문제가 생길 수 있다.  
이를 방지하기 위해 **각 항목을 별도의 `try/except` 블록으로 분리**했다.  
수집에 실패한 항목만 `"Error: ..."` 메시지로 대체되고 나머지는 정상 출력된다.

### 2. 물리 코어 vs 논리 코어 구분

`psutil.cpu_count()` 는 기본적으로 **논리 코어(하이퍼스레딩 포함)** 수를 반환한다.  
실제 하드웨어 코어 수를 파악하는 것이 진단에 더 유의미하다고 판단하여  
`logical=False` 옵션을 명시해 **물리 코어 수**만 수집했다.

### 3. 메모리 단위 변환

`psutil.virtual_memory().total` 은 바이트(Byte) 단위로 반환된다.  
사람이 읽기 쉬운 **GB 단위**로 변환 후 소수점 둘째 자리까지 표기했다.

```python
f'{total_bytes / (1024 ** 3):.2f} GB'
```

### 4. CPU 사용률 측정 방식

`psutil.cpu_percent(interval=1)` 의 `interval=1` 은  
**1초 동안 CPU 상태를 샘플링하여 평균 사용률**을 계산하도록 한다.  
`interval` 없이 호출하면 직전 호출 이후의 경과 시간을 기준으로 측정하기 때문에  
처음 호출 시 `0.0` 이 반환되는 문제가 있어 명시적으로 설정했다.

### 5. setting.txt 경로 처리

`setting.txt` 경로를 하드코딩하지 않고 `os.path.dirname(__file__)` 을 사용해  
**스크립트가 위치한 폴더를 기준으로 동적으로 경로를 구성**했다.  
이렇게 하면 실행 위치(현재 디렉토리)가 달라져도 파일을 찾을 수 있다.

### 6. 클래스 역할 분리 (problem_4 / problem_5)

시스템 정보 메서드(`get_mission_computer_info`, `get_mission_computer_load`)는  
**problem_4 의 `MissionComputer` 클래스에 직접 추가**했다.  
problem_5 는 해당 클래스를 `import` 해서 사용하는 역할만 담당한다.  
이렇게 분리하면 `MissionComputer` 클래스 자체가 모든 기능을 포함하게 되어  
다른 곳에서 `import` 하더라도 시스템 정보 기능을 그대로 사용할 수 있다.
