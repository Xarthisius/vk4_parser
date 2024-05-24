import base64
import io
import os
import sys
import pathlib
import zipfile

import matplotlib.pyplot as plt
import numpy as np
from lxml import etree
from matplotlib.colors import ListedColormap
import xlsxwriter

import dotnetlist
from vk4 import Vk4

fname = sys.argv[1]

fmapping = {
    "f1724dc6-686c-4502-9227-2a594bc8ed33": "index.xml",
    "fef71eb3-bfa4-4c3b-be42-ff0c51255d07": "MeasurementDataMap.xml",
    "19455c0b-6b15-4158-be47-e07e14292f90": "AnalysisConfigurationMap.xml",
    "cb0f22ca-f0d1-4a62-8a9a-808cb51fb85c": "PerCellConfigurationMap.xml",
    "ebf6007c-1914-4535-96c9-45fcb6be8728": "GridConfigurationMap.xml",
    "385ef3bb-dae5-4ec4-b8c8-a71f73db8ffc": "VersionInfo.xml",
}

meta_files = {}
workbook = xlsxwriter.Workbook(f"{fname[:-4]}.xlsx")
worksheet = workbook.add_worksheet()
merge_format = workbook.add_format(
    {
        "bold": 0,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "fg_color": "#666666",
        "color": "white",
        "font_size": 10,
        "font_name": "Tahoma",
    }
)

worksheet.set_column(0, 0, 20)
worksheet.set_column(1, 1, 43)
worksheet.set_column(2, 4, 15)

worksheet.merge_range("A1:A3", "File Name", merge_format)
worksheet.merge_range("B1:E1", "Volume & Area", merge_format)
worksheet.merge_range("B2:B3", "Laser+Optical", merge_format)
worksheet.merge_range("C2:E2", "Measured values", merge_format)
worksheet.write("C3", "Volume [μm³]", merge_format)
worksheet.write("D3", "C.S. area [μm²]", merge_format)
worksheet.write("E3", "Surface [μm²]", merge_format)


def get_image(fname, zip_ref, tree):
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    fig.add_axes(ax)
    with zip_ref.open(fname) as f:
        with zipfile.ZipFile(f) as z:
            dataset = Vk4.from_bytes(z.read("Vk4File"))
            data_image = dataset.color_light
            v = np.frombuffer(data_image.data, dtype="uint8")
            v.shape = (data_image.height, data_image.width, 3)

            extent = (0, data_image.width, 0, data_image.height)
            ax.imshow(v, extent=extent)

            # find all arrayitem with attribute typeId="blah"
            for measure_area in tree.findall(".//MeasureAreaInfos/ArrayItem"):
                bounds = tuple(
                    int(_) for _ in measure_area.find(".//AreaBounds").text.split(",")
                )
                im = np.zeros((bounds[2], bounds[3]))
                im_flat = im.T.flat

                label_location = tuple(
                    int(_)
                    for _ in measure_area.find(".//LableLocation").text.split(",")
                )
                label = measure_area.find(".//Number").text

                area_data = measure_area.find(".//AreaData")
                area = dotnetlist.Dotnetlist.from_bytes(
                    base64.b64decode(area_data.text)
                )
                pos = 0
                on = 1
                for offset in area.records[2].record.values:
                    im_flat[pos : pos + offset] = on
                    pos += offset
                    on = ~on

                mask = np.zeros((data_image.width, data_image.height))
                mask[
                    bounds[0] : bounds[0] + bounds[2], bounds[1] : bounds[1] + bounds[3]
                ] = im
                ax.imshow(
                    mask.T,
                    extent=extent,
                    alpha=0.3,
                    cmap=ListedColormap(["blue", "none"]),
                    interpolation="nearest",
                )
                lbl = ax.text(
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

            ax.imshow(
                (imp - mask).T,
                extent=extent,
                alpha=0.4,
                cmap=ListedColormap(["cyan", "none"]),
                interpolation="nearest",
            )

            buf = io.BytesIO()
            fig.savefig(buf, dpi=100)
            plt.close(fig)
            return buf


with zipfile.ZipFile(fname, "r") as zip_ref:
    index = etree.fromstring(zip_ref.read("f1724dc6-686c-4502-9227-2a594bc8ed33"))
    for item in index.findall("Item"):
        typeId, path = item.getchildren()
        meta_files[fmapping[typeId.text]] = {
            "path": path.text,
            "tree": etree.fromstring(zip_ref.read(path.text)),
        }

    # Get Cross Section Area measurements
    volumes = {}
    term = ".//AnalysisKey[. = 'cde0af28-3791-4831-9fcf-5f73f53050d1']"
    for item in meta_files["PerCellConfigurationMap.xml"]["tree"].findall(term):
        item = item.getparent()
        # Get Path and FileItem
        path = item.find("Path").text
        fileItem = item.find("FileItem").text
        vol_path = os.path.join(
            os.path.dirname(meta_files["PerCellConfigurationMap.xml"]["path"]),
            path,
            "4dc4bcd6-0fac-4677-a83d-03132fed2eb1/60c3adb2-d2e3-4168-9629-8d8cb19bb751",
        )
        volumes[fileItem] = {
            "path": vol_path,
            "tree": etree.fromstring(zip_ref.read(vol_path)),
        }

    measurements = {}
    for key, volume in volumes.items():
        xpath = "/" + "/".join(
            [
                "VolumeAreaConfiguration",
                "VolumeAreaModel",
                "VolumeArea",
                "MeasurementResult",
                "VolumeAreaResults",
                "ArrayItem",
            ]
        )
        csa = float(volume["tree"].xpath(f"{xpath}/CrossSessionArea")[0].text) / 1e-12
        vol = float(volume["tree"].xpath(f"{xpath}/Volume")[0].text) / 1e-18
        sa = float(volume["tree"].xpath(f"{xpath}/SurfaceArea")[0].text) / 1e-12
        measurements[key] = {"vol": vol, "csa": csa, "sa": sa}

    # Get vk6 files
    vk6_files = {}
    for item in meta_files["MeasurementDataMap.xml"]["tree"].findall(
        ".//MeasurementData"
    ):
        # get path child
        path = item.find("Path").text
        origfname = pathlib.Path(
            item.find("OriginalFileName").text.replace("\\", "/")
        ).name
        vk6_files[origfname] = {
            "path": os.path.join(
                os.path.dirname(meta_files["MeasurementDataMap.xml"]["path"]),
                path,
                "84b648d7-e44f-4909-ac11-0476720a67ff",
            ),
        }

    i = 4
    for fname, volume in volumes.items():
        buf = get_image(vk6_files[f"{fname}.vk6"]["path"], zip_ref, volume["tree"])
        worksheet.write(f"A{i}", fname)
        worksheet.insert_image(
            f"B{i}", fname + ".png", {"image_data": buf, "x_scale": 0.5, "y_scale": 0.5}
        )
        worksheet.write(f"C{i}", measurements[fname]["vol"])
        worksheet.write(f"D{i}", measurements[fname]["csa"])
        worksheet.write(f"E{i}", measurements[fname]["sa"])
        worksheet.set_row(i - 1, 175)
        i += 1

workbook.close()
