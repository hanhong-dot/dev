# -*- coding: utf-8 -*-
# author: linhuan
# file: batch_submit_variant_assets.py
# time: 2025/10/27 10:46
# description:
import sys
import os

sys.path.append('Z:/dev')

import database.shotgun.tools.actionitem.action_item_server as action_item_server
import database.shotgun.core.sg_base as sg_base
import apps.publish.process.maya.process_mb_sub_deadline as process_mb_sub_deadline


class BatchSubmitVariantAssets(object):
    def __init__(self):
        super(BatchSubmitVariantAssets, self).__init__()
        self.project = sys.argv[1]
        self.select_ids = sys.argv[2].split(',')

        self.entity_type = sys.argv[3]
        self.__sg = action_item_server.action_login()

    def submit(self):
        if not self.select_ids:
            print("No assets selected for submission.")
            return
        for asset_id in self.select_ids:
            if not asset_id:
                continue
            asset_id=int(asset_id)
            asset_name = self.get_asset_name(asset_id)
            if not asset_name:
                print("Asset {} retrieval failed. Skipping.".format(asset_id))
                continue

            print('Processing Asset : {}'.format(asset_name))
            __judge = self.__judge_item_asset(asset_id)
            if not __judge:
                print("Asset {} is not an item asset. Skipping.".format(asset_name))
                continue
            __judge_parent, parent_id_or_msg = self.__get_parent_item_asset(asset_id)
            if not __judge_parent:
                print("Asset {} parent check failed: {}. Skipping.".format(asset_name, parent_id_or_msg))
                continue


            result=process_mb_sub_deadline.batch_republish_item_variant_asset_deadline(asset_id, asset_name)
            if result:
                print("Asset {} submission successful.".format(asset_name))
            else:
                print("Asset {} submission failed.".format(asset_name))

    def get_asset_name(self, asset_id):
        filter = [['id', 'is', asset_id]]
        fields = ['code']
        asset_data = self.__sg.find_one('Asset', filter, fields)
        if not asset_data:
            return None
        return asset_data['code']

    def __judge_item_asset(self, asset_id):
        filter = [['id', 'is', asset_id], ['sg_asset_type', 'is', 'item']]
        fields = ['id']
        asset_data = self.__sg.find_one('Asset', filter, fields)
        if not asset_data:
            return False
        return True

    def __get_parent_item_asset(self, asset_id):
        fields = ['parents']
        filters = [
            ['id', 'is', asset_id]
        ]
        asset = self.__sg.find_one('Asset', filters, fields)
        if not asset or 'parents' not in asset or not asset['parents']:
            return False, u'not parent asset'
        parent_assets = asset['parents']
        item_parent_id = []
        for parent in parent_assets:
            parent_id = parent['id']
            __judge = self.__judge_item_asset(parent_id)
            if __judge:
                item_parent_id.append(parent_id)
        if not item_parent_id:
            return False, u'not item parent asset'
        if len(item_parent_id) > 1:
            return False, u'more than one item parent asset'
        return True, item_parent_id[0]


if __name__ == '__main__':
    # print sys.argv
    BatchSubmitVariantAssets().submit()
