# Built-in imports
import sys
import os
import logging

# Third parties imports
from requests import get
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from lxml import html

base_url = "https://yolaw-tokeep-hiring-env.herokuapp.com/"
json_url = "https://s3-eu-west-1.amazonaws.com/legalstart/thumbscraper_input_tampered.hiring-env.json"

login = "Thumb"
password = "Scraper"

default_key = "0"
test_query_key = "xpath_test_query"
test_result_key = "xpath_test_result"
button_key = "xpath_button_to_click"
next_page_key = "next_page_expected"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logger.addHandler(stream_handler)


class TomThumbParser(object):
    """
    Tom Thumb Parser class.
    Stores the current page and a boolean indicating an error as class attributes.
    """

    def __init__(self, input_dict):
        self.index = 1
        self.error_encountered = False
        self.parser(input_dict)

    def parser(self, input_dict, url=base_url, index_key=default_key):
        """

        :param input_dict: Input dictionary to work with.
        :type input_dict: dict
        :param url: URL of the page
        :type url: basestring
        :param index_key: Current key in the input dictionary.
        :type index_key: basestring
        :return: None
        """

        while not self.error_encountered:
            logger.info("Move to page %d" % self.index)

            try:
                response = get(url, auth=HTTPBasicAuth(login, password))
            except RequestException as request_exception:  # Generic Requests exception handling.
                logger.error(request_exception)
                sys.exit(0)

            html_content = html.fromstring(response.content)

            test_query = html_content.xpath(input_dict[index_key][test_query_key])

            logger.debug(test_query)
            logger.debug(input_dict[index_key][test_result_key])

            # Testing the xpath query against its expected result.
            if test_query != input_dict[index_key][test_result_key]:
                self.error_encountered = True
                break

            self.index += 1

            xpath_button = html_content.xpath(input_dict[index_key][button_key])

            hyperlink = xpath_button[0].get("href")

            # Using lstrip to remove a potential leading slash.
            next_url = os.path.join(base_url, hyperlink.lstrip("/"))

            next_key = input_dict[index_key][next_page_key]

            self.parser(input_dict, next_url, next_key)
        else:
            logger.error("ALERT - Can’t move to page %d: page %d link has been malevolently tampered with!!" %
                         (self.index + 1, self.index))
            sys.exit(0)


if __name__ == '__main__':
    try:
        response = get(json_url)
    except RequestException as requests_exception:  # Generic Requests exception handling
        logger.error(requests_exception)
        sys.exit(0)

    input_dict = response.json()

    TomThumbParser(input_dict)




