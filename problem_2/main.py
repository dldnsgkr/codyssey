# CSV 파일을 읽어서 리스트 형태로 변환하는 함수
def read_csv(file_path: str):
    data = []  # 최종 데이터를 담을 리스트

    # 파일 열기 (텍스트 모드, UTF-8 인코딩)
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()  # 모든 라인을 읽어옴

        # 첫 번째 줄은 header (컬럼명)
        headers = lines[0].strip().split(',')

        # 두 번째 줄부터 실제 데이터
        for line in lines[1:]:
            values = line.strip().split(',')

            # 컬럼 개수가 맞지 않으면 무시
            if len(values) != len(headers):
                continue

            row = {}

            # header와 value를 매핑하여 dict 생성
            for i in range(len(headers)):
                key = headers[i]
                value = values[i]

                # Flammability 값은 float으로 변환
                if key == 'Flammability':
                    try:
                        value = float(value)
                    except ValueError:
                        value = 0.0  # 변환 실패 시 기본값

                row[key] = value

            data.append(row)  # 리스트에 추가

    return data


# 전체 데이터를 출력하는 함수
def print_all(data):
    print('\n=== 전체 데이터 ===')
    for item in data:
        print(item)


# 인화성 기준으로 내림차순 정렬하는 함수
def sort_by_flammability(data):
    # Flammability 값 기준으로 정렬 (높은 순)
    return sorted(data, key=lambda x: x.get('Flammability', 0), reverse=True)


# 인화성 기준으로 위험 물질 필터링 함수
def filter_dangerous(data, threshold=0.7):
    result = []

    for item in data:
        # 기준 이상인 데이터만 추출
        if item.get('Flammability', 0) >= threshold:
            result.append(item)

    return result


# 특정 리스트를 출력하는 함수 (가독성 좋게)
def print_items(title, items):
    print(f'\n=== {title} ===')

    for item in items:
        print(f"{item['Substance']} | Flammability: {item['Flammability']}")


# 데이터를 CSV 파일로 저장하는 함수
def save_to_csv(data, file_path: str):
    if not data:
        return  # 데이터 없으면 종료

    headers = list(data[0].keys())  # 컬럼명 추출

    with open(file_path, 'w', encoding='utf-8') as file:
        # header 작성
        file.write(','.join(headers) + '\n')

        # 각 row를 CSV 형식으로 저장
        for row in data:
            line = []

            for key in headers:
                line.append(str(row[key]))

            file.write(','.join(line) + '\n')


# 🔥 이진 파일 저장 함수 (문자열을 바이트로 변환하여 저장)
def save_to_binary(data, file_path: str):
    with open(file_path, 'wb') as file:
        for row in data:
            # | 구분자를 사용하여 한 줄 문자열 생성
            line = (
                f"{row['Substance']}|"
                f"{row['Weight (g/cm³)']}|"
                f"{row['Specific Gravity']}|"
                f"{row['Strength']}|"
                f"{row['Flammability']}\n"
            )
            # 문자열을 바이트로 변환 후 저장
            file.write(line.encode('utf-8'))


# 🔥 이진 파일을 읽어서 다시 리스트로 변환하는 함수
def load_from_binary(file_path: str):
    data = []

    with open(file_path, 'rb') as file:
        lines = file.readlines()

        for line in lines:
            # 바이트 → 문자열로 변환
            decoded = line.decode('utf-8').strip()

            # | 기준으로 분리
            parts = decoded.split('|')

            # 컬럼 개수 검증
            if len(parts) != 5:
                continue

            # 다시 dict 형태로 구성
            row = {
                'Substance': parts[0],
                'Weight (g/cm³)': parts[1],
                'Specific Gravity': parts[2],
                'Strength': parts[3],
                'Flammability': float(parts[4]),
            }

            data.append(row)

    return data


# 텍스트 파일과 이진 파일의 차이를 설명하는 함수
def explain_file_types():
    print('\n=== 텍스트 파일 vs 이진 파일 설명 ===\n')

    print('[텍스트 파일]')
    print('- 사람이 읽을 수 있는 형태로 저장됨')
    print('- 장점: 가독성 좋음, 수정 쉬움, 호환성 높음')
    print('- 단점: 용량 큼, 처리 속도 느림\n')

    print('[이진 파일]')
    print('- 데이터를 바이트 형태로 저장')
    print('- 장점: 속도 빠름, 용량 작음')
    print('- 단점: 사람이 읽기 어려움, 구조 이해 필요\n')

    print('👉 핵심:')
    print('텍스트 = 사람이 보기 위한 데이터')
    print('이진 = 컴퓨터가 처리하기 위한 데이터')


# 프로그램의 시작 지점
def main():
    file_path = './problem_2/Mars_Base_Inventory_List.csv'

    # 1. CSV 파일 읽기
    data = read_csv(file_path)

    # 2. 전체 데이터 출력
    print_all(data)

    # 3. 정렬 (인화성 높은 순)
    sorted_data = sort_by_flammability(data)
    print_items('인화성 높은 순 정렬', sorted_data)

    # 4. 위험 물질 필터링 (0.7 이상)
    dangerous = filter_dangerous(sorted_data, 0.7)
    print_items('인화성 0.7 이상', dangerous)

    # 5. 위험 물질 CSV 저장
    save_to_csv(dangerous, './problem_2/Mars_Base_Inventory_danger.csv')
    print('\n✅ Mars_Base_Inventory_danger.csv 저장 완료')

    # 6. 이진 파일 저장
    save_to_binary(sorted_data, './problem_2/Mars_Base_Inventory_List.bin')
    print('✅ Mars_Base_Inventory_List.bin 저장 완료')

    # 7. 이진 파일 다시 읽기
    loaded = load_from_binary('./problem_2/Mars_Base_Inventory_List.bin')
    print_items('이진 파일에서 읽은 데이터', loaded)

    # 8. 파일 형식 설명
    explain_file_types()


# 파이썬에서 직접 실행될 때만 main() 실행
if __name__ == '__main__':
    main()