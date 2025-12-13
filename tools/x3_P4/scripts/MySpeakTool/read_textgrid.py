from tgt import read_textgrid

name = 'SpecialDate_ST_02_Excel_84'

filename = r'D:/kouxing/tongue/test_v03/%s.TextGrid' % name
json_filename = r'D:/kouxing/tongue/test_v03/%s.json' % name
textgrid = read_textgrid(filename)

# words and phones
tiers = textgrid.tiers
words = tiers[0]
phones = tiers[1]

# each words
words_interval_list = []
phones_interval_list = []


def remove_number(phone):
  if phone[-1].isdigit():
    return phone[:-1]
  return phone


def clean_list(list):
  return list(sorted(set(list)))


for interval in words.intervals:
  words_interval_list.append([remove_number(interval.text), interval.start_time, interval.end_time])
for interval in phones.intervals:
  phones_interval_list.append([remove_number(interval.text), interval.start_time, interval.end_time])

data = phones_interval_list
# for i in [ph[0] for ph in data]:
#   print i

import json
with open(json_filename, "w") as fp:
  json.dump(data, fp, indent=4)

# import sys
# print __file__
# print "args", sys.argv