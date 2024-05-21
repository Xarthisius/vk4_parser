import numpy as np
import base64
import dotnetlist
import matplotlib.pyplot as plt
from xml.etree import ElementTree as ET

bounds = (390, 250, 203, 242)

im = np.zeros((bounds[2], bounds[3]))
im_flat = im.T.flat

tree = ET.parse("volume_data.xml")
for ad in tree.findall(".//AreaData"):
    buf = base64.b64decode(ad.text)
    l = dotnetlist.Dotnetlist.from_bytes(buf)
    a1 = np.array(l.records[2].record.values)
    pos = 0
    on = 1
    for a in a1:
        im_flat[pos: pos + a] = on
        pos += a
        on = ~on
    plt.imshow(im)
    plt.savefig("hi.png")
    plt.clf()

history = base64.b64decode(tree.find(".//History").text)
setting = dotnetlist.Dotnetlist.from_bytes(base64.b64decode(tree.find(".//Setting").text))
