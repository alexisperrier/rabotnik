'''
A Job instance holds
- database connection object
- API key
- config (see config_rabotnik_sample.json )
- localized paths with respect to project root

And offers
- job.reconnect(): reconnects to the db
- job.execute(sql_query): wrapper around db.execute
'''

import os, json
import distutils.util
from .db import *
from .api import *
from pathlib import Path

class Job(object):

    config_file_path = './config/config_rabotnik_local.json'

    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__),'..', Job.config_file_path  )
        with open(config_path) as f:
            config = json.load(f)

        self.project_root   = config['project_root_path']
        self.tmp_folder     = os.path.join(self.project_root, 'tmp')
        self.reco_folder    = os.path.join(self.project_root, 'reco')
        self.img_folder     = os.path.join(self.project_root, 'img')

        self.forced_flow = False
        if 'forced_flow' in config.keys():
            self.forced_flow = bool(distutils.util.strtobool(config['forced_flow']))

        self.channel_growth = bool(distutils.util.strtobool(config['channel_growth']))
        self.plotshow   = bool(distutils.util.strtobool(config['plotshow']))
        self.verbose    = bool(distutils.util.strtobool(config['job_verbose']))
        self.db         = DbUtils(config)
        self.apikey     = APIkey(self).apikey
        self.config     = config

    def reconnect(self):
        print("=="*5, "reconnecting ")
        self.db         = DbUtils(self.config)

    def execute(self, sql):
        if self.db.conn.closed == 1:
            self.db  = DbUtils(self.config)

        try:
            self.db.execute(sql)
        except Exception as e:
            print('-- FAILED', sql)
            raise e

        if self.verbose:
            print("--"* 4)
            print(sql)
            print("== rowcount", self.db.cur.rowcount)

    def __repr__(self):
        return f'''
            - channel_growth {self.channel_growth}
            - project_root:\t {self.project_root}
            - plotshow:\t {self.plotshow}
            - len(apikey):\t {len(self.apikey)}
            - db:\t {self.db}
        '''

try:
    print(type(job.db))
except:
    job = Job()

# ---------
