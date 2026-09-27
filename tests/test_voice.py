import unittest

from motor_voz import tempo_por_extenso, tempo_por_extenso_en


class TimeFormattingTests(unittest.TestCase):
    def test_formats_midnight_and_noon_in_portuguese(self):
        self.assertEqual(tempo_por_extenso("00:00"), "Meia-noite em ponto.")
        self.assertEqual(tempo_por_extenso("12:00"), "Meio-dia em ponto.")

    def test_formats_minutes_in_portuguese(self):
        self.assertEqual(tempo_por_extenso("13:21"), "Treze horas e vinte e um minutos.")

    def test_formats_english_time(self):
        self.assertEqual(tempo_por_extenso_en("13:05"), "It is one oh five P.M.")
        self.assertEqual(tempo_por_extenso_en("00:00"), "It is twelve A.M.")


if __name__ == "__main__":
    unittest.main()
