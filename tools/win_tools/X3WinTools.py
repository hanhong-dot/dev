# -*- coding: utf-8 -*-

import sys, os, threading

sys.path.append(r'Z:\dev\Ide\python310\site-packages')
import yaml

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

# try:
#     _fromUtf8 = QtCore.QString.fromUtf8
# except AttributeError:
#     def _fromUtf8(s):
#         return s
try:
    _encoding = QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)


# class TrayIcon(QSystemTrayIcon):
#     def __init__(self, parent=None):
#         super(TrayIcon, self).__init__(parent)
#         self.showMenu()


def Analysis_yaml(config_path):
    with open(config_path, 'rb') as f:
        cont = f.read()
    content = yaml.load(cont, Loader=yaml.FullLoader)
    return content


class TrayIcon(QSystemTrayIcon):

    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.showMenu()

    def showMenu(self):
        self.Datadict = {}
        # Data = Analysis_yaml('//10.10.201.151/share/development/dev/tools/win_tools/x3_menu_config.yml')
        Data = Analysis_yaml('//10.10.201.151/share/development/dev/tools/win_tools/x3_menu_config.yml')
        # 创建托盘目录
        self.contextMenu = QMenu()
        for keyMenu, Menuvalue in Data.items():
            if 'FirstMenu' in keyMenu:
                for valuedic in Menuvalue:
                    for newkey in valuedic:
                        if newkey == 'MainTitle':
                            title = valuedic['MainTitle']
                            continue
                        if newkey == 'MainIcon':
                            icon = valuedic['MainIcon']
                            continue
                        if newkey == 'MainCMD':
                            cmd = valuedic['MainCMD']
                            continue
                        if newkey == 'MainMethod':
                            method = valuedic['MainMethod']
                            continue
                Menu = self.contextMenu.addAction(QIcon(icon), title)
                # Menu.triggered.connect(lambda: self.RunTread(method))
                Menu.triggered.connect(self.RunTread)

                self.Datadict.setdefault(title, []).extend([method[0], cmd])

            if 'SecondMenu' in keyMenu:
                for valuedic in Menuvalue:
                    for newkey in valuedic:
                        if newkey == 'MainTitle':
                            Maintitle = valuedic['MainTitle']
                            continue
                        if newkey == 'MainIcon':
                            Mainicon = valuedic['MainIcon']
                            continue
                        if newkey == 'SecondTitle':
                            Secondtitle = valuedic['SecondTitle']
                            continue
                        if newkey == 'MainCMD':
                            cmd = valuedic['MainCMD']
                            continue
                        if newkey == 'SecondMethod':
                            Secondmethod = valuedic['SecondMethod']
                            continue
                MainMenu = self.contextMenu.addMenu(QIcon(Mainicon), Maintitle)
                for i in range(len(Secondtitle)):
                    Menu = MainMenu.addAction(Secondtitle[i])
                    Menu.triggered.connect(self.RunTread)
                    self.Datadict.setdefault(Secondtitle[i], []).append(Secondmethod[i], cmd)

        self.messageClicked.connect(self.messageInfo)

        self.contextMenu.addSeparator()

        self.restAction = self.contextMenu.addAction(
            QIcon("//10.10.201.151/share/development/dev/ico/large/restart.png"), u'重启')
        self.restAction.triggered.connect(self.restart)

        self.contextMenu.addSeparator()

        self.quitAction = self.contextMenu.addAction(
            QIcon("//10.10.201.151/share/development/dev/ico/large/quit.png"), u'退出')

        self.quitAction.triggered.connect(qApp.quit)

        # 添加分隔线
        self.contextMenu.addAction(self.quitAction)
        # 设置目录为创建的目录
        self.setContextMenu(self.contextMenu)

    def restart(self):
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        global Mywindow
        try:
            Mywindow.close()
            Mywindow.deleteLater()
        except:
            pass
        Mywindow = TrayIcon()
        Mywindow.setIcon(QIcon("//10.10.201.151/share/development/dev/ico/sq32/tools/Tray_Toolset.png"))
        Mywindow.show()
        Mywindow.showMessage(u'X3托盘工具', u'鼠标右键点击该图标会显示托盘内容', QSystemTrayIcon.MessageIcon(1), 1000)
        app.exec_()

    def RunTread(self):
        action = self.sender()
        if self.Datadict:
            for key, value in self.Datadict.items():

                if action.text() == key:
                    threading.Thread(target=self.RunMain, args=(value[0], value[1])).start()

    def RunMain(self, method, cmd):
        if cmd == True:
            os.system(method)
        else:
            import subprocess
            subprocess.Popen(method, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def messageInfo(self):
        print(u'右键点击图标，显示托盘内容，鼠标左键选择点击')

    def start(self):
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        Mywindow = TrayIcon()
        Mywindow.setIcon(QIcon("//10.10.201.151/share/development/dev/ico/sq32/work.png"))
        Mywindow.show()
        Mywindow.showMessage(u'X3托盘工具', u'鼠标右键点击该图标会显示托盘内容', QSystemTrayIcon.MessageIcon(1), 1000)
        app.exec_()

#
# if __name__ == "__main__":
#     import sys
#
#     app = QApplication(sys.argv)
#     Mywindow = TrayIcon()
#     Mywindow.setIcon(QIcon(r"//10.10.201.151/share/development/dev/ico/sq32/tools/Tray_Toolset.png"))
#     Mywindow.show()
#     Mywindow.showMessage(u'X3托盘工具', u'鼠标右键点击该图标会显示托盘内容', QSystemTrayIcon.MessageIcon(1), 1000)
#     sys.exit(app.exec_())
