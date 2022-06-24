import pandas as pd
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import TweetTokenizer
from gensim.corpora import Dictionary
from gensim.models.ldamulticore import LdaMulticore
from wordcloud import STOPWORDS
from gensim.parsing.preprocessing import STOPWORDS as SW
from collections import Counter
import emoji
import re
from nltk.stem import WordNetLemmatizer
stop_words = ['hi','\n','\n\n', '&amp;', ' ', '.', '-', 'got', "it's", 'it’s', "i'm", 'i’m', 'im', 'want', 'like', '$', '@','yall']
stop_words += list(STOPWORDS)
stop_words += list(SW)
stop_words += stopwords.words('english')
#add punctuation char's to stopwords list
stop_words += list(string.punctuation) # <-- contains !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
#add integers
stop_words += ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
# print(stop_words)

class TopicModelling:
    def __init__(self,data):
        if not (isinstance(data, pd.DataFrame)):
            data = pd.DataFrame(data)
        self.df = data
    #clean
    def clean(self,text):
        emoji_list = [c for c in text if c in emoji.UNICODE_EMOJI]                
        clean_text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])       # remove emoji
        text = re.sub(r'http\S+', '', clean_text)   # remove url
        no_nums = re.sub('[^a-zA-Z ]','', text)          # remove noise
        return no_nums
    
    #tokens
    def tokenize_lowercase(self,text):
        tokens = word_tokenize(text)
        #tokens = TweetTokenizer().tokenize(text)
        stopwords_removed = [token.lower() for token in tokens if token.lower() not in stop_words]
        return stopwords_removed

    #lemmatized
    def lemmatize_text(self,df_text):
        lemmatized =[]
        for w in df_text:
            lemmatized.append(WordNetLemmatizer().lemmatize(w))
        return lemmatized
    
    def getTopics(self):
        self.df['text'] = self.df['text'].apply(self.clean)
        self.df['token']= self.df['text'].apply(self.tokenize_lowercase)
        self.df['lemmas_tokens'] =  self.df['token'].apply(self.lemmatize_text)
        self.df['lemmas_back_to_text'] = [' '.join(map(str, l)) for l in  self.df['lemmas_tokens']]

        id2word = Dictionary(self.df['lemmas_tokens'])
        print(len(id2word))
        # id2word.filter_extremes(no_below=2)
        print(len(id2word))
        if len(id2word) == 0:
            return None
        corpus = [id2word.doc2bow(d) for d in  self.df['lemmas_tokens']]
        base_model = LdaMulticore(corpus=corpus, num_topics=10,random_state=1, id2word=id2word, passes=20)
        words = [re.findall(r'"([^"]*)"',t[1]) for t in base_model.print_topics()]
        # topics = [' '.join(t) for t in words]
        Topics = Counter()
        for x in words:
            Topics += Counter(x)
        Topics = dict(Topics)
        
        TopicsDic = [{'text':x,'value':v} for (x,v) in Topics.items()]
        # max(Topics,key=Topics.get)
        # len(Topics)
        return TopicsDic
