def get_dict_pos(lst, key, value):
    return next((index for (index, d) in enumerate(lst) if d[key] == value), None)


def build_dict(seq, key):
    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))
