import UnityPy
from UnityPy import AssetsManager
import json
import os

def parse_binary_anim_unitypy(anim_path):
    """使用 UnityPy 解析二进制 .anim 文件"""

    am = AssetsManager(anim_path)

    anim_clips = []
    anim_data = {}
    for obj in am.objects:
        if obj.type.name == "AnimationClip":
            data = obj.read()
            fc = data.m_FloatCurves
            for float_curve in  data.m_FloatCurves:
                attribute = float_curve.attribute
                # print(dir(float_curve.curve.m_curve))
                tvs = float_curve.curve.m_Curve
                ts, vs = [], []
                for tv in tvs:
                    time = tv.time
                    value = tv.value
                    ts.append(time)
                    vs.append(value)
                bs_name = attribute.split(".")[-1]
                anim_data[bs_name] = dict(times=ts, values=vs)
    st = min([min(curve["times"]) for curve in anim_data.values()])
    et = max([max(curve["times"]) for curve in anim_data.values()])

    st = int(round(st*30))
    et = int(round(et*30))
    for name in anim_data.keys():
        ts = anim_data[name]["times"]
        vs = anim_data[name]["values"]
        new_ts, new_vs = [], []
        for i in range(st, et+1):
            t = i / 30
            if t <= ts[0]:
                v = vs[0]
            elif t >= ts[-1]:
                v = vs[-1]
            elif t in ts:
                idx = ts.index(t)
                v = vs[idx]
            else:
                # 插值
                for j in range(len(ts)-1):
                    if ts[j] <= t <= ts[j+1]:
                        t0, t1 = ts[j], ts[j+1]
                        v0, v1 = vs[j], vs[j+1]
                        v = v0 + (v1 - v0) * (t - t0) / (t1 - t0)
                        break
            new_vs.append(v/100)
        anim_data[name]["values"] = new_vs
    result_data = []
    for i in range(st, et+1):
        frame_data = {}
        for name in anim_data.keys():
            frame_data[name] = anim_data[name]["values"][i - st]
        result_data.append(frame_data)
    json_path = os.path.splitext(anim_path)[0]+".json"
    with open(json_path, "w") as f:
        json.dump(result_data, f, indent=4, ensure_ascii=False)






path = r"D:/work/AI_mh/load_x3_unity_anim/11-17-16-49_Cha_ST_Daily_01_faceBS.anim"

anim_data = parse_binary_anim_unitypy(path)
print(json.dumps(anim_data, indent=2, ensure_ascii=False))