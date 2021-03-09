from slack_sdk import WebClient
import requests
from bs4 import BeautifulSoup
import datetime
import pause
import korea_holiday


timedelta = datetime.timedelta(minutes=30)
day_of_the_week = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
slack = WebClient(token="토큰 입력")
koreaHoliday = korea_holiday.krx_holiday_data()


# main 함수
def main():
    interest_stock_list = get_interest_code_list()
    cur_time = datetime.datetime.now()
    today = day_of_the_week[cur_time.weekday()]

    # 주말 제외
    if today == "토요일" or today == "일요일":
        slack.chat_postMessage(channel="#current_stock_price", text=str(datetime.date.today()) + today + " 오늘은 휴장일입니다.")

    # 공휴일 제외
    elif str(cur_time.date()) in koreaHoliday[0]:
        index = koreaHoliday[0].index(str(cur_time.date()))
        holiday_name = koreaHoliday[1][index]
        print("1")
        slack.chat_postMessage(channel="#current_stock_price", text=str(datetime.date.today()) + holiday_name + " 오늘은 휴장일입니다.")

    # 그 외 시장 오픈
    else:
        slack.chat_postMessage(channel="#current_stock_price", text=str(datetime.date.today()) + " 장 시작")
        while True:
            slack_bot_get_current_price(interest_stock_list)
            cur_time += timedelta
            if cur_time.hour >= 16:
                break
            pause.until(cur_time)
        slack.chat_postMessage(channel="#current_stock_price", text=str(datetime.date.today()) + " 장 마감")
        slack_bot_today_stock_info(interest_stock_list)


# 현재가 가져오기
def slack_bot_get_current_price(interest_stock_list):
    for code in interest_stock_list:
        info = get_all_info(code)
        slack.chat_postMessage(channel='#current_stock_price', text=info["종목명"] + " 현재가 : " + info["현재가"])


# 장 마감 후 주식 정보 가져오기
def slack_bot_today_stock_info(interest_stock_list):
    for code in interest_stock_list:
        info = get_all_info(code)

        all_information = "종목명 : " + info["종목명"]
        all_information += ", 종목코드 : " + info["종목코드"]
        all_information += ", 전일가 : " + info["전일가"]
        all_information += ", 현재가 : " + info["현재가"]
        all_information += ", 고가 : " + info["고가"]
        all_information += ", 저가 : " + info["저가"]
        all_information += ", 거래량 : " + info["거래량"]
        slack.chat_postMessage(channel='#today_stock_info', text=all_information)


# 0. 관심 종목 코드 가져오기
def get_interest_code_list():
    f = open("interest_stock_list.txt", "rt")
    interest_stock_list = f.read().split()
    f.close()
    return interest_stock_list


# 1. 종목 데이터 가져오기
def get_all_info(company_code):
    html = connect_finance_page(company_code)
    current_info = html.find("dl", {"class": "blind"})
    current_info = change_info_format(current_info.find_all("dd"))  # dict 형태로 변경
    return current_info


# 1-1. url 연결
def connect_finance_page(company_code):
    url = "https://finance.naver.com/item/main.nhn?code=" + company_code
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup


# 1-2. 종목 데이터 리스트 -> 사전 형태로 변경
def change_info_format(current_info):
    info_dictionary = {"Date": current_info[0].get_text()}
    current_info.remove(current_info[0])

    for i, item in enumerate(current_info):
        current_info[i] = item.get_text().split()

    for i, item in enumerate(current_info):
        info_dictionary[item[0]] = item[1]

    return info_dictionary


if __name__ == "__main__":
    main()
