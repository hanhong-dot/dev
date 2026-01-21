# -*- coding: utf-8 -*-
# author: linhuan
# file: load_hair_normal_tool.py
# time: 2026/1/21 20:55
# description:

import hair_normal_line_adjuster_tool.ui
import hair_normal_line_adjuster_tool.functions

reload(hair_normal_line_adjuster_tool.ui)
reload(hair_normal_line_adjuster_tool.functions)


def show_hair_normal_tool():
    hair_normal_line_adjuster_tool.ui.show()
