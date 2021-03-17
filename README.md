# ts100player
Video player tools for the ts100 soldering iron (we gotta get Bad Apple! to run on every device)

## frame schema
Frames are stored as pixel diffs, each pixel is represented by a single byte

frames are 32 x 8 for us so...

5 bits for x location
3 bits for y location

0b XXXXX YYY

w/out any kind of compression, the diff method produces ~46kb of data (i.e. it might work)

0b00000000 is special, we use it to represent a frame clear