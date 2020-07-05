'''
DbUtils: connection to db
'''
import psycopg2
import os
import sys
import json

class DbUtils(object):
    '''
        Loads parameters and opens connections to the database
    '''

    def __init__(self, config):
        self.pwd = None
        if os.path.exists(f"{config['db']['credentials_path']}"):
            with open(f"{config['db']['credentials_path']}", 'r') as f:
                self.pwd = f.read().replace('\n','')
        elif config['db']['envar_credentials'] in os.environ.keys():
            self.pwd = os.environ[config['db']['envar_credentials']]

        if self.pwd:
            self.conn, self.cur = self.connect(config)
        else:
            self.conn, self.cur = None, None

    def connect(self,config):
        '''
            Connects to the database
        '''
        try:
            dns = f'''
                dbname={config['db']['dbname']}
                user={config['db']['user']}
                host={config['db']['host']}
                password={self.pwd}
                port={config['db']['port']}
            '''
            conn = psycopg2.connect(dns)
            cur  = conn.cursor()

        except BaseException as e:
            # TODO Alert
            error_message = f"Unable to connect \n{str(e)}"
            sys.exit(error_message)

        return conn, cur

    def table_columns(self, table_name):
        '''
            returns columns & type of table_name
        '''
        sql = f'''SELECT column_name,udt_name FROM information_schema.columns where table_name  = '{table_name}'; '''
        self.cur.execute(sql)
        columns = {dbres[0]:dbres[1] for  dbres in self.cur.fetchall() if dbres[0] != 'id'}
        return columns

    def count(self, table_name):
        '''
        Counts rows in table
        '''
        sql = "select count(*) from {}; ".format(table_name)
        self.cur.execute(sql)
        return self.cur.fetchone()[0]

    def close(self):
        '''
            Close connections to the local database
        '''
        self.cur.close()
        self.conn.close()

    def execute(self, sql):
        '''
            Runs sql query
        '''
        self.cur.execute(sql)
        self.conn.commit()

    def __repr__(self):
        open_flag = getattr(self,'conn').closed == 0
        return f'''open: {open_flag}
            {getattr(self,'conn')}
            {getattr(self,'cur')}
        '''




# -----------
