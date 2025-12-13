# -*- coding: UTF-8 -*-
import pymel.core as pm
import json
import speak_tool
reload(speak_tool)
import read_textgrid
reload(read_textgrid)

json_filename = read_textgrid.json_filename
with open(json_filename, 'r') as f:
    textgrid_phones_data = json.load(f)

print read_textgrid.name

tongue_bs_list = [
    "tgUp",
    "tgDown",
    "tgBack",
    "tgFront"
]

R_ph = ('b', 'p', 'f', 'a', 'e')
A_ph = ('d', 't', 'n', 'l', 'z', 'c', 's')
B_ph = ('zh', 'ch', 'sh', 'r')
C_ph = ('i', 'ii', 'q', 'x', 'v')
D_ph = ('g', 'k', 'h', 'o', 'ng', 'u', 'j')
E_ph = ('m')

close_teeth_ph = ['z', 'c', 's', 'zh', 'ch', 'sh', 'r', 'j', 'q', 'x', 'i', 'ii']

single_ph = {R_ph: [0, 0, 0, 0], A_ph: [1, 0, 0, 1], B_ph: [1, 0, 1, 0],
             C_ph: [0, 1, 0, 1], D_ph: [0, 1, 1, 0], E_ph: [0, 0, 1, 0]}

two_transition = [0.5, 0.5]
three_transition = [0.3, 0.3, 0.4]

Mix_ph = dict(ai=[], ao=[], ei=[], ia=[], iao=[], ie=[], io=[], iou=[],
              iu=[], ua=[], uai=[], ue=[], uei=[], uo=[], ou=[], va=[], ve=[])

for mix in Mix_ph.keys():
    a = mix[0]
    for grp in single_ph.keys():
        if a in grp:
            Mix_ph[mix].append(single_ph[grp])
    b = mix[1]
    for grp in single_ph.keys():
        if b in grp:
            Mix_ph[mix].append(single_ph[grp])
    if len(mix) == 2:
        Mix_ph[mix].append(two_transition)
    elif len(mix) == 3:
        c = mix[2]
        for grp in single_ph.keys():
            if c in grp:
                Mix_ph[mix].append(single_ph[grp])
        Mix_ph[mix].append(three_transition)

# print Mix_ph

# Mix_ph = {'va': [[0, 1, 1, 0], [0, 0, 0, 0], [0.5, 0.5]], 'uei': [[0, 1, 1, 0], [0, 0, 0, 0], [0, 1, 0, 1], [0.3, 0.3, 0.4]],
#           've': [[0, 1, 1, 0], [0, 0, 0, 0], [0.5, 0.5]], 'ai': [[0, 0, 0, 0], [0, 1, 0, 1], [0.5, 0.5]],
#           'iou': [[0, 1, 0, 1], [0, 1, 1, 0], [0, 1, 1, 0], [0.3, 0.3, 0.4]], 'iu': [[0, 1, 0, 1], [0, 1, 1, 0], [0.5, 0.5]],
#           'ao': [[0, 0, 0, 0], [0, 1, 1, 0], [0.5, 0.5]], 'uai': [[0, 1, 1, 0], [0, 0, 0, 0], [0, 1, 0, 1], [0.3, 0.3, 0.4]],
#           'io': [[0, 1, 0, 1], [0, 1, 1, 0], [0.5, 0.5]], 'ia': [[0, 1, 0, 1], [0, 0, 0, 0], [0.5, 0.5]],
#           'ei': [[0, 0, 0, 0], [0, 1, 0, 1], [0.5, 0.5]], 'ie': [[0, 1, 0, 1], [0, 0, 0, 0], [0.5, 0.5]],
#           'iao': [[0, 1, 0, 1], [0, 0, 0, 0], [0, 1, 1, 0], [0.3, 0.3, 0.4]], 'uo': [[0, 1, 1, 0], [0, 1, 1, 0], [0.5, 0.5]],
#           'ue': [[0, 1, 1, 0], [0, 0, 0, 0], [0.5, 0.5]], 'ou': [[0, 1, 1, 0], [0, 1, 1, 0], [0.5, 0.5]],
#           'ua': [[0, 1, 1, 0], [0, 0, 0, 0], [0.5, 0.5]]}


def get_time_scale():
    time_scale = 1
    time_unit = pm.currentUnit(q=1, t=1)
    if time_unit == "ntsc":
        time_scale = 0.5
    elif time_unit == "ntscf":
        time_scale = 1
    return time_scale

def unity_to_maya_time(unity_time):
    maya_start_time = pm.playbackOptions(q=1, min=1)
    time_scale = get_time_scale()
    offset = - 1 * time_scale
    maya_time = maya_start_time + (unity_time * 60.0 * time_scale) + offset
    return maya_time

def get_ctrl():
    ctrl = pm.selected()[0]
    name = ctrl.name().split(":")[-1].split("|")[-1]
    if name != "speakControl":
        return pm.warning("please selected speakControl")
    for attr_name in tongue_bs_list:
        if not ctrl.hasAttr(attr_name):
            pm.addAttr(ln=attr_name, at='double', min=0, max=1, dv=0)
            pm.setAttr(ctrl + '.' + attr_name, e=1, keyable=1)
            pm.setAttr(ctrl + '.' + attr_name, 1)
    return ctrl

def get_interval():

    all_anim_data = []
    for i, phone in enumerate(textgrid_phones_data):
        text = phone[0]
        if text in Mix_ph.keys():
            for j in range(len(Mix_ph[text])-1):
                text_solo = phone[0][j]
                value = Mix_ph[text][j]
                if j == 0:
                    start = phone[1]
                    end = phone[1] + (phone[2]-phone[1]) * Mix_ph[text][-1][0]
                elif j == 1:
                    start = phone[1] + (phone[2]-phone[1]) * Mix_ph[text][-1][0]
                    end = phone[1] + (phone[2]-phone[1]) * (Mix_ph[text][-1][0]+Mix_ph[text][-1][1])
                else:
                    start = phone[1] + (phone[2]-phone[1]) * (Mix_ph[text][-1][0]+Mix_ph[text][-1][1])
                    end = phone[2]
                ifCloseTeeth = text_solo in close_teeth_ph
                anim_data_one = dict(text=text_solo, value=value, start=start, end=end, ifCloseTeeth=ifCloseTeeth)
                all_anim_data.append(anim_data_one)
        else:
            for grp in single_ph.keys():
                if text in grp:
                    value = single_ph[grp]
                    ifCloseTeeth = text in close_teeth_ph
                    anim_data = dict(text=text, value=value, start=phone[1], end=phone[2], ifCloseTeeth=ifCloseTeeth)
                    all_anim_data.append(anim_data)

    return all_anim_data

def get_intersection_point(x1,y1, x2,y2, x3,y3, x4,y4):
    x0 = ((x3 - x4) * (x2 * y1 - x1 * y2) - (x1 - x2) * (x4 * y3 - x3 * y4)) \
         / ((x3 - x4) * (y1 - y2) - (x1 - x2) * (y3 - y4))
    y0 = ((y3 - y4) * (y2 * x1 - y1 * x2) - (y1 - y2) * (y4 * x3 - y3 * x4)) \
         / ((y3 - y4) * (x1 - x2) - (y1 - y2) * (x3 - x4))
    return round(x0, 2), round(y0, 2)

def smooth_value(value, valley, rate):
    result = valley + rate * (value - valley)
    return result

def get_key_data(bs_list=None, peak=None, valley=None, preTime=0, midTime=0, postTime=0):
    time_scale = get_time_scale()
    key_list = []
    for i, data in enumerate(bs_list):
        st = round(unity_to_maya_time(data['start'])) + preTime * time_scale
        mt = round(unity_to_maya_time(data['start'])) + midTime * time_scale
        et = round(unity_to_maya_time(data['end'])) + postTime * time_scale
        if not i:
            key_list.append([int(st), valley, str(data['text']), 'Start'])
        else:
            last_data = list(enumerate(bs_list))[i - 1][1]
            last_mt = round(unity_to_maya_time(last_data['start'])) + midTime * time_scale
            last_et = round(unity_to_maya_time(last_data['end'])) + postTime * time_scale
            if st > last_et:
                key_list.append([int(st), valley, str(data['text']), 'Start'])
            elif st == last_et:
                pass
                # 去掉st
            else:
                if mt <= last_et:
                    key_list.pop(-1)
                    # 去掉last_et和st
                else:
                    key_list.pop(-1)
                    # 去掉last_et和st，增加一个相交点
                    t = get_intersection_point(last_mt, peak, last_et, valley, st, valley, mt, peak)[0]
                    v0 = get_intersection_point(last_mt, peak, last_et, valley, st, valley, mt, peak)[1]
                    # v = (v0 + peak)/2
                    v = smooth_value(v0, peak, 0.4)
                    # v = v0
                    key_list.append([t, v, data['text']])
        # key_list.append([int(st), valley, str(data['text']), 'Start'])
        key_list.append([int(mt), peak, str(data['text']), 'Middle'])
        key_list.append([int(et), valley, str(data['text']), 'End'])

    for i, data in enumerate(key_list):
        if i:
            if data[1] == peak:
                last_data = list(enumerate(key_list))[i - 1][1]
                next_data = list(enumerate(key_list))[i + 1][1]
                if next_data[1] == valley and last_data[1] == valley:
                    data[1] = smooth_value(peak, valley, 0.4)
                elif next_data[1] == peak:
                    next_next_data = list(enumerate(key_list))[i + 2][1]
                    if last_data[1] == valley and next_next_data[1] == valley:
                        data[1] = smooth_value(peak, valley, 0.7)
                        next_data[1] = smooth_value(peak, valley, 0.7)

    return key_list




# def key_teeth_bs():
#     bridge = pm.PyNode('SpeakBlendShapeBridge')
#     teeth_bs_list = ['tg_MouthStretch', 'tg_LowerLipDepressor']
#     if pm.objExists('FaceDriverBS'):
#         BS_node = pm.PyNode('FaceDriverBS')
#         for i, attr in enumerate(BS_node.listAliases()):
#             for name in teeth_bs_list:
#                 if attr[0] == name:
#                     if not pm.objExists(name + '_BW'):
#                         BW = pm.createNode('blendWeighted', n=name + '_BW')
#                         bridge.attr(name[3:]).connect(BW.input[0], f=1)
#                         BW.output.connect(attr[1], f=1)
#
#     teeth_data_list = [data for data in get_interval() if data['ifCloseTeeth']]
#     key_list = get_key_data(bs_list=teeth_data_list, peak=0.5, valley=0.8, preTime=-8, midTime=-2, postTime=0)
#     for BW in [pm.PyNode(name + '_BW') for name in teeth_bs_list]:
#         pm.cutKey(BW, time=":", clear=1, at='w[0]')
#         for data in key_list:
#             pm.setKeyframe(BW, attribute='w[0]', t=data[0], v=data[1])
#             print data

def key_teeth_bs():
    bridge = pm.PyNode('SpeakBlendShapeBridge')
    ctrl = get_ctrl()
    attr_list = ['tg_MouthStretch', 'MouthStretch', 'LowerLipDepressor']
    if pm.objExists('FaceDriverBS'):
        teeth_data_list = [data for data in get_interval() if data['ifCloseTeeth']]
        key_list = get_key_data(bs_list=teeth_data_list, peak=0.8, valley=0, preTime=-8, midTime=-2, postTime=0)
        pm.cutKey(ctrl, time=":", clear=1, at=attr_list[0])
        pm.cutKey(ctrl, time=":", clear=1, at='close_ph')
        for data in key_list:
            closePh_value = data[1]
            pm.setKeyframe(ctrl, attribute='close_ph', t=data[0], v=closePh_value)

        start = int(pm.playbackOptions(q=1, min=1))
        end = int(pm.playbackOptions(q=1, max=1))
        for time in range(start, end, 2):
            pm.currentTime(time)
            MouthStretch_value = pm.getAttr(bridge.attr(attr_list[1]))
            LowerLipDepressor_value = pm.getAttr(bridge.attr(attr_list[2]))
            closePh_value = pm.getAttr(ctrl.attr('close_ph'))
            value = (MouthStretch_value * 1 + LowerLipDepressor_value * 0.4) * (1 - closePh_value) + 0.12 * closePh_value
            pm.setKeyframe(ctrl, attribute=attr_list[0], t=time, v=value)

        # multi_1 = pm.createNode('multiplyDivide', n='tg_MouthStretch_multi_1')
        # add_1 = pm.createNode('plusMinusAverage', n='tg_MouthStretch_add')
        # pm.setAttr(add_1.operation, 1)
        # plus = pm.createNode('plusMinusAverage', n='tg_MouthStretch_plus')
        # pm.setAttr(plus.operation, 2)
        # multi_2 = pm.createNode('multiplyDivide', n='tg_MouthStretch_multi_2')
        # add_2 = pm.createNode('plusMinusAverage', n='tg_MouthStretch_add_2')
        # pm.setAttr(add_2.operation, 1)
        #
        # pm.setAttr(multi_1.input2X, 1.0)
        # bridge.attr(attr_list[1]).connect(multi_1.input1X)
        # multi_1.output.outputX.connect(add_1.input1D[0])
        # pm.setAttr(multi_1.input2Y, 0.4)
        # bridge.attr(attr_list[2]).connect(multi_1.input1Y)
        # multi_1.output.outputY.connect(add_1.input1D[1])
        # add_1.output1D.connect(multi_2.input1X)
        # pm.setAttr(plus.input1D[0], 1.0)
        # ctrl.attr('close_ph').connect(plus.input1D[1])
        # plus.output1D.connect(multi_2.input2X)
        # multi_2.output.outputX.connect(add_2.input1D[0])
        # pm.setAttr(multi_2.input1Y, 0.12)
        # ctrl.attr('close_ph').connect(multi_2.input2Y)
        # multi_2.output.outputY.connect(add_2.input1D[1])
        # add_2.output1D.connect(ctrl.attr(attr_list[0]))

def key_tongue_bs(given_attr=None):
    ctrl = get_ctrl()
    for i, attr in enumerate(tongue_bs_list):
        if given_attr:
            if attr == given_attr:
                pm.cutKey(ctrl, time=":", clear=1, at=attr)
                tongue_data_list = [data for data in get_interval() if data['value'][i]]
                key_list = get_key_data(bs_list=tongue_data_list, peak=0.8, valley=0, preTime=4)
                for data in key_list:
                    pm.setKeyframe(ctrl, attribute=attr, t=data[0], v=data[1])
                    print data
        else:
            pm.cutKey(ctrl, time=":", clear=1, at=attr)
            tongue_data_list = [data for data in get_interval() if data['value'][i]]
            key_list = get_key_data(bs_list=tongue_data_list, peak=0.8, valley=0, preTime=4)
            for data in key_list:
                pm.setKeyframe(ctrl, attribute=attr, t=data[0], v=data[1])
