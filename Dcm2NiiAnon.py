#By Ashkan Pakzad on 6th April 2020 for anonymising dicom directories via the conversion to nifti and saving of
#desired tags contained in the original DICOMS.

import dicom2nifti
from pathlib import Path
import pydicom
import random
from functions import *
from pydicom.datadict import dictionary_keyword

# path names
top_dir = Path('~/directory_of_folders_containing_dicoms') # no excess directories permitted
output_dir = Path('~/output') # must already exist
taglut_path = Path('~/dcmmetatools/dicom_retaintags.json') # can be edited for what to copy
# repeating prefix to name of each reorganised dicom directory
prefix = 'case'

# get list of (dicom) directories in top directory
dirpath = str(top_dir)
dcmdir = getdiritemlist(dirpath)

# randomly reorganise list and assign new numbers for further anonimisation
newnames = []
random.shuffle(dcmdir)
i = 0
for name in dcmdir:
    i = i + 1
    newnames.append(prefix + '_' + str(i))

# load in json file listing metadata dicom tags to copy and retain
tag_LUT = load_jsontags(taglut_path)

# Find all dicom files in given dicomdir
allmeta = []
for dir, name in zip(dcmdir, newnames) :
    # identify folder holding dicoms
    filenames = getdiritemlist(str(dir))
    meta_list = []
    # Find all series names and get info
    series_names = []
    for dcm in filenames:
        meta = {'subjectname': name}
        ds = pydicom.filereader.dcmread(str(dir.joinpath(dcm)))
        try:
            current_series = str(ds.data_element('SeriesDescription').value)
        except KeyError:  # incase there is no series SeriesDescription tag.
            current_series = 'other'
        if current_series not in series_names:
            series_names.append(current_series)
            # extract requested dicom tags info to dict.
            meta[current_series] = {}
            for tag in tag_LUT:
                try:
                    savevalue = ds[tag].value
                    meta[current_series].update({dictionary_keyword(tag): str(ds[tag].value)})
                except KeyError:
                    # tag doesn't exist in this series
                    pass
            meta_list.append(meta)
    allmeta.append(meta_list)
print('Identified all dicom directories, their series and extracted metadata tags.')

# convert dicoms to nifti files and save metadata dicts as json files.
i = 0
for dicom_directory, name in zip(dcmdir, newnames):
    output_folder = output_dir.joinpath(name)
    jsonoutname = output_folder.joinpath(name+'.json')
    os.mkdir(output_folder)
    save_json(allmeta[i], str(jsonoutname))
    dicom2nifti.convert_directory(str(dicom_directory), str(output_folder), compression=True, reorient=True)
    i = i + 1
    print(str(i) + ' of '+ str(len(dcmdir)) + ' dicom directories converted')
print('ALL DONE!')


