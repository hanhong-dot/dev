# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : treedirs
# Describe   : 实现树目录功能部件
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2022/10/14__15:59
# -------------------------------------------------------
import uuid
import sys

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from Qt.QtWidgets import *
    from Qt.QtGui import *
    from Qt.QtCore import *



class TreeGroups(QTreeWidget):
    u'''
    树形部件类，实现相关从接口读取树形数据，并显示
    以及相关触信号等
    '''
    item_updata_signal = Signal(object)
    def __init__(self, data={}):
        super(TreeGroups, self).__init__()
        self.setColumnCount(1)
        self.setHeaderLabel(u'子资产目录')
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # 重新添加右键菜单，增加项目目录
        self.customContextMenuRequested.connect(self.show_menu)

        self.model = data
        self.delete_data = []
        self.presse_widget_item = ''
        self.old_item = ''
        self.pop_menu = True
        self.menu = QMenu()
        # 初始化函数
        self.init_menu()
        self.init_tree()
        # 取消可拖拽
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setAcceptDrops(True)
        # 信号
        self.menu.triggered.connect(self.action_reposed)
        self.itemPressed.connect(self.get_pressed_item)

    def test(self):
        for i in range(10):
            treewidget_item = QTreeWidgetItem(self, '{}'.format(i))

    def init_menu(self):
        u'''
        初始化树状目录的菜单，当前情况下，不使用左侧
        树目录。
        :return: None
        '''
        self.menu.addAction(u'添加子文件夹')
        self.menu.addAction(u'添加根文件夹')
        self.menu.addAction(u'删除文件夹')
        self.menu.addAction(u'重命名')

    def add_root_node(self):
        '''
        添加根节点,更新根节点
        :return:
        '''
        hex = uuid.uuid1().get_hex()
        temp = QTreeWidgetItem()
        input_dialog_dilaog = QInputDialog()
        input_dialog_dilaog.setWindowTitle(u'输入框')
        input_dialog_dilaog.setLabelText(u'输入名字')
        input_dialog_dilaog.setInputMode(QInputDialog.TextInput)

        if input_dialog_dilaog.exec_() == QInputDialog.Accepted:
            #
            temp.setText(0, input_dialog_dilaog.textValue())
            temp.setData(0, Qt.UserRole, hex)
            # 更新到数据库中
            self.model[u'根目录'].append(hex)
            self.model[hex] = [input_dialog_dilaog.textValue(), [], '']
            self.model.update(self.model)
            self.addTopLevelItem(temp)

    def delete_all_nodes(self):
        '''
        删除所有的节点。当前不使用
        :return:
        '''
        pass

    def add_chiled_node(self):
        '''
        添加新的子节点,并更新到数据库中。
        当前不再使用此函数。
        :return:
        '''
        hex = uuid.uuid1().get_hex()
        temp = QTreeWidgetItem()
        input_dialog_dilaog = QInputDialog()
        input_dialog_dilaog.setWindowTitle(u'输入框')
        input_dialog_dilaog.setLabelText(u'输入名字')
        input_dialog_dilaog.setInputMode(QInputDialog.TextInput)
        item = self.currentItem()
        if input_dialog_dilaog.exec_() == QInputDialog.Accepted:
            temp.setText(0, input_dialog_dilaog.textValue())
            temp.setData(0, Qt.UserRole,  hex)
            # 写入字典
            item.addChild(temp)
            item_data = item.data(0, Qt.UserRole)
            # 获取父元素字典，将该元素添加到父元素字典中
            self.model[item_data][1].append(temp.data(0, Qt.UserRole))
            # 初始化新添加的元素字典
            # self.data[temp.data(0, Qt.UserRole)] = [input_dialog_dilaog.textValue(), [], item_data]
            self.model[temp.data(0, Qt.UserRole)] = [input_dialog_dilaog.textValue(), [], item_data]
            self.model.update(self.model)


    def delete_node(self):
        '''
        删除选中的节点
        ,并更新相应的数据库,删除该节点下的所有子节点
        :return:
        '''
        self.delete_data = []
        delete_id = []
        item = self.currentItem()
        parent = item.parent()
        item_id = item.data(0, Qt.UserRole)
        # children_list = self.data[item_id][1]
        # parent_id = self.data[item_id][2]
        children_list = self.model[item_id][1]
        parent_id = self.model[item_id][2]

        # 搜集需要删除的节点
        self.delete_data.append(item_id)

        for children in children_list:
            self.delete_data.append(children)
            self.find_children(children)

        if not parent:
            # 是根目录
            index = self.indexFromItem(item)
            row = index.row()
            # self.data[u'根目录'].remove(item_id)
            self.model[u'根目录'].remove(item_id)
            self.takeTopLevelItem(row)

        else:
            # self.data[parent_id][1].remove(item_id)
            parent.removeChild(item)
            self.model[parent_id][1].remove(item_id)


        # 获取需删除字典后，开始删除self.data数据，以及资产与其关联的目录id
        # 程序合并后，使用接口删除
        self.model.update(self.model)

    def find_children(self, item):
        '''
        查找节点下的子节点
        :param item: QTreeWidgetItem
        :return: none
        '''
        for chilren in self.model[item][1]:
            self.delete_data.append(chilren)
            self.find_children(chilren)

    def rename_node(self):
        '''
        用户可以重命名当前节点,并将数据更新到字典中，
        当前不再使用此函数
        :return:
        '''
        q_input_dialog = QInputDialog(self)
        q_input_dialog.setWindowTitle(u'修改名字')
        q_input_dialog.setLabelText(u'输入名字')
        q_input_dialog.setInputMode(QInputDialog.TextInput)
        if q_input_dialog.exec_() == QInputDialog.Accepted:
            text_value = q_input_dialog.textValue()
            old_text_value = self.currentItem().text(0)
            id = self.currentItem().data(0, Qt.UserRole)
            self.model[id][0] = text_value
            self.currentItem().setText(0, text_value)
            # 更新到字典中的数据

        self.model.update(self.model)


    def show_menu(self):
        '''
        点击右键，触发树状图右键菜单执行函数。
        # 可重写
        :return: None
        '''
        if not self.pop_menu:
            return False
        # QCursor.pos()获取的是全局坐标
        self.menu.move(QCursor.pos())
        self.menu.show()

    def action_reposed(self, action):
        '''
        点击右键菜单之后，执行菜单槽。
        :return: None
        '''
        action_text = action.text()
        if action_text == u'添加子文件夹':
            self.add_chiled_node()

        elif action_text == u'添加根文件夹':
            self.add_root_node()

        elif action_text == u'删除文件夹':
            self.delete_node()

        elif action_text == u'重命名':
            self.rename_node()

        elif action_text == u'本地加载资产库':
            # 直接记录本地的数据
            pass

    def init_tree(self, data=[]):
        '''
        初始化文件夹树目录
        # LastModifed：更新数据库目录
        :param data: 记录树的层级
        :return: None
        '''
        # data = self.data
        data = self.model
        if data:
            for root in data:
                # 获取根目录名称
                if isinstance(root,str):
                    temp_root_name = root
                if isinstance(root,dict):
                    temp_root_name = root.keys()[0]
                tree_widget_item = QTreeWidgetItem()
                tree_widget_item.setText(0, temp_root_name)
                tree_widget_item.setData(0, Qt.UserRole, root)
                self.addTopLevelItem(tree_widget_item)
                # 添加子树
                if isinstance(root,dict):
                    self.add_child_tree(tree_widget_item, root[temp_root_name])
                # self.add_child_tree(tree_widget_item,self.model[root][1])
        else:
            self.model.tree_data = {u"根目录": []}

    def add_child_tree(self, parent, children_list):
        '''
        根据父类，以及需要添加的子树，完成相关的子树添加效果。
        :param parent: 树元素，
        :param children_list: children列表。
        :return: None
        '''
        # 递归添加子树

        for children in children_list:
            if isinstance(children,str):
                temp_dir_name = children
                temp_widget_item = QTreeWidgetItem()
                temp_widget_item.setText(0, temp_dir_name)
                temp_widget_item.setData(0, Qt.UserRole, children)
                parent.addChild(temp_widget_item)
            if isinstance(children,dict):
                temp_dir_name = children.keys()[0]
                second_children_list = children.values()[0]
                temp_widget_item = QTreeWidgetItem()
                temp_widget_item.setText(0, temp_dir_name)
                temp_widget_item.setData(0, Qt.UserRole, children)
                parent.addChild(temp_widget_item)
                self.add_child_tree(temp_widget_item, second_children_list)

    def enterEvent(self, event):
        '''
        是否接收进入事件
        :param event:
        :return:
        '''
        event.ignore()

    def dropEvent(self, event):
        '''
        拖拽事件发生时，接受拖拽事件，并进行相关的操作（包括目录树本身的相互移动，或者外部部件
        移动到目录树上。）
        :param event:
        :return:
        '''
        source = event.source()
        if not isinstance(source,TreeGroups):
            self.drop_dir(event)
            return True
        super(TreeGroups, self).dropEvent(event)

    def change_children_index_new_parent_none(self, parent_widget_item, current_widget_item):
        '''
        更改树目录位置时，更改树目录数据结构
        :param parent_widget_item: 树元素
        :param current_widget_item: 树元素
        :return: None
        '''
        top_item_id = []
        current_widget_id = current_widget_item.data(0, Qt.UserRole)
        # old_parent_id = self.data[current_widget_id][2]
        old_parent_id = self.model[current_widget_id][2]
        # self.data[current_widget_id][2] = None
        # self.data[old_parent_id][1].remove(current_widget_id)
        self.model[current_widget_id][2] = ''
        self.model[old_parent_id][1].remove(current_widget_id)

        # 开始排序
        root_len = len(self.model[u'根目录'])
        current_widget_item_row = self.indexFromItem(current_widget_item).row()
        if root_len < current_widget_item_row+1:
            # 元素加到列尾
            self.model[u'根目录'].append(current_widget_id)
        elif root_len >= current_widget_item_row+1:
            # 元素加到中间
            for toplevel_item_number in range(self.topLevelItemCount()):
                toplevel_item = self.topLevelItem(toplevel_item_number)
                temp_item_id = toplevel_item.data(0, Qt.UserRole)
                top_item_id.append(temp_item_id)
            self.model[u'根目录'] = top_item_id

    def change_children_index_old_parent_none(self, parent_widget_item, current_widget_item):
        '''
        处理之前根元素现在为子元素的情况
        当前有父元素，之前没有父元素
        :return:
        '''
        current_item_id = current_widget_item.data(0, Qt.UserRole)
        parent_widget_item_id = parent_widget_item.data(0, Qt.UserRole)
        self.model[u'根目录'].remove(current_item_id)
        self.model[current_item_id][2] = parent_widget_item_id

        current_widget_item_row = self.indexFromItem(current_widget_item).row()
        if len(self.model[parent_widget_item_id][1]) < current_widget_item_row + 1:
            # 元素加到列尾
            self.model[parent_widget_item_id][1].append(current_item_id)
        elif len(self.model[parent_widget_item_id][1]) >= current_widget_item_row + 1:
            # 元素加到中间
            child_id_list = []
            child_count = parent_widget_item.childCount()
            for index in range(child_count):
                temp_child_item = parent_widget_item.child(index)
                temp_child_item_id = temp_child_item.data(0, Qt.UserRole)
                child_id_list.append(temp_child_item_id)
            self.model[parent_widget_item_id][1] = child_id_list

    def change_children_index(self, parent_widget_item, current_widget_item):
        '''
        当元素移动后，父元素已变化后，调用该函数
        :param parent_widget_item:
        :param current_widget_item:
        :return:
        '''
        # 数据中父节点和当前节点不相同，剔除原父类中的当前元素，修改当前元素的父类为当前的父类
        # 同时当前父类增加当前元素
        current_item_id = current_widget_item.data(0, Qt.UserRole)
        old_parent_widget_item_id = self.model[current_item_id][2]
        new_parent_widget_item_id = parent_widget_item.data(0, Qt.UserRole)
        # 删除old parent item id
        self.model[old_parent_widget_item_id][1].remove(current_item_id)
        # 替换该元素的新父部件
        self.model[current_item_id][2] = new_parent_widget_item_id

        # 将改元素id添加到新父部件子列表中，注意子部件顺序
        current_widget_item_row = self.indexFromItem(current_widget_item).row()
        if len(self.model[new_parent_widget_item_id][1]) < current_widget_item_row + 1:
            # 元素加到列尾
            self.model[new_parent_widget_item_id][1].append(current_item_id)
        elif len(self.model[new_parent_widget_item_id][1]) >= current_widget_item_row + 1:
            # 元素加到中间
            child_id_list = []
            child_count = parent_widget_item.childCount()
            for index in range(child_count):
                temp_child_item = parent_widget_item.child(index)
                temp_child_item_id = temp_child_item.data(0, Qt.UserRole)
                child_id_list.append(temp_child_item_id)
            self.model[new_parent_widget_item_id][1] = child_id_list

    def change_children_index_position(self, parent_widget_item, current_widget_item):
        '''
        当前元素父类未变，只是交换了树的位置
        :param parent_widget_item: 父元素
        :param current_widget_item: 当前元素
        :return:
        '''
        item_id_list = []
        parent_widget_item_id = parent_widget_item.data(0, Qt.UserRole)
        current_item_id = current_widget_item.data(0, Qt.UserRole)
        # 查询之前在父节点中的位置
        old_index = self.model[parent_widget_item_id][1].index(current_item_id)
        new_index = self.indexFromItem(current_widget_item).row()  # QModelIndex
        if old_index == new_index:
            # 无需做任何修改
            return
        else:
            # 新旧索引不一样,替换相关顺序
            children_count = parent_widget_item.childCount()
            for children_number in range(children_count):
                temp_item = parent_widget_item.child(children_number)
                item_id_list.append(temp_item.data(0, Qt.UserRole))

            self.model[parent_widget_item_id][1] = item_id_list

    def get_pressed_item(self, item, column):
        '''
        函数形参传入被点击的树元素实例，并将其记录下来
        :param item: QTreeWidgetItem子元素
        :param column: 第几列
        :return: None
        '''
        self.presse_widget_item = item
        self.old_parent_widget_tem = item.parent()


    def dragEnterEvent(self, event):
        '''
        是否接受拖拽事件
        :param event:
        :return: None
        '''
        event.accept()

    def dragMoveEvent(self, event):
        '''
        检测鼠标移动事件，并进行相关的元素修改操作
        :param event: 物件移动事件
        :return:
        '''
        source = event.source()
        if not isinstance(source, TreeGroups):
            postion = event.pos()
            item = self.itemAt(postion)
            if item:
                if self.old_item:
                    self.old_item.setSelected(False)
                item.setSelected(True)
            self.old_item = item
        super(TreeGroups, self).dragMoveEvent(event)

    def dragLeaveEvent(self, event):
        '''
        鼠标离开事件
        :param event: 事件
        :return: None
        '''
        if self.old_item:
            self.old_item.setSelected(False)

    def drop_dir(self, event):
        '''
        处理图像视频拖拽到树目录情况
        :param event:
        :return:
        '''
        source = event.source()
        pos = event.pos()
        # 获得新元素id
        new_dir_item = self.itemAt(pos)
        new_dir_id = new_dir_item.data(0, Qt.UserRole)
        asset_id = source.asset_data['id']
        self.model.update_tree_value(asset_id, 'sg_dir_id'
                                     , new_dir_id)

        self.item_updata_signal.emit(new_dir_item)
        # 更换id


if __name__ == '__main__':
    app = QApplication(sys.argv)

    data=[{'FY001C': ['FY001W']}, 'FY001S', 'FY001S01', 'FY001S_Nnl', 'FY001S_test', 'FY003S', 'FY003S01', 'FY004S', 'FY005C', 'FY006S', 'FY007S', 'NPC_M01']
 #    data = {u'0e047e800a0211ebadffb8ca3a76bcf5': [u'1_1_1',
 #                                       [],
 #                                       u'e99da5800a0111eb954bb8ca3a76bcf5'],
 # u'1e4bd2700a0211eb9aaab8ca3a76bcf5': [u'2_1',
 #                                       [],
 #                                       u'e2edc3510a0111eb9cd0b8ca3a76bcf5'],
 # u'8d58b5c00a9811eb97f4b8ca3a76bcf5': [u'aaa',
 #                                       [],
 #                                       u'e2edc3510a0111eb9cd0b8ca3a76bcf5'],
 # u'90d7318f09fd11eb9b37b8ca3a76bcf5': [u'2222',
 #                                       [u'e99da5800a0111eb954bb8ca3a76bcf5',
 #                                        u'9291d6700a9811eb9048b8ca3a76bcf5'],
 #                                       u'id1'],
 # u'9291d6700a9811eb9048b8ca3a76bcf5': [u'aaaaa',
 #                                       [],
 #                                       u'90d7318f09fd11eb9b37b8ca3a76bcf5'],
 # '9b1802b009fd11ebbfbcb8ca3a76bcf5': [u'1111111111',
 #                                      [u'e81334ee0a0111eb9d02b8ca3a76bcf5'],
 #                                      ''],
 # u'e2edc3510a0111eb9cd0b8ca3a76bcf5': [u'dsadsa',
 #                                       [u'1e4bd2700a0211eb9aaab8ca3a76bcf5',
 #                                        u'8d58b5c00a9811eb97f4b8ca3a76bcf5'],
 #                                       u'id2'],
 # u'e614309e0a0111eba896b8ca3a76bcf5': [u'dsadsadsadsa', [], u'id3'],
 # u'e81334ee0a0111eb9d02b8ca3a76bcf5': [u'dsad',
 #                                       [],
 #                                       u'9b1802b009fd11ebbfbcb8ca3a76bcf5'],
 # u'e99da5800a0111eb954bb8ca3a76bcf5': [u'dadsad',
 #                                       [],
 #                                       u'90d7318f09fd11eb9b37b8ca3a76bcf5'],
 # u'id1': [u'\u6839\u76ee\u5f551', [u'90d7318f09fd11eb9b37b8ca3a76bcf5'], ''],
 # u'id2': [u'\u6839\u76ee\u5f552', [u'e2edc3510a0111eb9cd0b8ca3a76bcf5'], ''],
 # u'id3': [u'\u6839\u76ee\u5f553', [u'e614309e0a0111eba896b8ca3a76bcf5'], ''],
 # u'\u6839\u76ee\u5f55': [u'id1', u'id2']}
    # model_instance = base_data.EfxLibrary(project='X3')
    # model_instance = {"test01":{"test02":"ss"}}
    # model_instance.get_tree_data()
    treewidget = TreeGroups(data)
    treewidget.show()
    sys.exit(app.exec_())
