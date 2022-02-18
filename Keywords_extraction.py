#KEYWORDS EXTRACTION

from keybert import KeyBERT
kw_model = KeyBERT()
import tqdm # FOR TIMING


for i in tqdm.tqdm(range(len(df["text"]))):
    g_tweets.loc[i,"keywords"]=kw_model.extract_keywords(g_tweets.loc[i,"text"], keyphrase_ngram_range=(1, 1), stop_words=None)[0][0]
    