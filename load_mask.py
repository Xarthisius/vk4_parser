import matplotlib

matplotlib.use("Qt5Agg")
import numpy as np
import base64
import dotnetlist
import matplotlib.pyplot as plt
from xml.etree import ElementTree as ET
from vk4 import Vk4

dataset = Vk4.from_file("Vk4File")

data_image = dataset.color_light
v = np.frombuffer(data_image.data, dtype="uint8")
v.shape = (data_image.height, data_image.width, 3)


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
        im_flat[pos : pos + a] = on
        pos += a
        on = ~on

fig = plt.figure(frameon=False)
extent = (0, data_image.width, 0, data_image.height)
im1 = plt.imshow(v, extent=extent)

mask = np.zeros((data_image.width, data_image.height))
mask[bounds[0] : bounds[0] + bounds[2], bounds[1] : bounds[1] + bounds[3]] = im
im2 = plt.imshow(
    mask.T,
    extent=extent,
    alpha=0.2,
)

history = base64.b64decode(tree.find(".//History").text)
setting = dotnetlist.Dotnetlist.from_bytes(
    base64.b64decode(tree.find(".//Setting").text)
)

plt.show()
