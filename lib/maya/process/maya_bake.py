# -*- coding: utf-8 -*-#
# Python     : Python 2.7
# -------------------------------------------------------
# NAME       : maya_bake
# Describe   : bake
# version    : v0.01
# Author     : linhuan
# Email      : hanhong@papegames.net
# DateTime   : 2023/4/25__16:13
# -------------------------------------------------------
import maya.cmds as cmds


def bake(objlist, startframe, endframe, sim=1, samplby=1, discontrol=1, prekey=1, sparancurbake=0, removefromlayer=1,
         bakelayer=0,
         removebakeanilayer=0, minrotation=1, controlpoint=0, shape=1):
    u"""
    bake动画函数
    :param objlist:需要bake的物体列表(根据需要，可以是物体列表，也可以是物体+属性列表，例如：[obj01,obj02,obj03],['tree01.v','tree02.v']
    :param strtframe:起始帧（例如:101)
    :param endframe:结束帧（例如:105)
    :return:为True时，bake成功，为False,没有bake成功
    """
    # 执行bake命令
    if objlist and objlist != False:
        try:
            cmds.bakeResults(objlist, t=(startframe, endframe),
                             simulation=sim,
                             sampleBy=samplby,
                             disableImplicitControl=discontrol,
                             preserveOutsideKeys=prekey,
                             sparseAnimCurveBake=sparancurbake,
                             removeBakedAttributeFromLayer=removefromlayer,
                             bakeOnOverrideLayer=bakelayer,
                             removeBakedAnimFromLayer=removebakeanilayer,
                             minimizeRotation=minrotation,
                             controlPoints=controlpoint,
                             shape=shape)
            return True
        except:
            return False
    return False

# if __name__ == "__main__":
# 	objlist = ['pSphere1.visibility']  # 需要bake的物体或物体+属性列表
# 	startframe = 101  # 起始帧
# 	endframe = 105  # 结束帧
# 	# 执行bake命令
# 	bake(objlist, startframe, endframe)