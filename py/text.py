'''
    TextUtils: text related methods
    handles: stopwords, regex clean up, language detection, lemmatization (spacy), tokenization
    some methods are not currently used
'''
import re
import emoji
import os
from nltk.tokenize import word_tokenize
from .job import *
import fasttext
import numpy as np

class LangDetector(object):
    '''
    Uses FasText model to determine language of given text
    '''

    def __init__(self):
        self.model = fasttext.load_model( os.path.join(job.project_root, 'model/lid.176.bin'));

    def predict(self, text):
        wordcount = len(text.split())
        if wordcount > 2:
            res = self.model.predict(text.replace("\n",' '))
            self.lang = res[0][0].split('__')[-1]
            self.conf = res[1][0]
            self.predicted =  {'lang': res[0][0].split('__')[-1], 'conf': res[1][0] }
        else:
            self.predicted =  {'lang': '--', 'conf': 0 }
            self.lang = None
            self.conf = np.nan
        return self.predicted


class TextUtils(object):

    @classmethod
    def to_db(cls,text,lr = False):
        if text is None:
            text = ''
        text = str(text)
        text = text.replace("$","<dlr>")
        if lr:
            text = text.replace("\n"," ")
            text = text.replace("\r"," ")
        return text

    @classmethod
    def extract_topic_categories(cls,topics):
        '''
        used extract topic from wikipedia link in video topic_categories
        '''
        if type(topics) == list:
            return [t.split('/')[-1] for t in topics]
        else:
            return ''

    @classmethod
    def stopwords_rgx(cls,):
        f = open( os.path.join(job.project_root, 'files', 'stopwords_fr_00.txt'), 'r')
        stopwords = f.readlines()
        f.close()
        stopwords = [re.sub("[\r\n]+",'', t) for t in stopwords]
        return  re.compile(r'\b(' + r'|'.join(stopwords) + r')\b\s*', flags=re.IGNORECASE)

    @classmethod
    def lemmatize(cls,spacy_doc):
        lemmas = [token.lemma_  for token in spacy_doc]
        return ' '.join( lemmas )


class Refine(object):
    @classmethod
    def remove_emoji(cls, text):
        allchars = [str for str in text]
        emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
        clean_text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
        return clean_text

    Regex = {
        'html': {'regex': "<[^>]*>", 'sub_by': ' '},
        'linereturns': {'regex': "[\r\n]+", 'sub_by': ' '},
        'urls': {'regex': "http\S+", 'sub_by': ' --url-- '},
        'urlswww': {'regex': "www\S+", 'sub_by': ' --url-- '},
        'ats': {'regex': "@\S+", 'sub_by': ' '},
        'latex': {'regex': "\$[^>]*\$", 'sub_by': ' '},
        'brackets': {'regex': "\[\S+\]", 'sub_by': ' '},
        'digits': {'regex': "\d+", 'sub_by': ' '},
        'xao': {'regex': "\xa0|►|–", 'sub_by': ' '},
        'punctuation': {'regex': re.compile(f"[{re.escape('▬∞!.[]?#$%&()+►’*+/•:;<=>@[]^_`{|}~”“→→_,')}]"), 'sub_by': ' '},
        'multiple_spaces': {'regex': "\s\s+", 'sub_by': ' '},
    }

    def __init__(self, text, recipe = None):
        self.original = text
        if recipe is not None:
            for item in recipe:
                if item in Refine.Regex.keys():
                    text = re.sub(Refine.Regex[item]['regex'],Refine.Regex[item]['sub_by'], text)
                if item == 'remove_emoji':
                    text = Refine.remove_emoji(text)
                if item == 'people':
                    text = gengo.people_regex.sub(lambda match: gengo.people[match.group(0)], text)

            text = re.sub(Refine.Regex['multiple_spaces']['regex'],Refine.Regex['multiple_spaces']['sub_by'], text)
            text = text.strip()
        self.text = text

        self.tokenize()
        self.capitalize()

    def tokenize(self):
        self.tokens = word_tokenize(self.text)

    def capitalize(self):
        if self.text.isupper():
            captk = []
            for tk in self.tokens:
                captk.append(tk.lower())
            self.capitalized = ' '.join(captk).capitalize()
        else:
            self.capitalized = self.text

    def __repr__(self):
        return f"<Refine \n original: \t{self.original}\n text: \t{self.text} \n tokens: \t {self.tokens} \n capitalized: \t {self.capitalized}  >"






# --------
