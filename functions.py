import os
import json
from pydicom.tag import Tag

def getdiritemlist(directory):
    names = []
    for item in os.listdir(directory):
        # check not hidden file
        if not item.startswith('.'):
            names.append(item)
    return names


def load_json(filename):
    with open(filename, "r") as read_file:
        data = json.load(read_file)
    return data


def load_jsontags(filename):
    with open(filename, "r") as read_file:
        data = json.load(read_file)
    # make tag a BaseTag object
    data_list = [Tag(tag) for tag in data['tags']]
    return data_list


def save_json(data, filename):
    with open(filename, "w") as write_file:
        json.dump(data, write_file)