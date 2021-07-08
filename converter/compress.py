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
