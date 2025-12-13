# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : sub_assets_dialog
# Describe   : 说明描述
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/11/25__17:21
# -------------------------------------------------------
class SubAssetsInfoDialog(QDialog):
    UpdateAssetInfoSignal = QtCore.Signal(list)
    __TITLE__ = "子资产republish工具"

    def __init__(self, task_id):
        super( SubAssetsInfoDialog, self).__init__()
        self.task_id = task_id
        self.entity=shotgunfuns.get_entity_by_task_id(task_id)
