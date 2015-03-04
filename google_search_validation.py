import argparse
import logging
import urllib2
import requests
from datetime import datetime
import time
import platform
import os

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import test_data

# create webdriver instance
driver = webdriver.Firefox()
driver.implicitly_wait(30)

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('report.txt')
logger.addHandler(handler)

# create command line parser
parser = argparse.ArgumentParser()
parser.add_argument('-kwd', type=str, help='Keyword to search')
parser.add_argument('-link_to_validate', type=int, help='Number of link to validate')
parser.add_argument('-expected_total', type=int, help='expected amount of results')
args = parser.parse_args()

RESULTS_MATCHES = '# Total amount of returns ({0}) matches with expected ({1})'
RESULTS_MISMATCHES = '# Total amount of returns ({0}) mismatches with expected ({1})'


def test_google_search(keyword, expected_total, link_to_validate):
    # open Google page
    driver.get('http://www.google.com/')

    # Search for specified keyword - test argument
    driver.find_element_by_name('q').send_keys(keyword)
    search_btn = wait_for_visible(driver, By.XPATH, '//button[@aria-label="Google Search"]')
    search_btn.click()

    # Verify results amount: expected_total - actual_total
    actual_total_element = wait_for_visible(driver, By.ID, 'resultStats')
    actual_total = actual_total_element.text.split(' ')[1].replace(',', '')
    assert int(actual_total) == int(expected_total), RESULTS_MISMATCHES.format(actual_total, expected_total)
    logger.info(RESULTS_MATCHES.format(actual_total, expected_total))

    # Open result link
    click_on_link(link_to_validate)

    # Verify HTTP status code
    validate_status_code(driver.current_url, 200)
    logger.info('# Link (#{0}) is valid (200)'.format(link_to_validate))
    logger.info('# Page title - ({0})'.format(driver.title))

    # Retrieve page size
    logger.info('# Page size - {0} bytes'.format(get_content_size(driver.current_url)))


def log_system_info():
    logger.info('# ==================================================================')
    logger.info('# Username: ' + test_data.user_name)
    logger.info('# Email: ' + test_data.user_email)
    logger.info('# Date: ' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    logger.info('# ')
    logger.info('# OS: ' + platform.system() + platform.release() + '(' + os.name + platform.version() + ')')
    logger.info('# Browser name: ' + driver.capabilities['browserName'])
    logger.info('# Browser version: ' + driver.capabilities['version'])
    logger.info('# ')


def click_on_link(index):
    if index < 1 or index > 100:
        assert False, 'Please specify link in range: 0 < index <= 100'
    if index > 10:
        page = index / 10 + 1
        driver.find_element_by_xpath('//table[@id="nav"]//a[@class="fl" and text()="{0}"]'.format(page)).click()
    if index % 10 == 0:
        link_to_click = 10
    else:
        link_to_click = index % 10
    time.sleep(1)
    try:
        wait_for_visible(driver, By.ID, 'res')
        driver.find_elements_by_xpath('//div[@class="srg"]//h3[@class="r"]/a[@onmousedown]')[link_to_click-1].click()
    except IndexError:
        logger.info(link_to_click)
        # in case of SERP not always contains 10 results, go to second page, and determine new_link_to_click
        driver.find_element_by_xpath('//table[@id="nav"]//a[@class="fl" and text()="2"]').click()
        new_link_to_click = 10 - link_to_click
        driver.find_elements_by_xpath('//h3[@class="r"]/a[@onmousedown]')[new_link_to_click - 1].click()


def validate_status_code(url, expected_code):
    try:
        response = requests.get(url)
        actual_code = response.status_code
    except:
        assert False, 'Can\'t retrieve status code for URL" ' + url
    assert int(actual_code) == int(expected_code), 'Invalid status code: {0} Expected: {1}'.format(actual_code,
                                                                                                   expected_code)


def get_content_size(url):
    connection = urllib2.urlopen(url)
    return len(connection.read())


def wait_for_visible(driver, locator_type, locator, max_wait_time=30, optional_message=None):
    wait = WebDriverWait(driver, max_wait_time)
    if not optional_message:
        optional_message = "Element {0} did not appear on the page after waiting for {1} seconds".format(locator,
                                                                                                         max_wait_time)
    element = wait.until(
        EC.visibility_of_element_located((locator_type, locator)), optional_message
    )
    return element


if __name__ == '__main__':
    log_system_info()
    try:
        logger.info('# Script name: test_google_search')
        test_google_search(args.kwd, args.expected_total, args.link_to_validate)
        logger.info('# Result: PASS')
    except Exception, e:
        logger.error('Result: FAIL (%s)' % e)
    finally:
        driver.quit()
    logger.info('# ==================================================================')