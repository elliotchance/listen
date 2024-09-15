import unittest
from generate import Track

class TestTrack(unittest.TestCase):
  def test_1(self):
    t = Track('43 - ilan Bluestone', 7)
    self.assertTrack(t, '43', set(['ilan Bluestone']), False, 7)

  def test_2(self):
    t = Track('4Ever (Dub Mix) - [Alex M.O.R.P.H.] feat. [Natalie Gioia]', 7)
    self.assertTrack(t, '4Ever (Dub Mix)', set(['Alex M.O.R.P.H.', 'Natalie Gioia']), False, 7)

  def test_3(self):
    t = Track('Alchemy ([Above & Beyond] Club Mix) - [Above & Beyond] feat. [Zoe Johnston]', 7)
    self.assertTrack(t, 'Alchemy (Above & Beyond Club Mix)', set(['Above & Beyond', 'Zoe Johnston']), False, 7)

  def test_4(self):
    t = Track('@34:12', 5)
    self.assertTrack(t, '', set(), True, 5)

  def test_5(self):
    t = Track('<10> 43 - ilan Bluestone', 7)
    self.assertTrack(t, '43', set(['ilan Bluestone']), False, 10)

  def assertTrack(self, t, title, artists, is_time_code, rating):
    self.assertEqual(title, t.title)
    self.assertEqual(artists, t.artists)
    self.assertEqual(is_time_code, t.is_time_code)
    self.assertEqual(rating, t.rating)

if __name__ == '__main__':
  unittest.main()
