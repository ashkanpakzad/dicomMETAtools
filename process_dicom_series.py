### Rename all series belonging to single patient into folders
# By Ashkan Pakzad (ashkan.pakzad.13 at ucl.ac.uk)
# also rewindows CT images
#Folder Structure:
#|_PatientName
#   |
#   |_Series1
#       |_Dicomfiles....
#   |
#   |_Series2
#       |_Dicomfiles....
#   |
#   |_Series3
#       |_Dicomfiles....
#   |
#   |_Other
#       |_misc....

import os
import pydicom
import copy
from pathlib import Path
from argparse import ArgumentParser

if __name__ == "__main__":
    parser = ArgumentParser(description="Process raw unorganised dicom files for single patient in dicom series. Also anonymises DOB and changes default CT window.")
    parser.add_argument('Inputfilepath', nargs='+' ,type=str,
                        help='Input folder that directly contains all patient dicom files without subdirectories. e.g. ''dicoms'' ')
    parser.add_argument('--Outputfilepath','-o', nargs='+', type=str,
                        help='Output file to save processed dicom files to. defaults to ''./dicoms-processed/'' where dicoms is the input folder name')
    parser.add_argument('--CTwindow','-w',nargs='+',default=[-600, 1500],
                        type=int, help='Set default DICOM metadata CT window for data, [center, width]. set to pulmonary by default, [-600, 1500]. ')

    args = parser.parse_args()

    CTwindow = args.CTwindow
    # paths to data and save location
    filepath = Path(str(args.Inputfilepath[0])) # directory containing all dicom series of single patient

    # directory to save new metadata fields
    if args.Outputfilepath == None:
        newdir = filepath+'-processed'
    else:
        newdir = Path(str(args.Outputfilepath[0]))
    os.mkdir(newdir)

    # Create list of files in folder
    filenames = []
    for names in os.listdir(filepath):
        if not names.startswith('.'):
            filenames.append(names)

    # Read first file for patient name
    ds = pydicom.filereader.dcmread(str(filepath.joinpath(filenames[0])))
    patientname = str(ds.data_element('PatientName').value)
    print(patientname)
    os.mkdir(newdir.joinpath(patientname))
    newpatient_dir = newdir.joinpath(patientname)
    print('patient name: '+ patientname)

    series_names = []

    # Find all series names
    for dcm in filenames:
        ds = pydicom.filereader.dcmread(str(filepath.joinpath(dcm)))
        print(dcm)
        try:
            current_series = str(ds.data_element('SeriesDescription').value)
        except KeyError: # incase there is no series SeriesDescription tag.
            current_series = 'other'
        if current_series not in series_names:
            series_names.append(current_series)
            os.mkdir(newpatient_dir.joinpath(current_series))
            print('New image series: '+current_series)

    ## for all files
    error_number = 0
    for dcm in filenames:
        # load new dicom metadata
        ds = pydicom.filereader.dcmread(str(filepath.joinpath(dcm)))
        try:
            current_series = str(ds.data_element('SeriesDescription').value)
        except KeyError:
            current_series = 'other'
        # Set patient's DOB to anonymise
        try:
            ds.data_element('PatientBirthDate').value = '19000101'
        except KeyError:
            pass
        try:
            filenumber = ds.data_element('InstanceNumber').value
        except KeyError:
            # incase no instance number
            error_number = error_number + 1
            filenumber = error_number
        # Change default CT window to pulmonary
        try:
            ds.data_element('WindowCenter').value = CTwindow[0]
            ds.data_element('WindowWidth').value = CTwindow[1]
        except KeyError:
            pass
        newfile = 'IM_%04d.dcm' %filenumber
        ## write the dcm file to new file
        print('New file: '+ str(newpatient_dir.joinpath(current_series).joinpath(newfile)))
        ds.save_as(str(newpatient_dir.joinpath(current_series).joinpath(newfile)))

    print('COMPLETE')
