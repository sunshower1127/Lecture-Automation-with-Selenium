from driver import Element, condition
from datetime import datetime, timedelta


def get_datetime(str):
    if "시간" in str:
        return datetime.strptime(str, "%H시간 %M분 %S초")
    elif "분" in str:
        return datetime.strptime(str, "%M분 %S초")
    else:
        return datetime.strptime(str, "%S초")


"""
idpw.txt 파일 생성 -> 첫줄에 아이디, 두번째줄에 패스워드 저장
ban.txt 파일 생성 -> 듣고 싶지 않은 강의 제목 줄단위로 작성
"""

with open("idpw.txt", "r", encoding="utf-8") as file:
    id = file.readline().strip()
    pw = file.readline().strip()

with open("ban.txt", "r", encoding="utf-8") as file:
    ban_list = file.read()


web = Element()

web.get_url("https://lms.ssu.ac.kr/login")

web.find(name="userid").send_keys(id)
web.find(name="pwd").send_keys(pw)
web.find(text="로그인").click()
web.find(text="마이페이지").parent().click()
web.switch_iframe("default", "first")

while True:
    """ 봐야할 강의영상이 있는 과목 찾기 """
    try:
        subject_btns = web.find_all(
            raw="//"
            + condition(tag="span", css_class="xntc-title", text="동영상")
            + "/../"
            + condition(tag="a", text_g=0)
        )
    except Exception:
        break

    selected = False
    for subject_btn in subject_btns:
        subject_btn.parent(4).find(tag="button").click()

        titles = [
            video_icon.parent().find(tag="a").text()
            for video_icon in web.find_all(tag="i", css_class="xnsti-left-icon video")
        ]

        titles = [title for title in titles if title not in ban_list]
        if len(titles) > 0:
            selected = True
            break

    if not selected:
        break

    subject_btn.click()
    ##########################################

    """ 강의영상 보기 """
    for title in titles:
        web.switch_iframe("default", "tool_content")
        web.find(text=title).click()

        web.switch_iframe("default", "tool_content")

        total_duration = web.find(text="재생 시간").parent().find(n=2).text()

        current_time = (
            web.find(text="학습 진행 상태").parent().find(n=2).text().split("(")[0]
        )

        time_left = (
            get_datetime(total_duration) - get_datetime(current_time)
        ).total_seconds()

        web.switch_iframe("first")
        web.find(title="재생").click()
        web.uncertain(lambda: web.find(text="예").click())
        web.uncertain(lambda: web.find(text="확인").click())

        print(f"{title} : {str(timedelta(seconds=time_left))} 재생")
        web.wait_secs(time_left)

        web.go_back()
        web.uncertain(lambda: web.yes_to_alert())

    web.switch_iframe("default")
    web.find(text_c="마이페이지").parent().click()
    web.switch_iframe("tool_content")
    ##########################################


web.close_window()
print("강의 자동 듣기 완료")
