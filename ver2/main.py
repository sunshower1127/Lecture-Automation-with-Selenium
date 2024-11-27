from enhanced_selenium import EnhancedChrome, debugger, get_data_from_file_or_ui

debugger.start(__file__)


id, pw = get_data_from_file_or_ui(
    file_path="숭실대계정정보.txt",
    prompt_message="숭실대 아이디와 비밀번호를 입력해주세요.",
    length=2,
)

ban_list = get_data_from_file_or_ui(
    file_path="금지할강의명.txt",
    prompt_message="금지할 강의명을 입력해주세요.\n(여러개입력가능, 더이상 입력하지 않으려면 취소)",
    length="INF",
)

web = EnhancedChrome(
    timeout=10, keep_browser_open=False, prevent_sleep=True, popup=False, headless=True
)

web.get("https://lms.ssu.ac.kr/login")
web.find(name="userid").send_keys(id)
web.find(name="pwd").send_keys(pw + "\n")
web.find(text="마이페이지").up().click()

web.goto_frame("/fulliframe")

while True:
    # Find the subject that has videos to watch
    subject_btns = (
        web.find_all(tag="span", class_name="xntc-title", text="동영상")
        .up()
        .find_or_none(tag="a", text="!0")
    )

    selected = False

    for subject_btn in subject_btns:
        subject_btn.up(4).find(tag="button").click()
        titles = (
            web.find_all(tag="i", class_name="xnsti-left-icon video")
            .up()
            .find(tag="a")
            .texts
        )
        print(f"{titles=}")
        titles = [f"'{title}'" for title in titles if title not in ban_list]

        if titles:
            selected = True
            break
        ##

    if not selected:
        break

    subject_btn.click()

    for title in titles:
        web.goto_frame("/tool_content")
        web.find(tag="a", text=title).click()

        web.goto_frame("/tool_content")
        total_dur = web.find(text="재생 시간").up().find_all()[1].text

        cur_dur = web.find(text="학습 진행 상태").up().find_all()[1].text.split("(")[0]

        web.goto_frame("0")
        web.find(title="재생").click()
        with web.no_error, web.set_repeat(10):
            web.find(text="예").click()
            web.find(text="확인").click()
        print("Watching", title)
        web.wait((cur_dur, total_dur))
        web.back()

    web.goto_frame("/")
    web.find(text_contains="마이페이지").up().click()
    web.goto_frame("tool_content")


debugger.end()
