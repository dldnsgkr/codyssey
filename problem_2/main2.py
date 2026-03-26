# CSV 파일을 읽어서 리스트 형태로 변환
def read_csv(file_path: str):
    data = []

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        headers = lines[0].strip().split(',')

        for line in lines[1:]:
            values = line.strip().split(',')

            if len(values) != len(headers):
                continue

            row = {}

            for i in range(len(headers)):
                key = headers[i]
                value = values[i]

                if key == 'Flammability':
                    try:
                        value = float(value)
                    except ValueError:
                        value = 0.0

                row[key] = value

            data.append(row)

    return data


# 전체 출력
def print_all(data):
    print('\n=== 전체 데이터 ===')
    for item in data:
        print(item)


# 인화성 기준 정렬
def sort_by_flammability(data):
    return sorted(data, key=lambda x: x.get('Flammability', 0), reverse=True)


# 위험 물질 필터링
def filter_dangerous(data, threshold=0.7):
    return [item for item in data if item.get('Flammability', 0) >= threshold]


# 출력용 함수
def print_items(title, items):
    print(f'\n=== {title} ===')
    for item in items:
        print(f"{item['Substance']} | Flammability: {item['Flammability']}")


# CSV 저장
def save_to_csv(data, file_path: str):
    if not data:
        return

    headers = list(data[0].keys())

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(','.join(headers) + '\n')

        for row in data:
            line = [str(row[key]) for key in headers]
            file.write(','.join(line) + '\n')


# 🔥 진짜 이진 파일 저장 (구조 기반)
def save_to_binary(data, file_path: str):
    with open(file_path, 'wb') as file:
        for row in data:
            # 문자열 필드 처리 (길이 + 데이터)
            for key in ['Substance', 'Weight (g/cm³)', 'Specific Gravity', 'Strength']:
                value = str(row[key])
                encoded = value.encode('utf-8')

                # 문자열 길이 저장 (1바이트)
                file.write(len(encoded).to_bytes(1, 'little'))

                # 문자열 데이터 저장
                file.write(encoded)

            # Flammability는 숫자로 저장 (소수점 2자리 기준)
            flammability = int(row['Flammability'] * 100)

            # 2바이트로 저장
            file.write(flammability.to_bytes(2, 'little'))


# 🔥 진짜 이진 파일 읽기
def load_from_binary(file_path: str):
    data = []

    with open(file_path, 'rb') as file:
        while True:
            try:
                row = {}
                keys = ['Substance', 'Weight (g/cm³)', 'Specific Gravity', 'Strength']

                for key in keys:
                    # 길이 읽기
                    length_bytes = file.read(1)
                    if not length_bytes:
                        return data

                    length = int.from_bytes(length_bytes, 'little')

                    # 데이터 읽기
                    value = file.read(length).decode('utf-8')
                    row[key] = value

                # 숫자 읽기
                flammability_bytes = file.read(2)
                flammability = int.from_bytes(flammability_bytes, 'little') / 100

                row['Flammability'] = flammability

                data.append(row)

            except Exception:
                break

    return data


# 🔥 텍스트 vs 이진 설명 (업그레이드 버전)
def explain_file_types():
    print('\n=== 텍스트 파일 vs 이진 파일 설명 ===\n')

    print('[텍스트 파일]')
    print('- 데이터를 사람이 읽을 수 있는 문자 형태로 저장')
    print('- 예: CSV, TXT\n')
    print('장점:')
    print('- 가독성이 좋아 사람이 직접 확인 가능')
    print('- 수정이 쉽고 다양한 환경에서 호환 가능\n')
    print('단점:')
    print('- 데이터 크기가 커질 수 있음')
    print('- 처리 속도가 상대적으로 느림\n')

    print('[이진 파일]')
    print('- 데이터를 바이트 단위(0과 1)로 직접 저장')
    print('- 구조화된 데이터 형태로 저장 가능\n')
    print('장점:')
    print('- 저장 공간 효율이 높음')
    print('- 읽기/쓰기 속도가 빠름')
    print('- 데이터 구조를 명확하게 표현 가능\n')
    print('단점:')
    print('- 사람이 직접 내용을 읽기 어려움')
    print('- 구조를 모르면 데이터 해석이 불가능\n')

    print('👉 핵심 요약:')
    print('텍스트 파일은 사람이 읽기 위한 방식이고,')
    print('이진 파일은 컴퓨터가 효율적으로 처리하기 위한 방식이다.')


def main():
    file_path = './problem_2/Mars_Base_Inventory_List.csv'

    # 1. CSV 읽기
    data = read_csv(file_path)

    # 2. 출력
    print_all(data)

    # 3. 정렬
    sorted_data = sort_by_flammability(data)
    print_items('인화성 높은 순 정렬', sorted_data)

    # 4. 위험 필터
    dangerous = filter_dangerous(sorted_data, 0.7)
    print_items('인화성 0.7 이상', dangerous)

    # 5. CSV 저장
    save_to_csv(dangerous, './problem_2/Mars_Base_Inventory_danger.csv')
    print('\n✅ CSV 저장 완료')

    # 6. 이진 저장 (진짜 구조 기반)
    save_to_binary(sorted_data, './problem_2/Mars_Base_Inventory_List.bin')
    print('✅ 이진 파일 저장 완료')

    # 7. 이진 읽기
    loaded = load_from_binary('./problem_2/Mars_Base_Inventory_List.bin')
    print_items('이진 파일에서 읽은 데이터', loaded)

    # 8. 설명
    explain_file_types()


if __name__ == '__main__':
    main()