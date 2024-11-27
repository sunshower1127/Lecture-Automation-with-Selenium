import os
from time import sleep

from dotenv import load_dotenv
from selenium_wrapper_3.builder import ChromeBuilder
from selenium_wrapper_3.driver import Driver, driver
from selenium_wrapper_3.kor_date_parser import convert_date
from selenium_wrapper_3.node import (
    A,
    Any,
    Button,
    Div,
    I,
    IFrame,
    Input,
    Parent,
    Span,
)
from selenium_wrapper_3.utils import (
    click,
    count,
    frame,
    no_error,
    populate,
    retry_until,
    send_keys,
    text,
    url,
)

load_dotenv()

ChromeBuilder().debug_setting().set_retry(0.3, 5).add_option("maximize").build()

url("https://lms.ssu.ac.kr/login")

id, pw = os.getenv("ID"), os.getenv("PW")  # noqa: A001
assert id and pw, "ID and PW must be set"  # noqa: PT018, S101

send_keys(Input(name="userid"), [id, "\t", pw, "\n"])

click(Any(text="마이페이지") / Parent)

with frame(IFrame(id="fulliframe")):
    lines = Div(class_="xnscc-header")

    enable_subjects = retry_until(
        lambda: [line for line in populate(lines) if text(line // A()) != "0"],
    )

for subject in enable_subjects:
    url("https://lms.ssu.ac.kr/mypage")
    with frame(IFrame(id="fulliframe")):
        click(subject // Button())

        courses = subject / Parent // Div(class_="xnsti-left")

        titles = retry_until(
            lambda courses=courses: [
                text(course / A())
                for course in populate(courses)
                if count(course / I(("video", "in", "class")))
            ]
        )

        click(subject // A())

    for title in titles:
        with frame(IFrame(id="tool_content")):
            click(A(text=title))

        with frame(IFrame(id="tool_content")):
            total_dur = text(Span(text="재생 시간") / Parent / Span(1))

            cur_dur = text(Span(text="학습 진행 상태") / Parent / Span(1)).split("(")[0]

            with frame(IFrame()):
                click(Div(title="재생"))

                with no_error(), Driver().set_retry(1, 10):
                    click(Any(text="예"))
                    click(Any(text="확인"))

        print("Watching", title)

        t = convert_date(total_dur) - convert_date(cur_dur)
        print(t)
        sleep(t.total_seconds())

        driver().back()
