-- 데이터베이스 생성 (없을 경우)
CREATE DATABASE IF NOT EXISTS mars_db
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_general_ci;

USE mars_db;

-- mars_weather 테이블 생성
-- temp는 실제 CSV 데이터가 소수점 실수이므로 FLOAT 사용
CREATE TABLE IF NOT EXISTS mars_weather (
    weather_id INT         NOT NULL AUTO_INCREMENT,
    mars_date  DATETIME    NOT NULL,
    temp       FLOAT,
    storm      INT,
    PRIMARY KEY (weather_id)
);
