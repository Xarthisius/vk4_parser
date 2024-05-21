import numpy as np
import base64
import dotnetlist
import matplotlib.pyplot as plt
from xml.etree import ElementTree as ET

bounds = (390, 250, 203, 242)

im = np.zeros((bounds[2], bounds[3]))

tree = ET.parse("volume_data.xml")
for ad in tree.findall(".//AreaData"):
    buf = base64.b64decode(ad.text)
    l = dotnetlist.Dotnetlist.from_bytes(buf)
    arr = np.array(l.records[2].record.values).reshape((-1, 2), order='F')
    arr = arr[arr[:,0] > 0, :]
    for pair in arr:
        im[pair[1], pair[0]] = 1
    plt.imshow(im)
    plt.savefig("hi.png")
    plt.clf()
    plt.plot(arr[:,0], arr[:,1])
    plt.savefig("hi2.png")

history = base64.b64decode(tree.find(".//History").text)
setting = dotnetlist.Dotnetlist.from_bytes(base64.b64decode(tree.find(".//Setting").text))
