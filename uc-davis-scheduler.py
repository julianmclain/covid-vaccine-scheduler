"""
Script to navigate the UCD Covid vacine scheduling site and pause
when there's an appointment available.

In a future script, I would think about structuring this differently. Overall,
I like the Page abstraction, but I wonder if it would be better to inject the
driver into each page. Maybe:
- Driver function that takes a function as a value and calls it with the driver.
  E.g.: Driver(LocationSelectPate.navigate) or Driver(LocationSelectPage.click_button)
- My thought is that the Page objects would just tell the Driver how to behave during
  each interaction with the page and then retrun control back to the program where
  the Driver determines what to do next.

Future tip: working in the debugger is key. Set a breakpoint and then run a bunch of
"find..." methods with the driver and confirm that your selectors are working
as expected.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

import os
import time
import traceback
from datetime import datetime


class BasePage(object):
    """Page Objects are inteded to interact with the DOM via Selenium. This way,
    the WebSession doesn't need to know the underlying implementation of
    the interactions"""

    url = None
    timeout_seconds = 12
    screenshot_dir = 'screenshots'

    def __init__(self, driver):
        self.driver = driver

    def navigate(self) -> None:
        self.driver.get(self.url)

    def take_screenshot(self, file_name: str) -> None:
        self.driver.get_screenshot_as_file(f'{self.screenshot_dir}/{file_name}')


class LocationSelectPage(BasePage):
    url = 'https://vaccinescheduling.ucdavis.edu/MyChart/covid19/#/triage'
    # locators
    location_btn_class = 'location-card-title'

    def click_location_btn(self):
        self.take_screenshot('ucd_location_pg.png')
        location_btn = WebDriverWait(self.driver, self.timeout_seconds).until(
                    EC.presence_of_element_located((By.CLASS_NAME, self.location_btn_class)))
        location_btn.click()
        return SchedulingPage(self.driver)


class SchedulingPage(BasePage):
    # locators
    error_message_class = 'openingsNoData'

    def has_error_present(self) -> bool:
        try:
            time.sleep(10) # annoying and there's probably a better way to do this. iframe not available immediately.
            self.driver.switch_to.frame(self.driver.find_element_by_tag_name("iframe"))
            error_element = WebDriverWait(self.driver, self.timeout_seconds).until(
                    EC.presence_of_element_located((By.CLASS_NAME, SchedulingPage.error_message_class)))
            print(error_element)
            return True 
        except Exception as e:
            # Most likely TimeoutException 
            self.take_screenshot('scheduling_page_ready.png')
            return False 


def send_alert() -> None:
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    sid = os.environ['TWILIO_MESSAGE_SERVICE_SID']
    my_number = os.environ['MY_PHONE_NUMBER']
    body = 'BOOK YOUR COVID VACCINE!!!'

    client = Client(account_sid, auth_token)

    message = client.messages.create(messaging_service_sid=sid, body=body, to=my_number)


def run_attempt(driver) -> None:
    location_page = LocationSelectPage(driver)
    location_page.navigate()
    scheduling_page = location_page.click_location_btn()

    error_present = scheduling_page.has_error_present()
    if error_present:
        print(f'[{datetime.now()}] Better luck next time...')
        return

    else:
        scheduling_page.take_screenshot('available_to_schedule.png')
        send_alert()
        breakpoint()



def main():
    # Setup webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=2560x1600')
    driver = webdriver.Chrome(options=options)

    # Loop it
    try:
        while True:
            run_attempt(driver)
            time.sleep(30)

    except Exception as e:
        print(traceback.format_exc())

    finally:
        # Memory leak if you don't quit the driver at program exit
        driver.get_screenshot_as_file('screenshots/termination_point.png')
        driver.quit()
        print('Successfully quit Chrome browser')


if __name__ == '__main__':
    main()

