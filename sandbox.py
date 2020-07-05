
# NEXT
# -- translate channel_stat into ChannelStat and instantiate class name
# -- test on 50 channels

import numpy as np
import pandas as pd
import os
import re
import json
import requests
import argparse
import datetime

from py import *


if __name__ == '__main__':
    flowname = 'video_stats'
    classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))

    klass = globals()[classname]
    print(klass)
    op = klass(flowtag = False, mode = 'local', counting = True)
    print(op)


# ----
