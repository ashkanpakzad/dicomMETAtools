import dicom2nifti
import os
from pathlib import Path
import pydicom
import random
from functions import *
import json
from pydicom.datadict import dictionary_keyword

top_dir = ''
output_dir = ''
prefix = ''
taglut_path = ''

# get list of folders in dir
dirpath = Path(str(top_dir))
dirnames = getdiritemlist(dirpath)

# randomly reorganise list and assign new numbers
newnames = []
random.shuffle(dirnames)
i = 0
for name in dirnames:
    i = i + 1
    newnames.append(prefix + '_' + str(i))

# load in tag look up table
tag_LUT = load_jsontags(taglut_path)

# Find all dicom files in given dicomdir
for dir, name in zip(dirnames,newnames) :
    filenames = getdiritemlist(dir)

    # Find all series names and get info
    meta = {'subjectname': name}
    series_names = []
    for dcm in filenames:
        ds = pydicom.filereader.dcmread(str(dirpath.joinpath(dcm)))
        try:
            current_series = str(ds.data_element('SeriesDescription').value)
        except KeyError:  # incase there is no series SeriesDescription tag.
            current_series = 'other'
        if current_series not in series_names:
            series_names.append(current_series)
            print('New series found: ' + current_series)
            # extract useful info to json file for each series.
            # TODO: figure out input json file to get output here.
            meta[current_series] = {}
            for tag in tag_LUT:
                meta[current_series].update({dictionary_keyword(tag): ds[tag].value})
    # save the json file
    jsonoutname = output_dir + name + 'meta.json'
    save_json(meta, jsonoutname)

# convert dicom to nifti file.
# TODO: make a new dir for output
for dicomdir, name in zip(dirnames, newnames):
    dicom_directory = dicomdir
    output_folder = output_dir + name

    dicom2nifti.convert_directory(dicom_directory, output_folder, compression=True, reorient=True)

