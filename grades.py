import os
import time
import smtplib
from email.mime.text import MIMEText

# selenium imports for web scraping (make sure u 'pip install selenium')
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# set variables
USERNAME = os.environ.get("HARVARD_USERNAME")  # in terminal: 'export HARVARD_USERNAME=username'
PASSWORD = os.environ.get("HARVARD_PASSWORD")  # in terminal: 'export HARVARD_PASSWORD=password'

CHECK_INTERVAL = 30  # seconds

# email alert
EMAIL_FROM = os.environ.get("GMAIL_USERNAME")
EMAIL_TO = os.environ.get("GMAIL_USERNAME")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.environ.get("GMAIL_USERNAME")  # in terminal: 'export GMAIL_USERNAME=username'
# SEE INSTRUCTIONS ON SETTING PASSWORD in readme
SMTP_PASSWORD = os.environ.get("GMAIL_PASSWORD")  # see readme for how to set this up

# email function
def send_email_alert(subject, body):
    # sends an email alert via SMTP
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

# logs into my.harvard
def login_myharvard(driver, username, password):
    # start at my.harvard homepage
    driver.get("https://www.pin1.harvard.edu/cas/login?service=https%3a%2f%2fportal.my.harvard.edu%2f")
        
    # wait up to 15s for the username field
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    # enter username
    user_field = driver.find_element(By.ID, "username")
    user_field.send_keys(username)
    # enter password
    pass_field = driver.find_element(By.ID, "password")
    pass_field.send_keys(password)

    # click the submit button
    login_btn = driver.find_element(By.NAME, "submit")
    login_btn.click()

    # MANUALLY ACCEPT DUO, only have to do this once

    # wait for and click the trust button
    trust_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "trust-browser-button"))
    )
    trust_btn.click()

    # make sure we made it through
    WebDriverWait(driver, 20).until(
        EC.url_contains("my.harvard.edu"))  # or check a specific element
    
    time.sleep(15)

# go to the grades page
def go_to_grades_page(driver):

    # go to the grades tab
    grades_tab = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "IS_SSS_GRADESLnk"))
    )
    grades_tab.click()

    # wait for the term header, like Fall or Spring
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//h4[contains(text(),'Fall') or contains(text(),'Spring')]"))
    )

def keep_alive(driver):
    # refresh the page to keep the session alive
    driver.refresh()

def fetch_all_grades(driver):

    # dictionary to store grades
    grades_dict = {}

    # find all rows that are not for Spring 2025
    rows = driver.find_elements(By.XPATH, "//h4[not(contains(text(),'2025 Spring'))]/following-sibling::table[contains(@class,'accordion-table')]//tr")

    # loop through each row and extract the catalog number and grade
    for row in rows:
        try:
            # catalog Number
            catalog_td = row.find_element(By.XPATH, ".//td[@data-label='Catalog Number']")
            catalog_num = catalog_td.text.strip()

            # grade
            grade_td = row.find_element(By.XPATH, ".//td[@data-label='Grade']")
            grade = grade_td.text.strip()

            # add to the dictionary
            grades_dict[catalog_num] = grade
        except Exception:
            # in case any row doesn't match the expected structure, skip it
            continue

    return grades_dict

# main loop
def main():
    # set up Selenium in headless mode (no browser window)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # log in
        login_myharvard(driver, USERNAME, PASSWORD)

        # go to the grades page
        go_to_grades_page(driver)

        # keep track of old grades to compare
        old_grades = fetch_all_grades(driver)

        while True:
            try:
                current_grades = fetch_all_grades(driver)
                # compare to old dictionary
                for course, new_grade in current_grades.items():
                    old_grade = old_grades.get(course)
                    
                    # if new_grade is not blank and different from old, it changed
                    if new_grade and (new_grade != old_grade):
                        print(f"[GRADE UPDATE] {course} changed to {new_grade}")

                        subject = f"{course} Grade Update"
                        body = f"Your {course} grade is now: {new_grade}\nCheck my.harvard!"
                        send_email_alert(subject, body)
                    
                    else:
                        # only print if the grade is blank
                        if not new_grade:
                            print(f"[NO GRADE] {course} has no grade yet")

                # update old_grades
                old_grades = current_grades

            except Exception as e:
                print("Error fetching grades:", repr(e))

            # keep the session alive
            keep_alive(driver)

            # wait before next check
            time.sleep(CHECK_INTERVAL)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
