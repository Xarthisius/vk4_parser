from vk4 import Vk4
import numpy as np
import matplotlib.pyplot as plt

dataset = Vk4.from_file("Vk4File")

f, axarr = plt.subplots(2, 2)

data_image = dataset.light[0].value
v = np.frombuffer(data_image.data, dtype="uint16")
v.shape = (data_image.height, data_image.width)
axarr[0, 0].imshow(v)

data_image = dataset.height[0].value
v = (
    np.frombuffer(data_image.data, dtype="uint32")
    * dataset.meas_conds.conditions.z_length_per_digit
    * 1e-12
)
v.shape = (data_image.height, data_image.width)
axarr[0, 1].imshow(np.log10(v))

data_image = dataset.color_peak
v = np.frombuffer(data_image.data, dtype="uint8")
v.shape = (data_image.height, data_image.width, 3)
axarr[1, 0].imshow(v)

data_image = dataset.color_light
v = np.frombuffer(data_image.data, dtype="uint8")
v.shape = (data_image.height, data_image.width, 3)
axarr[1, 1].imshow(v)

f.savefig("example.png")
