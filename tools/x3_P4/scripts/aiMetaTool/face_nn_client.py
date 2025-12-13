# coding=utf-8
try:
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection
import os
import numpy as np
import io


def file_client(host, port, data):
    connection = HTTPConnection(host, port)
    headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(len(data))
    }
    connection.request('POST', '', body=data, headers=headers)
    response = connection.getresponse()
    if response.status == 200:
        result_data = response.read()
    else:
        return
    connection.close()
    return result_data


def get_comb_data(data_dir):
    datas = []
    ctrl_attrs = set()
    for name in os.listdir(data_dir):
        if not name.endswith(".npz"):
            continue
        data_path = os.path.join(data_dir, name).replace("\\", "/")
        data = np.load(data_path)
        datas.append(data)
        ctrl_attrs.update(data["ctrl_attrs"])
    ctrl_attrs = sorted(ctrl_attrs)
    target_attrs = datas[0]["target_attrs"]
    target_values = np.concatenate([data["target_values"] for data in datas], axis=0)
    scale_ids = []
    for i, attr in enumerate(ctrl_attrs):
        if attr.split(".")[-1] in ["sx", "sy", "sz"]:
            scale_ids.append(i)
    ctrl_values = []
    for data in datas:
        old_values = data["ctrl_values"]
        new_values = np.zeros([len(old_values), len(ctrl_attrs)], dtype=np.float32)
        new_values[:, scale_ids] = 1
        indexes = [ctrl_attrs.index(attr) for attr in data["ctrl_attrs"]]
        new_values[:, indexes] = old_values
        ctrl_values.append(new_values)
    ctrl_values = np.concatenate(ctrl_values, axis=0)
    target_attrs = np.array(target_attrs, dtype="U")
    ctrl_attrs = np.array(ctrl_attrs, dtype="U")
    return dict(
        target_attrs=target_attrs,
        ctrl_attrs=ctrl_attrs,
        target_values=target_values,
        ctrl_values=ctrl_values)


def seed_to_server_tran(data_dir, url='10.10.133.157:8081'):
    if url.count(":") != 1:
        return
    host, prot = url.split(":")
    prot = int(prot)
    comb_data = get_comb_data(data_dir)
    comb_data_dir = os.path.join(data_dir, "result")
    if not os.path.isdir(comb_data_dir):
        os.makedirs(comb_data_dir)
    nn_path = os.path.join(comb_data_dir, "ai_result_nn.npz")
    data_io = io.BytesIO()
    np.savez(data_io, **comb_data)
    data_io.seek(0)
    with open(nn_path, "wb") as fp:
        fp.write(file_client(host, prot, data_io.getvalue()))


if __name__ == '__main__':
    seed_to_server_tran(r"D:/work/AI_mh/x6/x6_nikki_ai_data/npz")
