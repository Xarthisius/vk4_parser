import base64
from xml.etree import ElementTree as ET

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

import dotnetlist
from vk4 import Vk4

dataset = Vk4.from_file("Vk4File")

data_image = dataset.color_light
v = np.frombuffer(data_image.data, dtype="uint8")
v.shape = (data_image.height, data_image.width, 3)

fig = plt.figure(frameon=False)
extent = (0, data_image.width, 0, data_image.height)
im1 = plt.imshow(v, extent=extent)

tree = ET.parse("volume_data.xml")

# find all arrayitem with attribute typeId="blah"
for measure_area in tree.findall(".//MeasureAreaInfos/ArrayItem"):
    bounds = tuple(int(_) for _ in measure_area.find(".//AreaBounds").text.split(","))
    im = np.zeros((bounds[2], bounds[3]))
    im_flat = im.T.flat

    label_location = tuple(int(_) for _ in measure_area.find(".//LableLocation").text.split(","))
    label = measure_area.find(".//Number").text

    area_data = measure_area.find(".//AreaData")
    area = dotnetlist.Dotnetlist.from_bytes(base64.b64decode(area_data.text))
    pos = 0
    on = 1
    for offset in area.records[2].record.values:
        im_flat[pos : pos + offset] = on
        pos += offset
        on = ~on

    mask = np.zeros((data_image.width, data_image.height))
    mask[bounds[0] : bounds[0] + bounds[2], bounds[1] : bounds[1] + bounds[3]] = im
    plt.imshow(
        mask.T,
        extent=extent,
        alpha=0.3,
        cmap=ListedColormap(["blue", "none"]),
        interpolation="nearest",
    )
    lbl = plt.text(
        label_location[0],
        768 - label_location[1],
        label,
        fontsize=12,
        color="black",
        ha="left",
        va="top",
        family="monospace",
    )
    lbl.set_bbox(dict(facecolor="white", alpha=0.5, edgecolor="white"))

setting = dotnetlist.Dotnetlist.from_bytes(
    base64.b64decode(tree.find(".//Setting").text)
)
imp = np.zeros((data_image.width, data_image.height))
im_flat = imp.T.flat
pos = 0
on = 1
for offset in setting.records[2].record.values:
    im_flat[pos : pos + offset] = on
    pos += offset
    on = ~on

im3 = plt.imshow(
    (imp - mask).T,
    extent=extent,
    alpha=0.4,
    cmap=ListedColormap(["cyan", "none"]),
    interpolation="nearest",
)

plt.savefig("keyence.png", dpi=150)
