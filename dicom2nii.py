# coding: utf8
import os.path
import sys
import time
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QStringListModel

import lib.folder
import lib.dcm
from ui import Ui_MainWindow


LIST_TYPE_UNDO = 1 # 左侧未执行类型
LIST_TYPE_DONE = 2 # 右侧已执行类型

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)
        self.setupUi(self)
        # 初始化局部变量
        self._init_variables()
        # 初始化用到的数据 model
        self._init_models()
        # 设置事件绑定
        self._bind_actions()

    def _init_variables(self):
        self.root_folder = ""
        # 设置运行目录 TODO 仅兼容 linux/Unix 系统，Windows 需额外设置
        self.log_folder = "/tmp/dicom2nii/log"
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder, exist_ok=True)

    def _init_log_info(self):
        filename = int(time.time())
        self.log_full_file = "{}/{}.log".format(self.log_folder, filename)
        self.log_error_file = "{}/{}.wf.log".format(self.log_folder, filename)

    def _log_access_log(self, filepath):
        with open(self.log_full_file, 'a+') as f:
            f.write(filepath+"\n")
            f.close()

    def _log_error_log(self, filepath, error):
        with open(self.log_error_file, 'a+') as f:
            line = "{},{}\n".format(filepath, error)
            f.write(line)
            f.close()

    def _init_models(self):
        self.succlist = []
        self.faillist = []
        self.undomodel = QStringListModel()
        self.donemodel = QStringListModel()

    def _bind_actions(self):
        self.selectFolderBtn.clicked.connect(self._action_selectFolder)
        self.convertBtn.clicked.connect(self._action_convert)
        self.binaryLayeredBtn.clicked.connect(self._action_binaryLayered)

        # 加入启动必知项
        self._about()

    def _update_listView(self, _type, ls):
        if _type == LIST_TYPE_UNDO:
            self.undomodel.setStringList(ls)
            self.undoListView.setModel(self.undomodel)
        elif _type == LIST_TYPE_DONE:
            self.donemodel.setStringList(ls)
            self.doneListView.setModel(self.donemodel)
        else:
            # 待添加其他 listview 更新相应
            pass

    def _action_selectFolder(self):
        folder = QFileDialog.getExistingDirectory(None, "选择读取的文件夹根目录", "~", QFileDialog.ShowDirsOnly)
        if folder == "":
            self.statusbar.showMessage("文件夹路径选择失败，请重新选择！")
            return
        self.root_folder = folder
        folders, action = lib.folder.get_folders(self.root_folder)
        if not action:
            msg = "扫描文件夹失败，请重试"
            QMessageBox.information(self, "Ooooooops~~~", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        self.folders = folders
        self._update_listView(LIST_TYPE_UNDO, self.folders)
        self._update_listView(LIST_TYPE_DONE, [])
        self.statusbar.showMessage("您选择的路径为：{}, 共扫描到：{}个文件夹".format(folder, len(self.folders)))

    def _action_convert(self):
        # 检查前置操作的根目录是否已选择
        if self.root_folder == "":
            msg = "您还没有要操作的选择文件夹哦"
            QMessageBox.information(self, "Ooooooops~~~", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return

        # 转换前要求用户选择要存储到的目录
        prompt = "转换前要选择输出到哪一个文件夹"
        QMessageBox.information(self, "Ooooooops~~~", prompt, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        output_folder = QFileDialog.getExistingDirectory(None, "选择要存储的文件夹根目录", "~", QFileDialog.ShowDirsOnly)
        if output_folder == "":
            self.statusbar.showMessage("文件夹路径选择失败，请重新选择！")
            return

        # 设置目录信息，以便于软件未关闭时每次转换都会有新的日志路径
        self._init_log_info()

        # 遍历处理转换行为
        done_list = []
        counter = 0
        for work_folder in self.folders:
            self._log_access_log(work_folder)
            counter += 1
            new_output = lib.folder.generate_new_path(self.root_folder, work_folder, output_folder)
            if new_output == "":
                self._log_error_log(work_folder, 'generate_new_path failed')
                continue

            # 执行目标转换操作
            new_output_folder = lib.folder.generate_new_path(self.root_folder, work_folder, output_folder)
            action_succ = lib.dcm.dcm_2_nii(work_folder, new_output_folder, "merged")
            if not action_succ:
                self._log_error_log(work_folder, 'convert dicom to nii failed')
                continue
            # 记录到成功列表
            done_list.append(new_output)

        self._update_listView(LIST_TYPE_UNDO, [])
        self._update_listView(LIST_TYPE_DONE, done_list)
        show_msg = "路径：{} 已被处理完毕；共：{}个，成功：{}个!".format(self.root_folder, len(self.folders), len(done_list))
        self.statusbar.showMessage(show_msg)

    def _action_binaryLayered(self):
        # 检查前置操作的根目录是否已选择
        if self.root_folder == "":
            msg = "您还没有要操作的选择文件夹哦"
            QMessageBox.information(self, "Ooooooops~~~", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return

        # 转换前要求用户选择要存储到的目录
        prompt = "转换前要选择输出到哪一个文件夹"
        QMessageBox.information(self, "Ooooooops~~~", prompt, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        output_folder = QFileDialog.getExistingDirectory(None, "选择要存储的文件夹根目录", "~",
                                                         QFileDialog.ShowDirsOnly)
        if output_folder == "":
            self.statusbar.showMessage("文件夹路径选择失败，请重新选择！")
            return

        # 设置目录信息，以便于软件未关闭时每次转换都会有新的日志路径
        self._init_log_info()

        # 遍历处理转换行为
        done_list = []
        counter = 0
        for work_folder in self.folders:
            self._log_access_log(work_folder)
            counter += 1
            new_output = lib.folder.generate_new_path(self.root_folder, work_folder, output_folder)
            if new_output == "":
                self._log_error_log(work_folder, 'generate_new_path failed')
                continue

            # 执行目标转换操作
            new_output_folder = lib.folder.generate_new_path(self.root_folder, work_folder, output_folder)
            action_succ = lib.dcm.dcm_layered_with_a_v(work_folder, new_output_folder)
            if not action_succ:
                self._log_error_log(work_folder, 'binary layered dicom to nii failed')
                continue
            # 记录到成功列表
            done_list.append(new_output)

        self._update_listView(LIST_TYPE_UNDO, [])
        self._update_listView(LIST_TYPE_DONE, done_list)
        show_msg = "路径：{} 已被处理完毕；共：{}个，成功：{}个!".format(self.root_folder, len(self.folders), len(done_list))
        self.statusbar.showMessage(show_msg)

    def _about(self):
        msg = """
        'DICOM转换工具' 使用说明书:

        1) 第一步骤：选择待操作的文件夹:
            选择最外层的目录即可

        2) 第二步骤：未选择输出目录时，系统会提示你进行选择的。
            '直接转换'：该操作会直接将 DICOM 文件转为 nii 格式
            '动静脉期分层转换'：该操作通过计算 MSE 进行动静脉期区分，再转为 nii 格式
        
        3）软件运行日志：系统每次转换都会生成一份日志，位于 /tmp/dicom/log/ （linux/unix，暂未适配 Windows） 

        4）免责声明:
            在使用本软件之前，请您备份好源数据文件，以免因程序故障造成不必要的损失。
            因使用此软件造成的任何信息、版权问题均由操作者本人承担。

            copyright@2023, 泰戈尔
        """
        QMessageBox.information(self, "关于", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    iconPath = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'Dicom2nii.icns')
    app.setWindowIcon(QIcon(iconPath))
    main = Main()
    main.setWindowTitle("DICOM 转 NIFTI(from-泰戈尔🤩的工具箱)")
    main.show()
    sys.exit(app.exec_())
