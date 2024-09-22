import unittest
from generate import Track, Release

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

class TestRelease(unittest.TestCase):
  def test_1(self):
    r = Release('2024-03-28: Tritonia #469')
    self.assertRelease(r, '2024-03-28', 'Tritonia', '469', '', '')
    self.assertEqual([], r.artists)

  def test_2(self):
    r = Release('2005-01-06: A State of Trance #182, "Yearmix"')
    self.assertRelease(r, '2005-01-06', 'A State of Trance', '182', 'Yearmix', '')

  def test_3(self):
    r = Release('2009-04-19: A State of Trance #400, "Godskitchen Air, Birmingham, England"')
    self.assertRelease(r, '2009-04-19', 'A State of Trance', '400', 'Godskitchen Air, Birmingham, England', '')

  def test_4(self):
    r = Release('2010-07-02: Sophie Sugar\'s Symphony #12, "1 Year Episode"')
    self.assertRelease(r, '2010-07-02', 'Sophie Sugar\'s Symphony', '12', '1 Year Episode', '')

  def test_5(self):
    r = Release('2011-04-09: A State of Trance #500, "Brabanthallen, Den Bosch, The Netherlands: A State of Blue"')
    self.assertRelease(r, '2011-04-09', 'A State of Trance', '500', 'Brabanthallen, Den Bosch, The Netherlands: A State of Blue', '')

  def test_6(self):
    r = Release('2012-03-07: A State of Trance #550, "Day 1": Expocenter, Moscow, Russia')
    self.assertRelease(r, '2012-03-07', 'A State of Trance', '550', 'Day 1', 'Expocenter, Moscow, Russia')
  
  def test_7(self):
    r = Release('Tritonia #469')
    self.assertRelease(r, '', 'Tritonia', '469', '', '')

  def test_8(self):
    r = Release('A State of Trance #182, "Yearmix"')
    self.assertRelease(r, '', 'A State of Trance', '182', 'Yearmix', '')

  def test_9(self):
    r = Release('A State of Trance #550, "Day 1": Expocenter, Moscow, Russia')
    self.assertRelease(r, '', 'A State of Trance', '550', 'Day 1', 'Expocenter, Moscow, Russia')
  
  def test_10(self):
    r = Release('2015-01-12: Boiler Room, "[Acid Pauli]"')
    self.assertRelease(r, '2015-01-12', 'Boiler Room', '', 'Acid Pauli', '')
    self.assertEqual(["Acid Pauli"], r.artists)
  
  def test_11(self):
    r = Release('2015-01-29: Boiler Room, "[ENA]": Tokyo, Japan')
    self.assertRelease(r, '2015-01-29', 'Boiler Room', '', 'ENA', 'Tokyo, Japan')
    self.assertEqual(["ENA"], r.artists)
  
  def test_12(self):
    r = Release('2020-05-12: Tritonia #300, "Part 2: Classic Progressive Trance Set"')
    self.assertRelease(r, '2020-05-12', 'Tritonia', '300', 'Part 2: Classic Progressive Trance Set', '')
  
  def test_13(self):
    r = Release('2021-10-26: EDC, "[Kayzo] b2b [Knife Party]"')
    self.assertRelease(r, '2021-10-26', 'EDC', '', 'Kayzo b2b Knife Party', '')
    self.assertEqual(["Kayzo", "Knife Party"], r.artists)

  def test_14(self):
    r = Release('2001-05-18: A State of Trance #0')
    self.assertRelease(r, '2001-05-18', 'A State of Trance', '0', '', '')

  def test_15(self):
    r = Release('2021-09-15: [Lane 8], "Fall 2021 Mixtape"')
    self.assertRelease(r, '2021-09-15', 'Lane 8', '', 'Fall 2021 Mixtape', '')

  def assertRelease(self, r, date, series, number, title, location):
    self.assertEqual(date, r.date)
    self.assertEqual(series, r.series)
    self.assertEqual(number, r.number)
    self.assertEqual(title, r.title)
    self.assertEqual(location, r.location)

if __name__ == '__main__':
  unittest.main()
