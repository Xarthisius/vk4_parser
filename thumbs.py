from vk4 import Vk4
import numpy as np
import matplotlib.pyplot as plt

dataset = Vk4.from_file("Vk4File")
f, axarr = plt.subplots(2, 2)

for i, data_image in enumerate(
    [
        dataset.light_thumbnail,
        dataset.height_thumbnail,
        dataset.color_peak_thumbnail,
        dataset.color_light_thumbnail,
    ]
):
    v = np.frombuffer(data_image.data, dtype="uint8")
    v.shape = (data_image.height, data_image.width, 3)
    axarr.ravel()[i].imshow(v)

f.savefig("thumbs.png")
