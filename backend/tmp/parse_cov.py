import xml.etree.ElementTree as ET
import os
p='tmp/backend-coverage.xml'
root=ET.parse(p).getroot()
files=[]
for pkg in root.findall('.//package'):
    for cls in pkg.findall('.//class'):
        fn=cls.get('filename')
        lr=cls.get('line-rate')
        if lr is None:
            lr='0'
        files.append((fn,float(lr)))
files.sort(key=lambda x:x[1])
for fn,lr in files:
    print(f"{lr*100:6.2f}%  {os.path.normpath(fn)}")
