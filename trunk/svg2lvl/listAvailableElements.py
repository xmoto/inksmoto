#ls *.png *.jpg | (while read line; do identify "$line" | cut -d' ' -f1,3 | sed -e "s/\(.*\)\.\(.*\) \(.*\)x\(.*\)/{'name':'\1', 'file':'\1.\2', 'width':\3, 'height':\4}/" ; done)

textures        = {'Black': {'file':'textures/Black.jpg', 'width':'3', 'height':'3'},
                   'BlueBricks': {'file':'textures/BlueBricks.jpg', 'width':'26', 'height':'26'},
                   'Bricks': {'file':'textures/Bricks.jpg', 'width':'26', 'height':'26'},
                   'DarkDirt': {'file':'textures/DarkDirt.jpg', 'width':'26', 'height':'26'},
                   'DarkFrostGround': {'file':'textures/DarkFrostGround.jpg', 'width':'26', 'height':'26'},
                   'Dirt': {'file':'textures/Dirt.jpg', 'width':'26', 'height':'26'},
                   'FrostGround': {'file':'textures/FrostGround.jpg', 'width':'26', 'height':'26'},
                   'MoltenRock': {'file':'textures/MoltenRock.jpg', 'width':'26', 'height':'26'}}
edgeTextures    = ['GrassAlt', 'Grass', 'GrayBricks', 'Ice1', 'BlueBricks', 'RedBricks']
particleSources = ['Smoke', 'Fire']
sprites         = {'BlankSignLeft1': {'file':'sprites/BlankSignLeft1.png', 'width':'26', 'height':'26'},
                   'BlankSignRight1': {'file':'sprites/BlankSignRight1.png', 'width':'26', 'height':'26'},
                   'Bridge': {'file':'sprites/Bridge.png', 'width':'26', 'height':'26'},
                   'CastleDoor1': {'file':'sprites/CastleDoor1.png', 'width':'26', 'height':'26'},
                   'CastleWindow1': {'file':'sprites/CastleWindow1.png', 'width':'26', 'height':'26'},
                   'FinSignLeft1': {'file':'sprites/FinSignLeft1.png', 'width':'26', 'height':'26'},
                   'FinSignRight1': {'file':'sprites/FinSignRight1.png', 'width':'26', 'height':'26'},
                   'Grass1': {'file':'sprites/Grass1.png', 'width':'3', 'height':'3'},
                   'HangingVines1': {'file':'sprites/HangingVines1.png', 'width':'26', 'height':'26'},
                   'HangingVines2': {'file':'sprites/HangingVines2.png', 'width':'26', 'height':'26'},
                   'HStones': {'file':'sprites/HStones.png', 'width':'13', 'height':'13'},
                   'SnowMan': {'file':'sprites/SnowMan.png', 'width':'13', 'height':'13'},
                   'ThisWaySignLeft1': {'file':'sprites/ThisWaySignLeft1.png', 'width':'26', 'height':'26'},
                   'ThisWaySignRight1': {'file':'sprites/ThisWaySignRight1.png', 'width':'26', 'height':'26'},
                   'Tree1': {'file':'sprites/Tree1.png', 'width':'26', 'height':'26'},
                   'Tree2': {'file':'sprites/Tree2.png', 'width':'26', 'height':'26'},
                   'Tut3Sign': {'file':'sprites/Tut3Sign.png', 'width':'26', 'height':'26'},
                   'YellowFlare': {'file':'sprites/YellowFlare.png', 'width':'3', 'height':'3'}}
skies           = ['sky1', 'sky2']
rversions       = ['0.2.0', '0.2.1', '0.2.2', '0.2.3', '0.2.4']
