import pydicom
import json

ds = pydicom.filereader.dcmread('IM-0002-0001.dcm')
ds.remove_private_tags()
del ds.ReferencedImageSequence
del ds.PixelData
# ds = pydicom.Dataset()
# ds.PatientID = 'name'

#print(ds)
out = ds.to_json()

f = open('raw.json', 'w')
f.write(out)
print("JSON saved!")
