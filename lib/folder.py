# coding: utf8
import os.path


def get_folders(root):
    # check the root path exists or not
    if not os.path.exists(root):
        return [], False

    # TODO maybe there should have a white list

    folders = []
    for full_path, dir_name, filenames in os.walk(root):
        # print("full_path={}, dir_name={}, filenames={}".format(full_path, dir_name, filenames))
        if dir_name:
            continue

        if full_path in folders:
            continue

        folders.append(full_path)

    # return the target folders within `root`
    return folders, True


def generate_new_path(root, dir_path, dest_root):
    """
    根据初始选择根目录、当前 dir_path 以及输出目录，生成目标目录
    :param root: 初始根目录
    :param dir_path 当前工作目录
    :param dest_root: 目标输出到的根目录
    :return:
    """
    # 参数校验
    root = root if not str(root).endswith(os.sep) else str(root).rstrip(os.sep)
    dir_path = dir_path if not str(dir_path).endswith(os.sep) else str(dir_path).rstrip(os.sep)
    dest_root = dest_root if not str(dest_root).endswith(os.sep) else str(dest_root).rstrip(os.sep)

    # 将 dir_path 剪切掉 root 部分，然后拼接到 dest_path 后面
    middle = dir_path.replace(root, "", 1)
    # print("root={}\ndir_path={}\ndest_path={}\nmiddle={}\n".format(root, dir_path, dest_root, middle))
    if middle == "":
        return ""
    final = "{}{}".format(dest_root, middle)
    return final

