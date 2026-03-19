# codyssey

# 가상환경 생성

python3 -m venv venv

# 가상환경 활성화

window: venv\Scripts\activate
mac: source venv/bin/activate

# 가상환경 비활성화

deactivate

# 설정된 가상환경 정보 저장(like package.json)

pip freeze > requirements.txt

# 패키지 목록 다운로드

pip install -r crawler/requirements.txt
pip install -r server/requirements.txt
