import cv2
import numpy as np
import quadtree
import compress

_INPUT = "../video/processing/badapple.mp4"    # needs to be gotten w/ yt-dl
# _INPUT = "../video/processing/tmp.mp4"    # needs to be gotten w/ yt-dl

_MAX_RES = (96, 16)
_TARGET_FPS = 10

# load vid
video = cv2.VideoCapture(_INPUT)

orig_framerate = video.get(cv2.CAP_PROP_FPS)
frame_skip = orig_framerate // _TARGET_FPS

frames = [] # yeah, we load it into mem. so what lul

cur_frame = frames_written = 0
prev_frame = None
while video.isOpened():
    ret, frame = video.read()
    if not ret:
        break

    if cur_frame % frame_skip == 0:
        if cur_frame == 0:
            prev_frame = cur_frame
            cur_frame += 1
            continue
        # load frame into mem
        frame = cv2.resize(frame, _MAX_RES,
                interpolation=cv2.INTER_NEAREST_EXACT)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
        xored_frame = cv2.bitwise_xor(frame, prev_frame)
        xored_frame = xored_frame.tolist()
        for i in range(len(xored_frame)):
            for j in range(len(xored_frame[i])):
                if xored_frame[i][j] != 0:
                    xored_frame[i][j] = 1
                else:
                    xored_frame[i][j] = 0
        frames.append(xored_frame)
    cur_frame += 1
video.release()

def copy_frame(frame):
    f = []
    for r in frame:
        t = []
        for c in r:
            t.append(c)
        f.append(t)
    return f

def quadtree_compress():
    bitstream = []
    for f in frames:
        frame = copy_frame(f)
        tree = quadtree.frame_to_quadtree(frame)
        flattened = quadtree.flatten(tree)
        bitstream.extend(flattened)

    while len(bitstream) % 8 != 0:
        bitstream.append(0)

    quadtree_compressed = []
    for i in range(len(bitstream) // 8):
        byte = bitstream[i*8:(i+1)*8][::-1]
        val = sum([2**k if v == 1 else 0 for k, v in enumerate(byte)])
        quadtree_compressed.append(val)
    return quadtree_compressed

pos_compress = quadtree_compress()
print(len(pos_compress))
pos_compress_repeated = compress.compress_repeated(pos_compress)
print(len(pos_compress_repeated))

quadtree.set_positive_frame(0)
neg_compress = quadtree_compress()
print(len(neg_compress))
neg_compress_repeated = compress.compress_repeated(neg_compress)
print(len(neg_compress_repeated))
