from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
import pandas as pd
import os
import sys
import MeCab


if len(sys.argv) < 4:
    print("Usage: python script.py [START_YEAR] [END_YEAR] [KEYWORD]")
    sys.exit(1)

# コマンドライン引数から西暦の年（開始と終了）とキーワードを取得
start_year = int(sys.argv[1])
end_year = int(sys.argv[2])
keyword = sys.argv[3]

# キーワード名でディレクトリを作成（出力用）
output_dir = f"{keyword}_sorted_v2"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# MeCabの初期化
mecab = MeCab.Tagger("-Owakati")

# 重要な単語を保存するためのリスト
important_words_list = []

stop_words = ["です", "ます", "こと", "それ", "として", "、",  "*", "。", "ます", "君", "（", "）", "的",  "こと", "それ", "ん", "一", "よう", "これ", "人", "私", "もの", "ある", "で", "に", "なり", "と", "な", "それから", "やる", "か", "た", "する", "やはり", "いわゆる", "それから", "が", "し", "そして", "まし", "まで", "つき", "この", "について", "だけ", "において", "それから", "やら", "なる", "でき", "どこ", "その", "そういう", "て", "い", "いま", "御", "等", "ところ", "という", "から", "ちょっと", "あるいは", "もう", "けれども", "おる", "を", "の", "れる", "いたし", "う", "は", "ぬ", "しかし", "でも", "れ", "だ", "そこ", "も", "へ", "たり", "さ", "も"]

# 各年ごとに処理
for year in range(start_year, end_year + 1):
    input_file_path = os.path.join(keyword, f"{year}.csv")
    output_file_path = os.path.join(output_dir, f"{year}_sorted.csv")

    # CSVファイルを読み込む
    df = pd.read_csv(input_file_path)

    # 対策1: データが空でないか確認
    if df['Speech'].empty:
        print(f"No speeches found for the year {year}. Skipping...")
        continue

    try:
        # 形態素解析を行い、スペースで単語を区切る
        df['Tokenized_Speech'] = df['Speech'].apply(lambda x: mecab.parse(x).strip())


        # TF-IDFでテキストをベクトル化
        vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split())
        #vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(df['Tokenized_Speech'])

        # 対策1: キーワード存在チェック
        if keyword.lower() not in vectorizer.vocabulary_:
            print(f"Keyword '{keyword}' not found in the speeches for the year {year}. Skipping...")
            continue

        keyword_index = vectorizer.vocabulary_[keyword.lower()]
        keyword_tfidf_scores = tfidf_matrix[:, keyword_index].toarray()
        # スコアでソート
        df['Keyword_TFIDF_Score'] = keyword_tfidf_scores
        df_sorted = df.sort_values(by='Keyword_TFIDF_Score', ascending=False).head(50)
    
        # ソートされたデータをCSVに出力
        df_sorted.to_csv(output_file_path, index=False, columns=['Date', 'Speaker', 'SpeakerGroup', 'SpeakerPosition', 'Speech'])

        # キーワード周辺の重要単語リスト
        #  形態素解析を行い、単語のリストを生成
        df['Tokenized_Speech_List'] = df['Speech'].apply(lambda x: mecab.parse(x).strip().split())
        # Word2Vecモデルの設定
        # sg=1 はSkip-gramを使用することを意味する
        # windowは予測に使用する周囲の単語数
        # min_countはモデルの訓練に使用する単語の最低出現回数
        word2vec_model = Word2Vec(sentences=df['Tokenized_Speech_List'], vector_size=100, window=5, min_count=1, sg=1)

        # 特定の単語（この例ではキーワード）に最も近い単語を表示
        similar_words = word2vec_model.wv.most_similar(keyword, topn=50)
        filtered_similar_words = [(word, score) for word, score in similar_words if word not in stop_words][:10]

        # 年と重要な単語をリストに追加
        words_with_scores = [f"{word}:{round(score, 2)}" for word, score in filtered_similar_words]
        important_words_list.append(f"{year}," + ", ".join(words_with_scores))

    except ValueError as e:
        # 対策3: エラーハンドリング
        print(f"An error occurred for the year {year}: {e}")
        continue


# CSVファイルに出力
output_file_path = os.path.join(output_dir, "important_words_by_year.csv")
with open(output_file_path, 'w') as f:
    for line in important_words_list:
        f.write(line + "\n")
