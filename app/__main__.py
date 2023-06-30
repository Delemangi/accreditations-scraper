import argparse
import json
import time
from pathlib import Path
from typing import cast

import pandas as pd
from pandas import Series
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from . import selectors

URL = "https://akreditacii.iknow.ukim.mk/CourseEntry/GetCoursesList"
BASE_URL = "https://akreditacii.iknow.ukim.mk"


def get_webdriver(cookies: list[dict[str, str]]) -> WebDriver:
    if type(cookies) != list:
        raise TypeError("Cookies must be a list")

    wd = webdriver.Chrome()
    wd.get(BASE_URL)

    for cookie in cookies:
        wd.add_cookie(cookie)

    return wd


def get_cookies() -> list[dict[str, str]]:
    return json.loads(open("cookies.json").read())


def get_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="File name",
        default="output.csv",
    )
    arg_parser.add_argument(
        "--cycle",
        "-c",
        type=str,
        help="Cycle",
        default=None,
    )
    arg_parser.add_argument(
        "--year",
        "-y",
        type=str,
        help="Year",
        default=None,
    )
    arg_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        help="Limit",
        default=0,
    )
    arg_parser.add_argument(
        "--export", "-e", type=str, help="Export a file", default=None
    )

    return arg_parser.parse_args()


def select_cycle(webdriver: WebDriver, cycle: str) -> None:
    cycle_select = webdriver.find_element(By.CSS_SELECTOR, selectors.cycle_select)
    cycle_select_element = Select(cycle_select)
    cycle_select_element.select_by_value(cycle)


def select_year(webdriver: WebDriver, year: str) -> None:
    year_select = webdriver.find_element(By.CSS_SELECTOR, selectors.year_select)
    year_select_element = Select(year_select)
    year_select_element.select_by_value(selectors.year_values[year])


def get_courses(webdriver: WebDriver, limit: int) -> pd.DataFrame:
    courses: list[dict[str, str]] = []
    n = 0

    courses_table = webdriver.find_element(By.CSS_SELECTOR, selectors.courses_table)
    course_rows = courses_table.find_elements(By.CSS_SELECTOR, selectors.table_row)

    for row in course_rows:
        n += 1

        code = row.find_element(By.CSS_SELECTOR, selectors.course_code).text
        name = row.find_element(By.CSS_SELECTOR, selectors.course_name).text
        url = row.find_element(By.CSS_SELECTOR, selectors.course_url).get_attribute(
            "href"
        )

        courses.append(
            {
                "Code": code,
                "Name": name,
                "URL": url,
            }
        )

        print(f"Found course {code}")

        if n == limit:
            break

    return pd.DataFrame(courses)


def get_courses_data(webdriver: WebDriver, urls: list[str]) -> pd.DataFrame:
    courses = []

    for url in urls:
        webdriver.get(url)
        time.sleep(0.3)

        code = webdriver.find_element(
            By.CSS_SELECTOR, selectors.course_code_input
        ).get_attribute("value")
        academic_year = Select(
            webdriver.find_element(
                By.CSS_SELECTOR, selectors.course_academic_year_select
            )
        ).first_selected_option.text
        semester = Select(
            webdriver.find_element(By.CSS_SELECTOR, selectors.course_semester_select)
        ).first_selected_option.text
        ects = webdriver.find_element(
            By.CSS_SELECTOR, selectors.course_credits_input
        ).get_attribute("value")
        cycle = Select(
            webdriver.find_element(By.CSS_SELECTOR, selectors.course_cycle_select)
        ).first_selected_option.text
        active_accreditation = (
            webdriver.find_element(
                By.CSS_SELECTOR, selectors.course_active_accreditation_input
            ).get_attribute("checked")
            == "true"
        )

        teachers_button = webdriver.find_element(
            By.CSS_SELECTOR, selectors.teachers_button
        )
        webdriver.execute_script("arguments[0].click();", teachers_button)
        time.sleep(0.3)

        professors_table = webdriver.find_element(
            By.CSS_SELECTOR, selectors.course_professors_table
        )
        professors_rows = professors_table.find_elements(
            By.CSS_SELECTOR, selectors.table_row
        )

        professors: list[str] = []
        for row in professors_rows:
            professors.append(
                row.find_element(By.CSS_SELECTOR, selectors.course_professor).text
            )

        dependencies_button = webdriver.find_element(
            By.CSS_SELECTOR, selectors.dependencies_button
        )
        webdriver.execute_script("arguments[0].click();", dependencies_button)
        time.sleep(0.3)

        dependencies = webdriver.find_element(
            By.CSS_SELECTOR, selectors.dependencies
        ).get_attribute("value")

        courses.append(
            {
                "Code": code,
                "Academic Year": academic_year,
                "Semester": semester,
                "Credits": ects,
                "Cycle": cycle,
                "Active Accreditation": active_accreditation,
                "Professors": ", ".join(professors),
                "Dependencies": dependencies,
            }
        )

        print(f"Scraped course {code}")

    return pd.DataFrame(courses)


def export_results(file_name: str) -> None:
    folder_path = Path("./results")

    df = pd.read_csv(folder_path / f"{file_name}")
    df = df[["Code", "Name", "Semester", "Credits", "Professors", "Dependencies"]]

    df.to_excel(folder_path / f"{file_name.split('.')[0]}_short.xlsx", index=False)
    df.to_csv(folder_path / f"{file_name.split('.')[0]}_short.csv", index=False)


def main() -> None:
    args = get_args()
    export: str | None = args.export

    if export is not None:
        export_results(export)
        return

    file_name: str = args.file
    cycle: str | None = args.cycle
    year: str | None = args.year
    limit: int = args.limit

    cookies = get_cookies()
    webdriver = get_webdriver(cookies)
    webdriver.get(URL)

    time.sleep(2)

    if cycle is not None:
        select_cycle(webdriver, cycle)
    if year is not None:
        select_year(webdriver, year)

    time.sleep(2)

    df_1 = get_courses(webdriver, limit)
    df_2 = get_courses_data(webdriver, cast(Series[str], df_1.loc[:, "URL"]).tolist())
    df = pd.merge(df_1, df_2, on="Code", how="left")

    folder_path = Path("./results")
    folder_path.mkdir(parents=True, exist_ok=True)
    df.to_csv(folder_path / f"{file_name}", index=False)

    print(df)


if __name__ == "__main__":
    main()
