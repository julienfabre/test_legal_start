# coding: utf-8

# Built-in imports
import sys
import os
import logging
import json
# Using open from io to be able to specify an encoding when opening a file.
# Compatible with Python 2.X and 3.X.
from io import open

# Third parties imports
from requests import get
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from lxml import html


# Global variables.
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
    Stores the current page and a boolean (indicating a tampered input file) as class attributes.
    """

    def __init__(self):
        self.page_index = 1
        self.error_encountered = False

    def parse(self, input_dict, url=base_url, index_key=default_key):
        """
        Parse the input file's dictionary.
        :param input_dict: Input dictionary to work with.
        :type input_dict: dict
        :param url: URL of the page
        :type url: basestring
        :param index_key: Current key in the input dictionary.
        :type index_key: basestring
        :return: The page index where the input file has been tampered, or None if the input file has not been
        tampered with.
        :rtype: int, bool
        """

        while not self.error_encountered:
            logger.info("Move to page %d" % self.page_index)

            try:
                response = get(url, auth=HTTPBasicAuth(login, password))
            except RequestException as request_exception:  # Generic Requests exception handling.
                logger.error(request_exception)
                sys.exit(0)

            html_content = html.fromstring(response.content)

            try:
                test_query = html_content.xpath(input_dict[index_key][test_query_key])
            except KeyError:
                # Handle the case where the input file has not been tampered.
                # We consider this to be the end of the input file.
                self.page_index = None
                self.error_encountered = True
                break

            # Testing the xpath query against its expected result.
            if test_query != input_dict[index_key][test_result_key]:
                self.error_encountered = True
                break

            self.page_index += 1

            xpath_button = html_content.xpath(input_dict[index_key][button_key])

            hyperlink = xpath_button[0].get("href")  # Acessing the button's hyperlink.

            # Using lstrip to remove a potential leading slash.
            next_url = os.path.join(base_url, hyperlink.lstrip("/"))

            next_key = input_dict[index_key][next_page_key]

            self.parse(input_dict, next_url, next_key)  # Recursively calling the parse function.
        else:
            # Returning the index in which there is a tampering, or None if there is no tampering.
            return self.page_index

        return None


def load_json_file(test_file_name=None):
    """
    Load the input json file. If no local test file name is provided,
    the URL specified in the test's Google Doc is used.
    :param test_file_name: Test file name, the file must be in current working directory.
    :type test_file_name: basestring
    :return: The input file as a Python dictionary.
    :type: dict
    """

    if test_file_name:  # Loading a local test file.
        try:
            with open(os.path.join(os.getcwd(), test_file_name), encoding='utf-8') as test_file:
                data = json.load(test_file)
        except IOError as io_error:
            logger.error(io_error)
            sys.exit(0)
        input_dictionary = data
    else:  # Using the URL specified in the test's Google Doc.
        try:
            response = get(json_url)
        except RequestException as requests_exception:  # Generic Requests exception handling
            logger.error(requests_exception)
            sys.exit(0)
        input_dictionary = response.json()

    return input_dictionary


if __name__ == '__main__':

    input_dict = load_json_file()

    tom_thumb_parser = TomThumbParser()

    index = tom_thumb_parser.parse(input_dict)
    if index:  # If an index is returned, the file has been tampered with.
        logger.error("ALERT - Can’t move to page %d: page %d link has been malevolently tampered with!!" %
                     (index + 1, index))
    else:
        # Case where the input file hasn't been tampered.
        logger.info("End of the input file.")

    sys.exit(0)








