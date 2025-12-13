from maya import cmds
import json

def key_bs():
    bs = "Head_Comb_Geo2_bs"
    names = ['anger', 'confused', 'sad', 'smile', 'surprise']
    for i in range(len(names)):
        cmds.setKeyframe(f"{bs}.{names[i]}", t=i*30, v=0)
        cmds.setKeyframe(f"{bs}.{names[i]}", t=i*30+30, v=0)
        cmds.setKeyframe(f"{bs}.{names[i]}", t=i * 30 + 20, v=1)

def export_bs_data():
    data = []
    for i in range(0, 150+1):
        cmds.currentTime(i)
        row = {}
        bs = "Head_Comb_Geo2_bs"
        names = ['anger', 'confused', 'sad', 'smile', 'surprise']
        for name in names:
            row[name] = cmds.getAttr(f"{bs}.{name}")
        data.append(row)
    path = "D:/work/x3_ai_face/st_faces/base_face_anim.json"
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def doit():
    export_bs_data()