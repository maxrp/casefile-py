import os

def find_cases(base):
    for item in os.scandir(base):
        if item.is_dir():
            yield item

def list_cases(base):
    return [l for l in find_cases(base)]

def new_case(base, notes, case_directories):
    pass
