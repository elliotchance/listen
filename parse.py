paste = """
#10	2/13
Lost Together (Armin van Buuren Mashup) - Sophie Sugar vs. Sunlounger feat. Zara
Queensland (Arctic Moon Remix) [Symphony Track of The Month] - Dimension
#12: 1 Year Episode	3/14
Listening (Philip El Sisi Remix) - Aly & Fila feat. Josie
Inner Beauty (Angel Ace Remix) - Mike Danis
Florescence - Andy Blueman
#13	1/14
Perception - Markus Schulz feat. Justine Suissa
#14	3/13
Sanctuary (Sean Tyas Remix) [Symphony Track of the Month] - Gareth Emery feat. Lucy Saunders
Evoked Satellite [Symphony Timeless Track] - Deep Haze vs. OceanLab
All For You - Sophie Sugar
#15	0/15
#16	3/17
Never Enough - Jon O'Bir feat. Julie Harrington
Synaesthesia (Alex M.O.R.P.H. Remix) [Symphony Timeless Track] - The Thrillseekers
All For You - Sophie Sugar
#18	2/16
Bullet That Saved Me - Tritonal feat. Underdown
Aldo - Norin & Rad
#19	2/14
Banshee [Symphony Track Of The Month] - Sean Tyas
Talk To Me (Activa pres. Solar Movement Remix) - John O'Callaghan & Timmy & Tommy
#23	0/11
#24	3/14
Silence In Your Heart (4 Strings Remix) - Dash Berlin feat. Chris Madin
Constellation [Timeless Track] - Thomas Bronzwaer
Starships Over Alice - Arctic Moon
#25	2/12
Every Other Day - ReOrder
Foolish Boy (John O'Callaghan Remix) - Emma Hewitt
#26	2/13
Proteus - Thomas Bronzwaer
Messing With The Fantasy - Ian Betts
#27	0/11
"""

for line in paste.split('\n')[1:]:
  if line.startswith('#'):
    number = ' '.join(line[1:].split('\t')[:-1])
    tracks = line.split('/')[-1]
    title = ''
    if ':' in line:
      title = ':'.join(line.split(':')[1:]).strip()

    print('')
    print('  - number: ' + number)
    if title:
      print('    title: ' + title)
    if tracks:
      print('    tracks: ' + tracks)
    print('    liked:')
  else:
    print('      - ' + line)
