# from unittest.mock import Mock
from mock import Mock
from mock import patch
from google.api_core import exceptions
import pytest

import main

@patch("main.storage.Client", autospec=True)
def test_print_name(clientMock):
    data = {"fileName": "c9880557-cb3d-49dd-8ab2-1a13b4f2b575",
            "fileContent": "86df48ab-2d5e-41f0-8cb1-263c49360992"}
    req = Mock(get_json=Mock(return_value=data), args=data)

    # Call tested function
    assert main.create_text_file_http(req) == ({"fileName": "c9880557-cb3d-49dd-8ab2-1a13b4f2b575"}, 200)
