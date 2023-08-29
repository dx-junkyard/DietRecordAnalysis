import mysql.connector
import csv
import sys
from collections import defaultdict
from datetime import datetime

def current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if len(sys.argv) < 4:
    print("Usage: python script.py [START_YEAR] [END_YEAR] [KEYWORD]")
    sys.exit(1)

# コマンドライン引数から西暦の開始年、終了年、とキーワードを取得
start_year = int(sys.argv[1])
end_year = int(sys.argv[2])
keyword = sys.argv[3]

# データベース接続設定
config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'dietrecord',
    'password': 'dietrecord',
    'database': 'dietrecorddb'
}

# キーワード出現数を年ごとにカウントする辞書
keyword_count_by_year = defaultdict(int)

print(f"{current_timestamp()} - 処理を開始します。")


# データベースに接続
connection = mysql.connector.connect(**config)

try:
    cursor = connection.cursor()
    # SQLクエリを実行
    sql = """
    SELECT 
        YEAR(MeetingRecords.date) as year, 
        SpeechRecords.speech
    FROM 
        MeetingRecords 
    JOIN 
        SpeechRecords ON MeetingRecords.id = SpeechRecords.meeting_id 
    WHERE 
        YEAR(MeetingRecords.date) BETWEEN %s AND %s;
    """
    cursor.execute(sql, (start_year, end_year))
    
    for row in cursor.fetchall():
        year = row[0]
        speech = row[1]
        
        keyword_count = speech.lower().count(keyword.lower())
        keyword_count_by_year[year] += keyword_count

    for year, count in sorted(keyword_count_by_year.items()):
        print(f"{current_timestamp()} - 年: {year}, キーワード検出数: {count}")


    # CSVファイルに出力
    with open('keyword_count_by_year.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Year', 'Keyword Count'])
        
        for year, count in sorted(keyword_count_by_year.items()):
            csvwriter.writerow([year, count])
                
finally:
    cursor.close()
    connection.close()

print(f"{current_timestamp()} - 処理を終了します。")
