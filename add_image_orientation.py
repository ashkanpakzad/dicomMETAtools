import os
import pydicom

# paths to data and save location
filepath = './data/' # directory containing the dicom series
dcmprefix = 'Image_' # Individual dicom file prefix before number
firstdcm = dcmprefix + '%04d.DICOM' %1 # first dicom image to inspect metadata fields
newdir = './data-edited/' # directory to save new metadata fields

# Find total number of dicom files in series
j = 0
for file in os.listdir(filepath):
    if file.endswith(".DICOM"):
        j = j + 1
totaldcm = j 

# Read all tags for first image
ds = pydicom.filereader.dcmread(filepath+firstdcm)
print(ds)

## load the data
for i in range(totaldcm):
    filenumber = i+1
    name = '%04d.DICOM' %filenumber
    ds = pydicom.filereader.dcmread(filepath+dcmprefix+name)
    if i == 0: ## 1. Adding slicelocation for first dicom image
        ds.SliceLocation = '0.000000'
    else:
        pass
    ## 2. Set ImageOrientation Patient for all images
    ds.add_new('0x00200037', 'DS', ['1.000000','0.000000','0.000000','0.000000','1.000000','0.000000'])
    ## write the dcm file to new directory
    ds.save_as(newdir+dcmprefix+name)

print('COMPLETE')
