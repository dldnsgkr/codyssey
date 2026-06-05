import csv
import pymysql


DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'mars_db'
CSV_FILE = 'mars_weathers_data.csv'

# temp 컬럼은 실제 데이터가 소수점 실수이므로 FLOAT 사용
CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS mars_weather (
    weather_id INT         NOT NULL AUTO_INCREMENT,
    mars_date  DATETIME    NOT NULL,
    temp       FLOAT,
    storm      INT,
    PRIMARY KEY (weather_id)
)
'''


class MySQLHelper:
    def __init__(self, host, port, user, password, database):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._connection = None
        self._cursor = None

    def connect(self):
        self._connection = pymysql.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database,
            charset='utf8mb4'
        )
        self._cursor = self._connection.cursor()
        print('MySQL 연결 성공')

    def execute(self, sql, params=None):
        if params:
            self._cursor.execute(sql, params)
        else:
            self._cursor.execute(sql)

    def commit(self):
        self._connection.commit()

    def fetchall(self):
        return self._cursor.fetchall()

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self._connection:
            self._connection.close()
        print('MySQL 연결 종료')


def read_csv(file_path):
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    print(f'CSV 파일 읽기 완료: {len(rows)}건')
    return rows


def print_csv_data(rows):
    print('\n[CSV 데이터 미리보기 (처음 10건)]')
    header = f"{'mars_date':<15} {'temp':>7} {'storm':>6}"
    print(header)
    print('-' * len(header))
    for row in rows[:10]:
        # CSV 헤더의 'stom'은 storm 컬럼과 매핑
        storm_val = row.get('storm') or row.get('stom', '')
        print(f"{row['mars_date']:<15} {row['temp']:>7} {storm_val:>6}")
    if len(rows) > 10:
        print(f'  ... 외 {len(rows) - 10}건')


def insert_weather_data(helper, rows):
    insert_sql = (
        'INSERT INTO mars_weather (mars_date, temp, storm) '
        'VALUES (%s, %s, %s)'
    )
    success = 0
    for row in rows:
        # CSV 헤더에 'stom' 오타가 있으므로 두 키 모두 시도
        storm_val = row.get('storm') or row.get('stom', 0)
        try:
            helper.execute(insert_sql, (
                row['mars_date'],
                float(row['temp']),
                int(storm_val)
            ))
            success += 1
        except Exception as e:
            print(f'INSERT 오류 ({row["mars_date"]}): {e}')
    helper.commit()
    print(f'데이터 입력 완료: {success}/{len(rows)}건')


def main():
    helper = MySQLHelper(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    try:
        helper.connect()
        helper.execute(CREATE_TABLE_SQL)
        helper.commit()
        print('테이블 생성(또는 확인) 완료')

        rows = read_csv(CSV_FILE)
        print_csv_data(rows)

        insert_weather_data(helper, rows)

        helper.execute('SELECT * FROM mars_weather ORDER BY weather_id LIMIT 10')
        results = helper.fetchall()
        print(f'\n[DB 저장 결과 확인 (처음 10건)]')
        print(f"{'ID':>4} {'mars_date':<22} {'temp':>7} {'storm':>6}")
        print('-' * 45)
        for record in results:
            print(
                f'{record[0]:>4} {str(record[1]):<22} '
                f'{record[2]:>7.2f} {record[3]:>6}'
            )

    except Exception as e:
        print(f'오류 발생: {e}')
    finally:
        helper.close()


if __name__ == '__main__':
    main()
