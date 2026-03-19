def parse_logs(file_path: str):
    result = []

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

        headers = lines[0].strip().split(",")

        for line in lines[1:]:
            values = line.strip().split(",")

            if len(values) != len(headers):
                continue

            row = {}
            for i in range(len(headers)):
                row[headers[i]] = values[i]

            result.append(row)

    return result


def count_events(logs):
    counter = {}
    for log in logs:
        event = log["event"]
        counter[event] = counter.get(event, 0) + 1
    return counter


# 🔥 위험 키워드 + 점수
RISK_KEYWORDS = {
    "explosion": 100,
    "meltdown": 100,
    "fire": 90,
    "rupture": 80,
    "leak": 70,
    "failure": 70,
    "crash": 70,
    "unstable": 50,
    "critical": 50,
    "warning": 40,
    "degraded": 40,
    "pressure drop": 60,
    "pressure loss": 60,
    "oxygen leak": 80,
    "oxygen loss": 80,
    "decompression": 90,
    "power failure": 80,
    "blackout": 90,
    "overload": 60,
}


def calculate_risk_score(message):
    message = message.lower()
    score = 0

    for keyword, weight in RISK_KEYWORDS.items():
        if keyword in message:
            score += weight

    return score


# 🔥 이상 탐지 (점수 기반)
def detect_anomalies(logs, threshold=50):
    anomalies = []

    for log in logs:
        score = calculate_risk_score(log["message"])

        if score >= threshold:
            log["risk_score"] = score
            anomalies.append(log)

    return anomalies


# 🔥 원인 체인 추적
def trace_root_cause_chain(logs):
    chain = []

    for i in range(len(logs) - 1, -1, -1):
        msg = logs[i]["message"].lower()

        if "explosion" in msg:
            chain.append(logs[i])

            j = i - 1
            while j >= 0:
                prev_msg = logs[j]["message"].lower()

                if any(
                    k in prev_msg for k in ["unstable", "leak", "failure", "critical"]
                ):
                    chain.append(logs[j])
                else:
                    break

                j -= 1

            break

    return list(reversed(chain))


# 🔥 자연어 체인 설명
def generate_chain_summary(chain):
    if not chain:
        return "사고 원인을 특정할 수 없습니다."

    if len(chain) == 1:
        log = chain[0]
        return f"{log['timestamp']} 에 '{log['message']}' 사고가 발생했습니다."

    summary = "사고는 다음과 같은 흐름으로 발생했습니다:\n\n"

    for log in chain:
        summary += f"- {log['timestamp']} : {log['message']}\n"

    summary += "\n위 상태 변화가 누적되어 최종 사고가 발생한 것으로 판단됩니다."

    return summary


# 🔥 이상 로그 저장
def save_anomalies(anomalies, file_path="anomalies.log"):
    with open(file_path, "w", encoding="utf-8") as f:
        for log in anomalies:
            f.write(
                f"{log['timestamp']},{log['event']},{log['message']},{log.get('risk_score', 0)}\n"
            )


# 🔥 Markdown 보고서
def generate_markdown_report(
    logs,
    event_counts,
    anomalies,
    chain,
    file_path="log_analysis.md",
):
    sorted_logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)
    chain_summary = generate_chain_summary(chain)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("# 🚀 Log Analysis Report\n\n")

        # 자연어 체인 분석
        f.write("## 🧠 원인 체인 분석\n\n")
        f.write(chain_summary + "\n")

        # 이벤트 통계
        f.write("\n## 📊 이벤트 통계\n\n")
        for k, v in event_counts.items():
            f.write(f"- {k}: {v}\n")

        # 전체 로그
        f.write("\n## 📄 전체 로그 (Original Order)\n\n```text\n")
        for log in logs:
            f.write(f"{log['timestamp']} | {log['event']} | {log['message']}\n")
        f.write("```\n")

        # 역순 로그
        f.write("\n## 🔽 전체 로그 (Latest First)\n\n```text\n")
        for log in sorted_logs:
            f.write(f"{log['timestamp']} | {log['event']} | {log['message']}\n")
        f.write("```\n")

        # 이상 로그
        f.write("\n## ⚠️ 이상 로그 (Score 기반)\n\n")
        for log in anomalies:
            f.write(
                f"- {log['timestamp']} | {log['message']} (score: {log['risk_score']})\n"
            )


def main():
    file_path = "./problem_1/mission_computer_main.log"

    try:
        logs = parse_logs(file_path)

        # 분석
        event_counts = count_events(logs)
        anomalies = detect_anomalies(logs)
        chain = trace_root_cause_chain(logs)

        # 저장
        save_anomalies(anomalies)

        generate_markdown_report(
            logs,
            event_counts,
            anomalies,
            chain,
        )

        print("✅ anomalies.log 생성 완료")
        print("✅ log_analysis.md 생성 완료")

    except FileNotFoundError:
        print("❌ 로그 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")


if __name__ == "__main__":
    main()
