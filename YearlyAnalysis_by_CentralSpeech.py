from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import os
import sys
import re

if len(sys.argv) < 4:
    print("Usage: python script.py [START_YEAR] [END_YEAR] [MAIN_KEYWORD] [OPTIONAL_KEYWORD]")
    sys.exit(1)

start_year = int(sys.argv[1])
end_year = int(sys.argv[2])
main_keyword = sys.argv[3]
optional_keyword = sys.argv[4] if len(sys.argv) > 4 else None  # 追加キーワード




# キーワード名でディレクトリを作成（出力用）
output_dir = ""
if optional_keyword:
    output_dir = f"{main_keyword}_{optional_keyword}_sorted"
else:
    output_dir = f"{main_keyword}_sorted"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# 各年ごとに処理
for year in range(start_year, end_year + 1):
    input_file_path = os.path.join(main_keyword, f"{year}.csv")
    output_file_path = os.path.join(output_dir, f"{year}_sorted.csv")

    if not os.path.exists(input_file_path):
        print(f"File {input_file_path} does not exist. Skipping...")
        continue

    # CSVファイルを読み込む
    df = pd.read_csv(input_file_path)

    # 追加キーワードが指定されている場合、そのキーワードを含むspeechだけを対象とする
    if optional_keyword:
        df = df[df['Speech'].str.contains(re.escape(optional_keyword), case=False, regex=True)]

    # 対策1: データが空でないか確認
    if df['Speech'].empty:
        print(f"No speeches found for the year {year}. Skipping...")
        continue

    try:
        # TF-IDFでテキストをベクトル化
        vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b|"+re.escape(main_keyword.lower())+"|"+re.escape(optional_keyword.lower()) if optional_keyword else "")
        tfidf_matrix = vectorizer.fit_transform(df['Speech'])

        # 対策1: キーワード存在チェック
        if main_keyword.lower() not in vectorizer.vocabulary_:
            print(f"Keyword '{main_keyword}' not found in the speeches for the year {year}. Skipping...")
            continue

        keyword_index = vectorizer.vocabulary_[main_keyword.lower()]
        keyword_tfidf_scores = tfidf_matrix[:, keyword_index].toarray()
        # スコアでソート
        df['Keyword_TFIDF_Score'] = keyword_tfidf_scores
        df_sorted = df.sort_values(by='Keyword_TFIDF_Score', ascending=False).head(50)
    
        # ソートされたデータをCSVに出力
        df_sorted.to_csv(output_file_path, index=False, columns=['Date', 'Speaker', 'SpeakerGroup', 'Speech'])


    except ValueError as e:
        # 対策3: エラーハンドリング
        print(f"An error occurred for the year {year}: {e}")
        continue


