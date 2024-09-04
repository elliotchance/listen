import re

paste = """
series:
  from: 1
  to: 34
  status: complete

episodes:
  - number: 1
    tracks: 15
    liked:
      - All Your Colours - Kyau & Albert
      - D# Fat - [Armin van Buuren] & [W&W]

  - number: 2
    tracks: 15
    liked:
      - Bullet That Saved Me - [Tritonal] feat. [Underdown]

  - number: 3
    tracks: 16

  - number: 4
    tracks: 15
    liked:
      - Bullet That Saved Me - [Tritonal] feat. [Underdown]

  - number: 5
    tracks: 15

  - number: 6
    tracks: 16
    liked:
      - All Your Colours {[Andrew Rayel] Remix} - Kyau & Albert

  - number: 7
    tracks: 14

  - number: 8
    tracks: 15
    liked:
      - The Truth - Seven Lions

  - number: 9
    tracks: 16
    liked:
      - "@-42:20"
      - "@-38:50"

  - number: 10
    tracks: 15
    liked:
      - "@-13:40"
      - "@-3:15"
      - "@-2:00"

  - number: 11
    tracks: 15
    liked:
      - "@2:50"

  - number: 12
    tracks: 15

  - number: 13
    tracks: 15

  - number: 14
    tracks: 16

  - number: 15
    tracks: 16

  - number: 16
    tracks: 16
    liked:
      - "@5:50" # Dash Berlin - Steal You Away?

  - number: 17
    tracks: 16

  - number: 18
    tracks: 16

  - number: 19
    tracks: 17
    liked:
      - "@49:30"

  - number: 20
    tracks: 18

  - number: 21
    tracks: 18

  - number: 22
    tracks: 16

  - number: 23
    tracks: 17

  - number: 24
    tracks: 16

  - number: 25
    tracks: 17
    liked:
      - "@41:10"

  - number: 26
    tracks: 18

  - number: 27
    tracks: 16

  - number: 28
    tracks: 16

  - number: 29
    tracks: 16
    liked:
      - "@56:00"

  - number: 30
    tracks: 16

  - number: 31
    tracks: 18

  - number: 32
    tracks: 19
    liked:
      - "@9:00" # Fisherman and Hawkins?

  - number: 33
    tracks: 17

  - number: 34
    tracks: 34
    liked:
      - "@35:30" # Bruno Mars - Locked out of Heaven

"""

dir = """
/Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-12-23_ Tritonia #34 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-03-13_ Tritonia #1 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-03-20_ Tritonia #2 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-03-24_ Tritonia #3 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-04-03_ Tritonia #4 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-04-16_ Tritonia #5 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-04-27_ Tritonia #6 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-05-04_ Tritonia #7 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-05-11_ Tritonia #8 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-05-20_ Tritonia #9 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-05-25_ Tritonia #10, _circuitGROUNDS Stage__ EDC Chicago 2013, IL, USA /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-06-11_ Tritonia #11 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-06-17_ Tritonia #12 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-06-24_ Tritonal #13_ EDC 2013, Las Vegas, NV, USA /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-07-08_ Tritonia #14 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-07-15_ Tritonia #15 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-07-22_ Tritonia #16 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-08-07_ Tritonia #17 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-08-11_ Tritonia #18 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-08-19_ Tritonia #19 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-08-26_ Tritonia #20 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-09-02_ Tritonia #21_ Electric Zoo 2013, NY, USA /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-09-16_ Tritonia #22 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-09-24_ Tritonia #23 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-10-07_ Tritonia #24 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-10-14_ Tritonia #25 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-10-21_ Tritonia #26 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-10-28_ Tritonia #27 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-11-04_ Tritonia #28 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-11-11_ Tritonia #29 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-11-26_ Tritonia #30 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-12-02_ Tritonia #31 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-12-09_ Tritonia #32 /Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/Tritonia/2013/2013-12-13_ Tritonia #33
"""

def value(s, regexp):
  m = re.findall(regexp, s)
  if len(m) > 0:
    return m[0]

dates = {'499': '2011-03-10'}
for line in dir.replace('/Users/elliot/Library/Mobile Documents/com~apple~CloudDocs/Music/', '\n').split('\n'):
  dates[value(line, '#(\d+)')] = value(line, '[\d-]{10}')

paste = re.sub('  - number: (\d+)', lambda x: '  - number: ' + x.group(1) + '\n    date: ' + str(dates[x.group(1)]), paste)

print(paste)
