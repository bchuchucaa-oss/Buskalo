import unittest

from src.near_market.requests import validate_request_texto

class Test_validate_request_texto(unittest.TestCase):
    def test_texto_valido(self):
        self.assertTrue(validate_request_texto("MACBOOK"))
    def test_texto_espacios(self):
            self.assertTrue(validate_request_texto(" MACBOOK    "))
    def test_texto_vacio(self):
                self.assertFalse(validate_request_texto(""))
    def test_texto_numeros(self):
            self.assertFalse(validate_request_texto(123))
    def test_caracteres(self):
            self.assertFalse(validate_request_texto("l"*201))
    def test_caracteres_correctos(self):
            self.assertTrue(validate_request_texto("l"*200))
    def test_none_type(self):
            self.assertFalse(validate_request_texto(None))