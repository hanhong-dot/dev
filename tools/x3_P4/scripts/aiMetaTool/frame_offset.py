import json

def load_iphone_data2(path):
    lines = open(path).readlines()
    anim_data = []
    frame_lines = []
    for line in lines:
        if "{" in line:
            frame_lines = []
        frame_lines.append(line)
        if "}" not in line:
            continue
        frame_lines[-1] = "}"
        frame = "".join(frame_lines)
        frame_data = json.loads(frame)
        anim_data.append(frame_data)
    return anim_data


def get_frame_offset(take_path, anim_path):
    anim_data = load_iphone_data2(anim_path)
    take_data = json.load(open(take_path))
    FrameNumber = anim_data[0]["FrameNumber"]
    SubFrame = anim_data[0]["SubFrame"]
    timescale = take_data["startTimestamp"]["timescale"]
    value = take_data["startTimestamp"]["value"]
    print("Frame Number:", FrameNumber)
    print("SubFrame:", SubFrame)
    print("timescale:", timescale)
    print("value:", value)
    frame_offset = (FrameNumber + SubFrame) - value/timescale*30.0
    frame_offset = int(round(frame_offset))
    print("frame_offset:", frame_offset)
    return frame_offset



def doit():
    take_path = r"D:\work\AI_mh\LS0200_SC009_0CD_004_LiTing\take.json"
    anim_path = r"D:\work\AI_mh\LS0200_SC009_0CD_004_LiTing\LS0200_SC009_0CD_004_LiTing.json"
    get_frame_offset(take_path, anim_path)

if __name__ == '__main__':
    doit()