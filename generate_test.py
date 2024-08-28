import unittest
from generate import Track

class TestTrack(unittest.TestCase):
  def test_1(self):
    t = Track('43 - ilan Bluestone')
    self.assertTrack(t, '43', set(['ilan Bluestone']), False, False)

  def test_2(self):
    t = Track('4Ever (Dub Mix) - [Alex M.O.R.P.H.] feat. [Natalie Gioia]')
    self.assertTrack(t, '4Ever (Dub Mix)', set(['Alex M.O.R.P.H.', 'Natalie Gioia']), False, False)

  def test_3(self):
    t = Track('Alchemy ([Above & Beyond] Club Mix) - [Above & Beyond] feat. [Zoe Johnston]')
    self.assertTrack(t, 'Alchemy (Above & Beyond Club Mix)', set(['Above & Beyond', 'Zoe Johnston']), False, False)

  def test_4(self):
    t = Track('@34:12')
    self.assertTrack(t, '', set(), True, False)

  def test_5(self):
    t = Track('+ 43 - ilan Bluestone')
    self.assertTrack(t, '43', set(['ilan Bluestone']), False, True)

  def assertTrack(self, t, title, artists, is_time_code, is_boosted):
    self.assertEqual(title, t.title)
    self.assertEqual(artists, t.artists)
    self.assertEqual(is_time_code, t.is_time_code)
    self.assertEqual(is_boosted, t.is_boosted)

if __name__ == '__main__':
  unittest.main()
