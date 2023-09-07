from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import os
import sys
import MeCab

if len(sys.argv) < 5:
    print("Usage: python script.py [START_YEAR] [END_YEAR] [KEYWORD] [SPEAKER_POSITIONS]")
    sys.exit(1)

# コマンドライン引数から西暦の年（開始と終了）、キーワード、SpeakerPositionキーワードを取得
start_year = int(sys.argv[1])
end_year = int(sys.argv[2])
keyword = sys.argv[3]
speaker_positions = sys.argv[4].split(',')  # カンマで区切られた文字列をリストに変換


# キーワード名でディレクトリを作成（出力用）
output_dir = f"{keyword}_sorted"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# ストップワードのリストを定義
stop_words = ['です', 'ます', 'こと', 'それ', 'として', 'の', 'て', 'に', 'なつ', 'で', '、', '。']

# MeCabの初期化
mecab = MeCab.Tagger("-Owakati")

# MeCabの初期化（固有名詞抽出用）
mecab_chasen = MeCab.Tagger("-Ochasen")

# 固有名詞だけを抽出する関数
def extract_proper_nouns(text):
    nodes = mecab_chasen.parse(text).split("\n")
    proper_nouns = []
    for node in nodes[:-2]:
        surface, feature = node.split("\t")[0], node.split("\t")[3]
        if "名詞" in feature and "固有名詞" in feature:
            proper_nouns.append(surface)
    return " ".join(proper_nouns)


# 重要な単語を保存するためのリスト
important_words_list = []


# 各年ごとに処理
for year in range(start_year, end_year + 1):
    input_file_path = os.path.join(keyword, f"{year}.csv")
    output_file_path = os.path.join(output_dir, f"{year}_sorted.csv")

    # CSVファイルを読み込む
    df = pd.read_csv(input_file_path)

    # SpeakerPositionでフィルタリング
    # NaNやNoneを除去
    df = df.dropna(subset=['SpeakerPosition'])

    # SpeakerPositionでフィルタリング
    df = df[df['SpeakerPosition'].apply(lambda x: any(pos in x for pos in speaker_positions))]

    if 'Speech' not in df.columns:
        print(f"The 'Speech' column was not found in the DataFrame for the year {year}. Skipping...")
        continue

    # 対策1: データが空でないか確認
    if df['Speech'].empty:
        print(f"No speeches found for the year {year}. Skipping...")
        continue
        
    try:
        # 形態素解析を行い、スペースで単語を区切る
        df['Tokenized_Speech'] = df['Speech'].apply(lambda x: mecab.parse(x).strip())

        # DataFrameに固有名詞だけを含む新しい列を追加
        #df['ProperNouns'] = df['Speech'].apply(extract_proper_nouns)


        # TF-IDFでテキストをベクトル化
        vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split(), ngram_range=(1, 3))
        tfidf_matrix = vectorizer.fit_transform(df['Tokenized_Speech'])

        # TF-IDFでテキストをベクトル化（ProperNouns列を使用）
        #vectorizer = TfidfVectorizer()
        #tfidf_matrix = vectorizer.fit_transform(df['ProperNouns'])


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


        # TF-IDFスコアが高い単語を抽出
        #feature_names = vectorizer.get_feature_names_out()
        #tfidf_sorting = tfidf_matrix.sum(axis=0).A1.argsort()[::-1]
        #top_n = 300  # 上位300単語を取得
        #top_features = [feature_names[i] for i in tfidf_sorting[:top_n]]
        # 
        # 年と重要な単語をリストに追加
        #important_words_list.append(f"{year}," + ",".join(top_features))

        # 形態素解析して固有名詞とそのTF-IDFスコアを取得
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.sum(axis=0).A1
        proper_nouns = {}
    
        for i, feature in enumerate(feature_names):
            node = mecab.parseToNode(feature)
            while node:
                if node.feature.split(",")[0] == "名詞" and node.feature.split(",")[1] == "固有名詞" and len(node.surface) >= 2:
                    proper_nouns[feature] = tfidf_scores[i]
                node = node.next
    
        # TF-IDFスコアが高い単語を抽出
        sorted_proper_nouns = sorted(proper_nouns.items(), key=lambda x: x[1], reverse=True)
        top_n = 50  # 上位10単語を取得
        top_features = [word for word, score in sorted_proper_nouns[:top_n]]
    
        # 年と重要な単語をリストに追加
        important_words_list.append(f"{year}," + ",".join(top_features))
        


    except ValueError as e:
        # 対策3: エラーハンドリング
        print(f"An error occurred for the year {year}: {e}")
        continue


# CSVファイルに出力
output_file_path = os.path.join(output_dir, "important_words_by_year.csv")
with open(output_file_path, 'w') as f:
    for line in important_words_list:
        f.write(line + "\n")


