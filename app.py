from flask import Flask, render_template, request
import requests  # pip install requests
from urllib.parse import urlencode, unquote
import json
import csv
from dotenv import load_dotenv
import os
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led_blue = 14
led_green = 15
led_yellow = 27
led_red = 10
buzzer = 6

GPIO.setup(led_blue, GPIO.OUT)
GPIO.setup(led_green, GPIO.OUT)
GPIO.setup(led_yellow, GPIO.OUT)
GPIO.setup(led_red, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)

load_dotenv()
myWeatherKey = os.environ.get("WEATHER_FORECAST_KEY")
print(myWeatherKey)

app = Flask(__name__)  # Initialise app

city_images = {
    "서울": "seoul.jpg",
    "인천": "incheon.jpg",
    "경기": "Gyeonggi.jpg",
    "강원": "gangwon.jpg",
    "충남": "chungnam.jpg",
    "충북": "chungbuk.jpg",
    "세종": "saejong.jpg",
    "대전": "daejeon.jpg",
    "경북": "gyeongbuk.jpg",
    "경남": "gyeongnam.jpg",
    "울산": "ulsan.jpg",
    "대구": "daegu.jpg",
    "부산": "busan.jpg",
    "전남": "jeonnam.jpg",
    "전북": "jeonbuk.jpg",
    "광주": "gwangju.jpg",
    "제주": "jaeju.jpg",
    "전국": "Korea.png"
}
# Config
error_message = ""
# 미세먼지 농도
def getWeather(city_name):
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
    queryString = "?" + urlencode(
        {
            "ServiceKey": unquote(myWeatherKey),
            "returnType": "JSON",
            "numOfRows": "100",
            "pageNo": "1",
            "sidoName": city_name,
            "ver": "1.0",
        }
    )
    try:
        response = requests.get(url + queryString)
        r_dict = json.loads(response.text)
        r_response = r_dict.get("response")
        r_body = r_response.get("body")

        r_item = r_body.get("items")
        if isinstance(r_item, list):
            misaemj = int(r_item[1].get("pm10Value"))
        else:
            misaemj = int(r_item.get("pm10Value"))
        return misaemj
    except (ValueError, KeyError, TypeError):
        # 예외 발생 시 기본값 또는 오류 메시지 반환
        return None

# 초 미세먼지 농도
def getWeather25(city_name):
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
    queryString = "?" + urlencode(
        {
            "ServiceKey": unquote(myWeatherKey),
            "returnType": "JSON",
            "numOfRows": "100",
            "pageNo": "1",
            "sidoName": city_name,
            "ver": "1.0",
        }
    )
    try:
        response = requests.get(url + queryString)
        r_dict = json.loads(response.text)
        r_response = r_dict.get("response")
        r_body = r_response.get("body")

        r_item = r_body.get("items")
        if isinstance(r_item, list):
            misaemj25 = int(r_item[1].get("pm25Value"))
        else:
            misaemj25 = int(r_item.get("pm25Value"))
        return misaemj25
    except (ValueError, KeyError, TypeError):
        # 예외 발생 시 기본값 또는 오류 메시지 반환
        return None

def getWeatherO3(city_name):
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
    queryString = "?" + urlencode(
        {
            "ServiceKey": unquote(myWeatherKey),
            "returnType": "JSON",
            "numOfRows": "100",
            "pageNo": "1",
            "sidoName": city_name,
            "ver": "1.0",
        }
    )
    try:
        response = requests.get(url + queryString)
        r_dict = json.loads(response.text)
        r_response = r_dict.get("response")
        r_body = r_response.get("body")

        r_item = r_body.get("items")
        if isinstance(r_item, list):
            misaemjo3 = float(r_item[0].get("o3Value"))
        else:
            misaemjo3 = float(r_item.get("o3Value"))
        return misaemjo3
    except (ValueError, KeyError, TypeError):
        # 예외 발생 시 기본값 또는 오류 메시지 반환
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 미세먼지 종류 선택
        dust_type = request.form["type"]

        # 지역 이름
        city_name = request.form["name"]

        if city_name == "":
            return render_template("index.html")
        
        if city_name not in city_images:
            return render_template("index.html", error_message="존재하지 않는 지역 이름입니다.")

        if dust_type == "pm10":
            misaemj = getWeather(city_name)
            dust_type_label = "미세먼지(PM10)"
            gijun_class = "pm10-class"  # 클래스명을 적절히 변경하세요
        elif dust_type == "pm25":
            misaemj = getWeather25(city_name)
            dust_type_label = "초미세먼지(PM2.5)"
            gijun_class = "pm25-class" 
        elif dust_type == "o3":
            misaemj = getWeatherO3(city_name)
            dust_type_label = "오존(O3)"
            gijun_class = "o3-class" # 클래스명을 적절히 변경하세요
        else:
            misaemj = None
            dust_type_label = ""
            gijun_class = ""
        
        if gijun_class == "pm10-class":
            if misaemj is not None:
                info_picture = "mis.PNG"
                if misaemj <= 30:
                    gijun = "좋음"
                    dg_gijun="good"
                    GPIO.output(led_blue, 1)
                    GPIO.output(led_green, 0)
                    GPIO.output(led_yellow, 0)
                    GPIO.output(led_red, 0)
                    play_buzzer(294, 1)
                elif misaemj <= 80:
                    gijun = "보통"
                    dg_gijun="warning"
                    GPIO.output(led_blue, 0)
                    GPIO.output(led_green, 1)
                    GPIO.output(led_yellow, 0)
                    GPIO.output(led_red, 0)
                    play_buzzer(349, 3)
                elif misaemj <= 150:
                    gijun = "나쁨"
                    dg_gijun="bad"
                    GPIO.output(led_blue, 0)
                    GPIO.output(led_green, 0)
                    GPIO.output(led_yellow, 1)
                    GPIO.output(led_red, 0)
                    play_buzzer(440, 5)
                else:
                    gijun = "매우나쁨"
                    dg_gijun="very-bad"
                    GPIO.output(led_blue, 0)
                    GPIO.output(led_green, 0)
                    GPIO.output(led_yellow, 0)
                    GPIO.output(led_red, 1)
                    play_buzzer(523, 7)
        elif gijun_class == "pm25-class":
            if misaemj is not None:
                info_picture = "chomis.PNG"
                if misaemj <= 15:
                    gijun = "좋음"
                    dg_gijun="good"
                    GPIO.output(led_blue, 1)
                    GPIO.output(led_green, 0)
                    GPIO.output(led_yellow, 0)
                    GPIO.output(led_red, 0)
                    play_buzzer(294, 1)
                elif misaemj <= 35:
                    gijun = "보통"
                    dg_gijun="warning"
                    GPIO.output(led_blue, 0)
                    GPIO.output(led_green, 1)
                    GPIO.output(led_yellow, 0)
                    GPIO.output(led_red, 0)
                    play_buzzer(349, 3)
                elif misaemj <= 75:
                    gijun = "나쁨"
                    dg_gijun="bad"
                    GPIO.output(led_blue, 0)
                    GPIO.output(led_green, 0)
                    GPIO.output(led_yellow, 1)
                    GPIO.output(led_red, 0)
                    play_buzzer(440, 5)
                else:
                    gijun = "매우나쁨"
                    dg_gijun="very-bad"
                    GPIO.output(led_blue, 0)
                    GPIO.output(led_green, 0)
                    GPIO.output(led_yellow, 0)
                    GPIO.output(led_red, 1)
                    play_buzzer(523, 7)
        else:
            if misaemj is not None:
                info_picture = "ozon.PNG"
                if misaemj <= 0.030:
                    gijun = "좋음"
                    dg_gijun="good"
                    GPIO.output(led_blue, 1)
                    GPIO.output(led_green, 0)
                    GPIO.output(led_yellow, 0)
                    GPIO.output(led_red, 0)
                    play_buzzer(294, 1)
                elif misaemj <= 0.090:
                    gijun = "보통"
                    dg_gijun="warning"
                    GPIO.output(led_blue, 0)
                    GPIO.output(led_green, 1)
                    GPIO.output(led_yellow, 0)
                    GPIO.output(led_red, 0)
                    play_buzzer(349, 3)
                elif misaemj <= 0.150:
                    gijun = "나쁨"
                    dg_gijun="bad"
                    GPIO.output(led_blue, 0)
                    GPIO.output(led_green, 0)
                    GPIO.output(led_yellow, 1)
                    GPIO.output(led_red, 0)
                    play_buzzer(440, 5)
                else:
                    gijun = "매우나쁨"
                    dg_gijun="very-bad"
                    GPIO.output(led_blue, 0)
                    GPIO.output(led_green, 0)
                    GPIO.output(led_yellow, 0)
                    GPIO.output(led_red, 1)
                    play_buzzer(523, 7)

        return render_template(
            "index.html",
            misaemj=misaemj,
            city_name=city_name,
            gijun=gijun,
            dust_type_label=dust_type_label,
            gijun_class=gijun_class,
            city_images=city_images[city_name],
            info_picture = info_picture,
            dg_gijun=dg_gijun,
            error_message=error_message
        )
    else:
        return render_template("index.html")
def play_buzzer(frequency, repeat):
    p = GPIO.PWM(buzzer, 50)
    p.start(50)
    for _ in range(repeat):
        p.ChangeFrequency(frequency)
        time.sleep(0.5)
    p.stop()

if __name__ == "__main__":
    app.run(debug=True)