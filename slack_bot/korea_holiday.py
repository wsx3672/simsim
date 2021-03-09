import requests
import pandas as pd
from bs4 import BeautifulSoup


def koreaHoliday():
    # 공공데이터 공휴일 정보 OpenAPI 이용을 위한 url, key값 설정
    operation = "getRestDeInfo"
    year = 2021
    mykey = "CtSMsSzzUb6STRMoDp9D751nLaY54bG2a5vTRIo3CWwAiRRovKvhhdBikpnmXsYpopW%2FbjmsyhAjeAbqOBJXEw%3D%3D"
    url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService"

    # locDate : 공휴일 정보, dateName : 공휴일 이름
    locDate = []
    dateName = []

    # 1월 ~ 12월
    for i in range(1, 13):
        if i >= 10:
            month = str(i)
        elif i < 10:
            month = "0" + str(i)

        # url 접속 후 데이터 받아오기
        request_url = url + "/" + operation + "?solYear=" + str(year) + "&solMonth=" + month + "&serviceKey=" + mykey
        resp = requests.get(request_url)

        if resp.ok:
            soup = BeautifulSoup(resp.text, 'html.parser')
            item = soup.find_all('item')

            for i in item:
                date = i.find("locdate").get_text()
                locDate.append(date[:4] + "-" + date[4:6] + "-" + date[6:])
                dateName.append(i.find("datename").get_text())

    locDate.append("2021-05-01")
    dateName.append("근로자의 날")
    locDate.append("2021-12-31")
    dateName.append("연말휴장일")
    return locDate, dateName


def krx_holiday_data():
    holiday_data = pd.read_excel("2021_holiday.xls")
    locDate = holiday_data["일자 및 요일"].to_list()
    dateName = holiday_data["비고"].to_list()
    return locDate, dateName
