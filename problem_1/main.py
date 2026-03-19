# 로그 파일을 읽어서 구조화된 데이터(list of dict)로 변환
def parse_logs(file_path: str):
    result = []

    # 파일 열기 (UTF-8 인코딩)
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

        # 첫 줄: 컬럼(header) 정보
        headers = lines[0].strip().split(",")

        # 실제 데이터 파싱
        for line in lines[1:]:
            values = line.strip().split(",")

            # 컬럼 개수 불일치 방어 (잘못된 로그 제외)
            if len(values) != len(headers):
                continue

            # 각 행을 dict 형태로 변환
            row = {}
            for i in range(len(headers)):
                row[headers[i]] = values[i]

            result.append(row)

    return result


# 이벤트 종류별 발생 횟수 집계
def count_events(logs):
    counter = {}

    for log in logs:
        event = log["event"]

        # event 키 기준으로 카운트 증가
        counter[event] = counter.get(event, 0) + 1

    return counter


# 🔥 위험 키워드 + 점수 (사고 심각도 기준)
RISK_KEYWORDS = {
    "explosion": 100,       # 치명적 사고
    "meltdown": 100,
    "fire": 90,
    "rupture": 80,
    "leak": 70,
    "failure": 70,
    "crash": 70,
    "unstable": 50,         # 이상 상태
    "critical": 50,
    "warning": 40,
    "degraded": 40,
    "pressure drop": 60,    # 환경 이상
    "pressure loss": 60,
    "oxygen leak": 80,
    "oxygen loss": 80,
    "decompression": 90,
    "power failure": 80,    # 전력 문제
    "blackout": 90,
    "overload": 60,
}


# 로그 메시지 기반 위험 점수 계산
def calculate_risk_score(message):
    message = message.lower()
    score = 0

    # 키워드 포함 여부에 따라 점수 누적
    for keyword, weight in RISK_KEYWORDS.items():
        if keyword in message:
            score += weight

    return score


# 🔥 이상 로그 탐지 (임계값 기반 필터링)
def detect_anomalies(logs, threshold=50):
    anomalies = []

    for log in logs:
        # 각 로그의 위험 점수 계산
        score = calculate_risk_score(log["message"])

        # 일정 점수 이상만 이상 로그로 판단
        if score >= threshold:
            log["risk_score"] = score  # 점수 추가
            anomalies.append(log)

    return anomalies


# 🔥 사고 원인 체인 추적 (역순 탐색)
def trace_root_cause_chain(logs):
    chain = []

    # 최신 로그부터 거꾸로 탐색
    for i in range(len(logs) - 1, -1, -1):
        msg = logs[i]["message"].lower()

        # 최종 사고 지점 (explosion) 발견
        if "explosion" in msg:
            chain.append(logs[i])

            # 이전 로그들을 원인으로 추적
            j = i - 1
            while j >= 0:
                prev_msg = logs[j]["message"].lower()

                # 원인 후보 키워드 포함 여부 확인
                if any(
                    k in prev_msg for k in ["unstable", "leak", "failure", "critical"]
                ):
                    chain.append(logs[j])
                else:
                    break

                j -= 1

            break

    # 시간 순서로 정렬
    return list(reversed(chain))


# 🔥 원인 체인을 자연어 문장으로 변환
def generate_chain_summary(chain):
    if not chain:
        return "사고 원인을 특정할 수 없습니다."

    # 단일 사고만 있는 경우
    if len(chain) == 1:
        log = chain[0]
        return f"{log['timestamp']} 에 '{log['message']}' 사고가 발생했습니다."

    # 사고 흐름 설명
    summary = "사고는 다음과 같은 흐름으로 발생했습니다:\n\n"

    for log in chain:
        summary += f"- {log['timestamp']} : {log['message']}\n"

    summary += "\n위 상태 변화가 누적되어 최종 사고가 발생한 것으로 판단됩니다."

    return summary


# 🔥 이상 로그를 별도 파일로 저장
def save_anomalies(anomalies, file_path="anomalies.log"):
    with open(file_path, "w", encoding="utf-8") as f:
        for log in anomalies:
            f.write(
                f"{log['timestamp']},{log['event']},{log['message']},{log.get('risk_score', 0)}\n"
            )


# 🔥 Markdown 형식 보고서 생성
def generate_markdown_report(
    logs,
    event_counts,
    anomalies,
    chain,
    file_path="log_analysis.md",
):
    # 시간 역순 정렬 (최신순)
    sorted_logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)

    # 자연어 사고 요약 생성
    chain_summary = generate_chain_summary(chain)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("# 🚀 Log Analysis Report\n\n")

        # 사고 원인 체인
        f.write("## 🧠 원인 체인 분석\n\n")
        f.write(chain_summary + "\n")

        # 이벤트 통계
        f.write("\n## 📊 이벤트 통계\n\n")
        for k, v in event_counts.items():
            f.write(f"- {k}: {v}\n")

        # 전체 로그 (원본 순서)
        f.write("\n## 📄 전체 로그 (Original Order)\n\n```text\n")
        for log in logs:
            f.write(f"{log['timestamp']} | {log['event']} | {log['message']}\n")
        f.write("```\n")

        # 전체 로그 (최신순)
        f.write("\n## 🔽 전체 로그 (Latest First)\n\n```text\n")
        for log in sorted_logs:
            f.write(f"{log['timestamp']} | {log['event']} | {log['message']}\n")
        f.write("```\n")

        # 이상 로그 출력
        f.write("\n## ⚠️ 이상 로그 (Score 기반)\n\n")
        for log in anomalies:
            f.write(
                f"- {log['timestamp']} | {log['message']} (score: {log['risk_score']})\n"
            )


# 프로그램 전체 흐름 제어
def main():
    print('Hello Mars')
    file_path = "./problem_1/mission_computer_main.log"

    try:
        # 1. 로그 파싱
        logs = parse_logs(file_path)

        # 2. 분석 수행
        event_counts = count_events(logs)
        anomalies = detect_anomalies(logs)
        chain = trace_root_cause_chain(logs)

        # 3. 결과 저장
        save_anomalies(anomalies)

        generate_markdown_report(
            logs,
            event_counts,
            anomalies,
            chain,
        )

        print("✅ anomalies.log 생성 완료")
        print("✅ log_analysis.md 생성 완료")

    # 파일이 없는 경우
    except FileNotFoundError:
        print("❌ 로그 파일을 찾을 수 없습니다.")

    # 기타 예외 처리
    except Exception as e:
        print(f"❌ 에러 발생: {e}")


# 프로그램 시작 지점
if __name__ == "__main__":
    main()