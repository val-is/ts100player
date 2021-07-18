# basic repeated value compression alg
def compress_repeated(vals):
    r = []
    prev = None
    count = 0
    for i in vals:
        if prev == i:
            count += 1
        else:
            if prev != None:
                r.extend([count, prev])
            prev = i
            count = 1
    return r


# split a set of frames into ones that iterate through quadrants
def split_quad_iter(frames):
    q = 0
    new = []
    for frame in frames:
        new.append(_get_quad_pixels(frame, q))
        q = (q + 1) % 4
    return new


def _get_quad_pixels(frame, quad):
    x_off, y_off = {
            0: (1, 0),
            1: (0, 0),
            2: (0, 1),
            3: (1, 1)
            }[quad]
    miniframe = []
    for row in range(y_off, len(frame), 2):
        r = []
        for col in range(x_off, len(frame), 2):
            r.append(frame[row][col])
        miniframe.append(r)
    return miniframe
