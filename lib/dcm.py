# coding: utf8
import os
import numpy as np
import SimpleITK as sitk


def _read_dcm(dir_path):
    reader = sitk.ImageSeriesReader()
    img_name = reader.GetGDCMSeriesFileNames(dir_path)
    reader.SetFileNames(img_name)
    image = reader.Execute()
    image_array = sitk.GetArrayFromImage(image)
    return image, image_array

def dcm_2_nii(dir_path, dest_path, filename):
    # 参数校验
    if not os.path.exists(dir_path) or not dest_path or not filename:
        return False, "dir_path={} or dest_path={} or filename={} invalid.".format(dir_path, dest_path, filename)

    # 读取 DICOM 序列信息
    try:
        image, image_array = _read_dcm(dir_path)
    except Exception as e:
        return False, str(e)

    # 查看各项指标
    origin = image.GetOrigin()
    spacing = image.GetSpacing()
    direction = image.GetDirection()

    # 将array转为img，并保存为 xx.nii.gz
    image3 = sitk.GetImageFromArray(image_array)
    image3.SetSpacing(spacing)
    image3.SetDirection(direction)
    image3.SetOrigin(origin)

    # 根据 dest_path 生成完整的目录
    try:
        dest_path = dest_path if not str(dest_path).endswith(os.sep) else str(dest_path).rstrip(os.sep)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path, exist_ok=True)
        filename = filename if str(filename).endswith('.nii.gz') else "{}.nii.gz".format(filename)
        full_name = "{}/{}".format(dest_path, filename)
        sitk.WriteImage(image3, full_name)
    except Exception as e:
        return False, str(e)

    return True, 'success converted'


def dcm_layered_with_a_v(dir_path, dest_path):
    """
    将 DICOM 分割成静脉期（Venous phase 本处命名为 3b）和动脉期（ Arterial phase 本处命名为 3a），并转储为 nii 格式
    :param dir_path: 源文件夹
    :param dest_path: 目标输出文件夹
    :return:
    """
    if dir_path == "" or not os.path.exists(dir_path):
        return False, "dir_path={} 为空或不存在".format(dir_path)
    if dest_path == "":
        return False, "dest_path={} 不能为空".format(dest_path)
    os.makedirs(dest_path, exist_ok=True)
    try:
        image, image_array = _read_dcm(dir_path)
    except Exception as e:
        return False, str(e)

    if image == None or len(image_array) <= 0:
        return False, "image or image_array 为空"

    # 通过计算 MSE 来区分图层差异最大的位置
    mse = np.sum((image_array[:-1] - image_array[1:]).reshape((image_array.shape[0] - 1, -1)) ** 2, axis=-1) ** 0.5
    target_index = np.argmax(mse)

    # 动脉期
    image_arterial = image_array[:target_index+1]
    image_arterial = sitk.GetImageFromArray(image_arterial)
    image_arterial.SetSpacing(image.GetSpacing())
    sitk.WriteImage(image_arterial, os.path.join(dest_path, "3a.nii.gz"))

    # 静脉期
    image_venous = image_array[target_index+1:]
    image_venous = sitk.GetImageFromArray(image_venous)
    image_venous.SetSpacing(image.GetSpacing())
    sitk.WriteImage(image_venous, os.path.join(dest_path, "3b.nii.gz"))
    return True, "success"
