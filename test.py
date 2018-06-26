from tom_thumb_parser import TomThumbParser, load_json_file


def test_valid_file():
    input_dict = load_json_file("valid.json")  # Using and untampered local file.
    tom_thumb_parser = TomThumbParser()

    page_index = tom_thumb_parser.parse(input_dict)
    assert page_index is None


def test_tampered_file():
    input_dict = load_json_file()
    tom_thumb_parser = TomThumbParser()

    page_index = tom_thumb_parser.parse(input_dict)
    assert type(page_index) is int
