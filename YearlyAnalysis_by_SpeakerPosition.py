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


# MeCabの初期化
mecab = MeCab.Tagger("-Owakati")

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

    # 対策1: データが空でないか確認
    if df['Speech'].empty:
        print(f"No speeches found for the year {year}. Skipping...")
        continue

    try:
        # 形態素解析を行い、スペースで単語を区切る
        df['Tokenized_Speech'] = df['Speech'].apply(lambda x: mecab.parse(x).strip())
#        df['Speech'] = df['Speech'].apply(lambda x: mecab.parse(x).strip())


        # TF-IDFでテキストをベクトル化
        vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split())
        #vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(df['Tokenized_Speech'])

        # 対策1: キーワード存在チェック
        if keyword.lower() not in vectorizer.vocabulary_:
            print(f"Keyword '{keyword}' not found in the speeches for the year {year}. Skipping...")
#            print(f"token pattern '{vectorizer.vocabulary_}'")
            continue

        keyword_index = vectorizer.vocabulary_[keyword.lower()]
        keyword_tfidf_scores = tfidf_matrix[:, keyword_index].toarray()
        # スコアでソート
        df['Keyword_TFIDF_Score'] = keyword_tfidf_scores
        df_sorted = df.sort_values(by='Keyword_TFIDF_Score', ascending=False).head(50)
    
        # ソートされたデータをCSVに出力
        df_sorted.to_csv(output_file_path, index=False, columns=['Date', 'Speaker', 'SpeakerGroup', 'SpeakerPosition', 'Speech'])


    except ValueError as e:
        # 対策3: エラーハンドリング
        print(f"An error occurred for the year {year}: {e}")
        continue


