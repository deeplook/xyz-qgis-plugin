# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2020 HERE Europe B.V.
#
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
#
###############################################################################

class LoadingMode(list):
    LIVE = "live"
    INCREMENTAL = "incremental"
    SINGLE = "single"
    def __init__(self):
        super().__init__([self.LIVE, self.INCREMENTAL, self.SINGLE])

LOADING_MODES = LoadingMode() # live, incremental, single