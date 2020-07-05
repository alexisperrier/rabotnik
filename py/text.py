'''
    TextUtils: text related methods
'''

class TextUtils(object):
    @classmethod
    def valid_string_db(cls,string):
        if string is None:
            string = ''
        string = str(string)
        string = string.replace("$","#")
        string = string.replace("\n"," ")
        string = string.replace("\r"," ")
        return string

    def extract_topic_categories(topics):
        '''
        used extract topic from wikipedai link in video topic_categories
        '''
        if type(topics) == list:
            return [t.split('/')[-1] for t in topics]
        else:
            return ''
