# CT image anonymisation and rename all series belonging to single patient into folders
# By Ashkan Pakzad (ashkan.pakzad.13 at ucl.ac.uk)


# Folder Structure:
# Series1
#       |_Dicomfiles....

import os
import pydicom
import json
import datetime
from pathlib import Path
from argparse import ArgumentParser


def load_json(filename):
    with open(filename, "r") as read_file:
        data = json.load(read_file)
    return data


def save_json(data, filename):
    with open(filename, "w") as write_file:
        json.dump(data, write_file)


if __name__ == "__main__":
    ### Parser
    parser = ArgumentParser(description="Folder containing dicom series")
    parser.add_argument('Inputfilepath', nargs='+', type=str,
                        help='Input folder that directly contains all patient dicom files. e.g. ''dicoms'' ')
    parser.add_argument('--Outputfilepath', '-o', nargs='+', type=str,
                        help='Output file to save processed dicom files to. defaults to ''./dicoms-processed/'' where dicoms is the input folder name')
    parser.add_argument('--meta_file', '-m', nargs='+', type=str,
                        help='json file to append newly anonymised files to. defaults to create new json file called ''sensitive_meta.json''')
    args = parser.parse_args()

    # paths to data and save location
    filepath = Path(str(args.Inputfilepath[0]))  # directory containing all dicom series of single patient
    if args.Outputfilepath == None:
        newdir = Path(str(filepath) + '-anon')
    else:
        newdir = Path(str(args.Outputfilepath[0]))

    # incase dir already exits, force new dir
    #while str(newdir) in os.listdir('..'):
    z = None
    while z is None:
        try:
            os.mkdir(newdir)
            z = 1
        except FileExistsError:
            newdir = Path(str(newdir) + '_1')
            pass



# Create list of files in folder
    filenames = []
    for names in os.listdir(filepath):
        if not names.startswith('.'):
            filenames.append(names)

    # Read first file for patient info to be extracted.
    ds = pydicom.filereader.dcmread(str(filepath.joinpath(filenames[0])))
    patientname = str(ds.data_element('PatientName').value)
    age = str(ds.data_element('PatientAge').value)
    sex = str(ds.data_element('PatientSex').value)
    study_date = str(ds.data_element('StudyDate').value)
    patientid = str(ds.data_element('PatientID').value)
    # Create dictionary element
    new_sensitive_meta = {patientname: {'Patient': patientname, 'PatientID': patientid, 'Age': age, 'Sex': sex, 'Study Date': study_date}}

    # add patient to sensitive data file
    if args.meta_file == None:
        save_json(new_sensitive_meta, 'sensitive_meta.json')
    else:
        orig_meta = load_json(args.meta_file)
        orig_meta.update(new_sensitive_meta)
        save_json(orig_meta, args.meta_file)

    print(patientname)
    os.mkdir(newdir.joinpath(patientname))
    newpatient_dir = newdir.joinpath(patientname)
    print('patient name: ' + patientname)

    # Create reference json fields for CT fields
    ref_ds_raw = load_json("CT_dcm_ref.json")
    ref_ds = pydicom.dataset.Dataset()
    ref_ds = ref_ds.from_json(ref_ds_raw)

    print(ref_ds)
    # load tags to maintain in orig
    change_tags_json = load_json("CT_change.json")
    change_tags = change_tags_json['tags']

    ## for all files
    for dcm in filenames:

        # load original dicom file
        ds = pydicom.filereader.dcmread(str(filepath.joinpath(dcm)))

        # remove private tags
        ds.remove_private_tags()
        #print(ds)
        orig_tags = ds.dir()
        for tagname in orig_tags:
            # delete irrelevant tags
            if tagname not in ref_ds:
                del ds[tagname]
            # change sensitive values
            tag_base = str(pydicom.tag.Tag(tagname))
            tag_num = tag_base[1:5]+tag_base[7:11]
            if tag_num in change_tags:
                ds[tagname] = ref_ds[tagname]


        # Save file.
        # file name based on instance number
        filenumber = ds.data_element('InstanceNumber').value

        newfile = 'IM_%04d.dcm' % filenumber
        # save new dicomfile

        # Set creation date/time
        dt = datetime.datetime.now()
        ds.ContentDate = dt.strftime('%Y%m%d')
        timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
        ds.ContentTime = timeStr

        print('New file: ' + str(newpatient_dir.joinpath(newfile)))
        ds.save_as(str(newpatient_dir.joinpath(newfile)))

    print('COMPLETE')

