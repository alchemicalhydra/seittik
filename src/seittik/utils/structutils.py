import re


STRUCT_FORMAT_RE = re.compile(r'(\d+)?[?bBcdefhHiIlLnNpPqQs]')


def calc_struct_input(s):
    return sum((1 if count is None else int(count)) for count in (m.groups()[0] for m in STRUCT_FORMAT_RE.finditer(s)))
