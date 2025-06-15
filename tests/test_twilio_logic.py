import unittest

class TwilioLogicTest(unittest.TestCase):

    def test_extract_message_info_raises_error_on_missing_field(self):
        from app.core.twilio_logic import extract_message_info
        twilio_data = {}
        with self.assertRaises(AttributeError):
            extract_message_info(twilio_data)


    def test_get_full_twilio_data_raises_error_on_missing_client(self):
        from app.core.twilio_logic import get_full_twilio_data
        from app.exceptions import RequiresClientException
        with self.assertRaises(RequiresClientException):
            get_full_twilio_data("")