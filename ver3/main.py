"""숭실대학교 LMS 동영상 강의를 자동으로 시청하는 프로그램입니다."""

from sw_selenium.driver import SwChrome
from sw_selenium.ui_manager import get_data_from_file_or_ui

id, pw = get_data_from_file_or_ui(  # noqa: A001
    file_path="숭실대계정정보.txt",
    prompt_message="숭실대 아이디와 비밀번호를 입력해주세요.",
    length=2,
)

ban_list = get_data_from_file_or_ui(
    file_path="금지할강의명.txt",
    prompt_message="금지할 강의명을 입력해주세요.\n(여러개 입력가능, 더이상 입력하지 않으려면 취소)",
    length="INF",
)

web = SwChrome(
    "disable_popup", "mute_audio", "prevent_sleep", "maximize", "headless", timeout=20
)

web.get("https://lms.ssu.ac.kr/login")
web.find(name="userid").send_keys(id, "\t", pw, "\n")
web.find(text="마이페이지").up.click()

web.goto_frame("/fulliframe")

while True:
    # 볼 영상이 있는 과목 찾기
    subject_btns = (
        web.find_all(tag="span", class_name="xntc-title", text="동영상")
        .left()
        .wait(1)
        .filter(text="!0")
    )

    selected = False

    # 과목의 봐야할 동영상 강의 찾기
    for subject_btn in subject_btns:
        subject_btn.find_all(axis="preceding", tag="button")[-1].click()
        titles = web.find_all(tag="i", class_name="xnsti-left-icon video").right(0).text
        titles = [f"'{title}'" for title in titles if title not in ban_list]
        print(*titles, sep=", ")

        if titles:
            selected = True
            break
        ##

    if not selected:
        break

    subject_btn.click()

    # 강의 보기
    for title in titles:
        web.goto_frame("/tool_content")
        web.find(tag="a", text=title).click()

        web.goto_frame("/tool_content")
        total_dur = web.find(text="재생 시간").right[0].text

        cur_dur = web.find(text="학습 진행 상태").right[0].text.split("(")[0]
        web.goto_frame("0")
        web.find(title="재생").click()  # maximize 안해서 에러였었나 모르겠네

        with web.no_exc(), web.set_retry(10):
            web.find(text="예").click()
            web.find(text="확인").click()

        print("Watching", title)
        web.wait((cur_dur, total_dur), display=True)
        web.back()

    web.goto_frame("/")
    web.find(text_contains="마이페이지").up.click()
    web.goto_frame("tool_content")
