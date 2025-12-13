import requests

url = 'http://10.10.133.39:8000/'
path = r'D:\kouxing\tongue\SpecialDate_ST_01_Excel_231.wav'
print(path)
files = {'file': open(path, 'rb')}
r = requests.post(url, files=files)
print(r.url)
print(type(r.text))
# with
# #
# import json
json_filename = r'D:\kouxing\tongue\SpecialDate_ST_01_Excel_231.json'
with open(json_filename, 'w') as f:
    f.write(r.text)
    # json_data = json.dump(r.text, f, indent=4)
#
