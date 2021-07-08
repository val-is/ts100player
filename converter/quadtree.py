import math
import random


def frame_to_quadtree(frame):
    s_y, s_x = len(frame), len(frame[0])
    assert s_y != 0
    assert s_x != 0
    if s_y != s_x or not (s_y & (s_y - 1) == 0) or not (s_x & (s_x - 1) == 0):
        pad_frame(frame)
    return _recursive_convert(frame), int(math.log2(len(frame)))


def empty(frame):
    for row in frame:
        for val in row:
            if val != 0:
                return False
    return True


def _recursive_convert(frame):
    s_y, s_x = len(frame), len(frame[0])
    assert s_y == s_x
    if empty(frame):
        return 0
    elif s_x == 1 or s_y == 1:
        return 1
    else:
        return [_recursive_convert(get_sub_frame(frame, i)) for i in range(4)]


def get_sub_frame(frame, quad):
    # get a sub quadrant. quadrants numbered like in math (i.e NE, NW, SW, SE)
    s_y, s_x = len(frame), len(frame[0])
    x, y = 0, 0
    w, h = s_x // 2, s_y // 2
    if quad == 0:
        x, y = s_x // 2, 0
    elif quad == 1:
        x, y = 0, 0
    elif quad == 2:
        x, y = 0, s_y // 2
    elif quad == 3:
        x, y = s_x // 2, s_y // 2
    w += x
    h += y

    f = []
    for row in range(y, h):
        r = []
        for col in range(x, w):
            r.append(frame[row][col])
        f.append(r)
    return f


def pad_frame(frame):
    # "naive" padding implementation. just add to bottom and side
    # TODO: pad equally on both sides of the frame
    s_y, s_x = len(frame), len(frame[0])
    if s_y >= s_x:
        if not (s_y & (s_y - 1) == 0):
            closest_pow = 2 ** (math.floor(math.log2(s_y)) + 1)
            cols_adding = closest_pow - s_y
            for _ in range(cols_adding):
                frame.append([0] * s_x)
            s_y += cols_adding
        for row in frame:
            row.extend([0] * (s_y - s_x))
    elif s_x > s_y:
        if not (s_x & (s_x - 1) == 0):
            closest_pow = 2 ** (math.floor(math.log2(s_x)) + 1)
            rows_adding = closest_pow - s_x
            for row in frame:
                row.extend([0] * rows_adding)
            s_x += rows_adding
        for _ in range(s_x - s_y):
            frame.append([0] * s_x)


def reconstruct_quadtree(tree):
    return _recursive_reconstruct(*tree)


def _recursive_reconstruct(tree, depth):
    if depth == 1:
        if tree == 0:
            return [[0, 0], [0, 0]]
        return [
                [tree[1], tree[0]],
                [tree[2], tree[3]]
                ]
    elif tree == 0:
        return [[0 for _ in range(2**depth)] for _ in range(2**depth)]

    rr = lambda x: _recursive_reconstruct(x, depth-1)
    
    # build in order of 1, 0, 2, 3 to get indexes right
    top_quad = rr(tree[1])
    for i, row in enumerate(rr(tree[0])):
        top_quad[i].extend(row)

    bottom_quad = rr(tree[2])
    for i, row in enumerate(rr(tree[3])):
        bottom_quad[i].extend(row)

    top_quad.extend(bottom_quad)
    return top_quad


def compare_trees(a, b):
    assert len(a) == len(b)
    assert len(a[0]) == len(b[0])
    for row in range(len(a)):
        for col in range(len(a[0])):
            assert a[row][col] == b[row][col]


def random_matrix(max_size, avoid_empty=True, random_bias=0.5):
    while True:
        w = random.randint(2, max_size)
        h = random.randint(2, max_size)
        m = []
        for _ in range(h):
            r = []
            for _ in range(w):
                r.append(1 if random.randint(0, 100) / 100 >= random_bias \
                        else 0)
            m.append(r)
        if not empty(m):
            return m
        elif not avoid_empty:
            return m


def flatten(tree):
    tree, depth = tree
    flattened = _flatten(tree, depth)
    if flattened == [0]:
        return [0]
    return flattened


def _flatten(tree, depth):
    if depth == 1:
        return tree
    if tree == 0:
        return [0]
    b = [1 if i != 0 else 0 for i in tree]
    f = []
    for i in tree:
        if i != 0:
            f.extend(_flatten(i, depth-1))
    return b + f


def unflatten(flat, depth):
    stack = []
    for i in range(len(flat) // 4):
        stack.append(flat[i*4:i*4+4])
    return _unflatten(stack, depth)


def _unflatten(stack, depth):
    instr = stack.pop(0)
    t = []
    for i in instr:
        if i == 0:
            t.append(0)
        elif depth > 1:
            t.append(_unflatten(stack, depth-1))
        else:
            t.append(1)
    return t


if __name__ == "__main__":
    # fuzzing/perf test tree gen
    n_fuzzes = 100
    max_size = 100
    comp_ratios = []
    for i in range(n_fuzzes):
        frame = random_matrix(max_size, random_bias=0.70)
        data = (len(frame) ** 2) / 8
        tree, depth = frame_to_quadtree(frame)
        flattened = flatten((tree, depth))
        comp = len(flattened) / 8
        unflattened = unflatten(flattened, depth)
        compare_trees(frame, reconstruct_quadtree((unflattened, depth)))
        comp_ratios.append(comp / data)

        if i % (n_fuzzes*0.1) == 0:
            print(f"{i/n_fuzzes * 100}% complete...")

    avg_comp = sum(comp_ratios) / len(comp_ratios)
    print(f"avg compression: {avg_comp}")
