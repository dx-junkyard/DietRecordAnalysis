from sklearn.feature_extraction.text import CountVectorizer
from gensim import corpora, models
import pandas as pd
import os
import sys
import MeCab

if len(sys.argv) < 4:
    print("Usage: python script.py [START_YEAR] [END_YEAR] [KEYWORD]")
    sys.exit(1)

# コマンドライン引数から西暦の年（開始と終了）を取得
start_year = int(sys.argv[1])
end_year = int(sys.argv[2])
keyword = sys.argv[3]

# キーワード名でディレクトリを作成（出力用）
output_dir = f"{keyword}_lda"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# MeCabの初期化
mecab = MeCab.Tagger("-Owakati")

# ストップワードのリスト（ここは充実させていく）
#stop_words = ["、", "の", "は", "て", "で", "を", "が", "*", "。", "ます", "君", "（", "）", "的", "者", "こと", "それ", "ん", "一", "よう", "これ", "人", "私", "もの", "つて"]
stop_words = ["、",  "*", "。", "ます", "君", "（", "）", "的",  "こと", "それ", "ん", "一", "よう", "これ", "人", "私", "もの"]

# 形態素解析を行い、名詞として抽出された単語をスペースで区切る
def extract_nouns(text):
    nodes = MeCab.Tagger().parse(text).split("\n")
    nouns = []
    for node in nodes[:-2]:
        word, feature = node.split("\t")[0], node.split("\t")[1]
        if "名詞" in feature:
            nouns.append(word)
    return " ".join(nouns)


# 各年ごとに処理
for year in range(start_year, end_year + 1):
    input_file_path = os.path.join(keyword,f"{year}.csv")
    output_file_path = os.path.join(output_dir,f"{year}_lda_topics.txt")

    # CSVファイルを読み込む
    df = pd.read_csv(input_file_path)

    if 'Speech' not in df.columns:
        print(f"The 'Speech' column was not found in the DataFrame for the year {year}. Skipping...")
        continue

    # 形態素解析を行い、スペースで単語を区切る
    #df['Tokenized_Speech'] = df['Speech'].apply(lambda x: mecab.parse(x).strip())

    # 形態素解析を行い、名詞だけを抽出
    df['Nouns'] = df['Speech'].apply(extract_nouns)

    try:
        # CountVectorizerを使って文書-単語行列を作成
        #vectorizer = CountVectorizer(tokenizer=lambda x: x.split())
        #count_matrix = vectorizer.fit_transform(df['Tokenized_Speech'])
        # CountVectorizerを使って文書-単語行列を作成（ストップワードを除去）
        vectorizer = CountVectorizer(tokenizer=lambda x: x.split(), stop_words=stop_words, ngram_range=(1, 3))
        count_matrix = vectorizer.fit_transform(df['Nouns'])
    
        # gensim用の辞書とコーパスを作成
        #gensim_dict = corpora.Dictionary(df['Tokenized_Speech'].apply(lambda x: x.split()))
        gensim_dict = corpora.Dictionary(df['Nouns'].apply(lambda x: x.split()))
        #corpus = [gensim_dict.doc2bow(text.split()) for text in df['Tokenized_Speech']]
        corpus = [gensim_dict.doc2bow(text.split()) for text in df['Nouns']]
    
        # LDAモデルの設定と学習
        lda_model = models.ldamodel.LdaModel(corpus=corpus, num_topics=10, id2word=gensim_dict, passes=15)
    
        # 各トピックの単語とその重みを出力
        topics = lda_model.print_topics(num_words=5)
        with open(output_file_path, 'w') as f:
            for topic in topics:
                f.write(str(topic) + "\n")
    
        print(f"Topics for the year {year} have been saved to {output_file_path}.")
    except ValueError as e:
        print(f"An error occurred for the year {year}: {e}")
        print("The DataFrame rows causing the issue are:")
        #print(df[df['Tokenized_Speech'].apply(lambda x: len(x.strip()) == 0)])
        print(df[df['Nouns'].apply(lambda x: len(x.strip()) == 0)])
        continue
