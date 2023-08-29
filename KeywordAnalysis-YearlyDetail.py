import mysql.connector
import csv
import sys

if len(sys.argv) < 3:
    print("Usage: python script.py [YEAR] [KEYWORD]")
    sys.exit(1)

# コマンドライン引数から西暦の年とキーワードを取得
year = int(sys.argv[1])
keyword = sys.argv[2]

# データベース接続設定
config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'dietrecord',
    'password': 'dietrecord',
    'database': 'dietrecorddb'
}

# データベースに接続
connection = mysql.connector.connect(**config)

try:
    cursor = connection.cursor()
    # SQLクエリを実行
    sql = """
    SELECT 
        MeetingRecords.date, 
        SpeechRecords.speech, 
        MeetingRecords.meetingURL 
    FROM 
        MeetingRecords 
    JOIN 
        SpeechRecords ON MeetingRecords.id = SpeechRecords.meeting_id 
    WHERE 
        YEAR(MeetingRecords.date) = %s;
    """
    cursor.execute(sql, (year,))
    
    # CSVファイルに出力
    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Date', 'Keyword Count', 'Meeting URL'])
        
        for row in cursor.fetchall():
            date = row[0]
            speech = row[1]
            meeting_url = row[2]
            
            keyword_count = speech.lower().count(keyword.lower())
            
            if keyword_count > 0:
                csvwriter.writerow([date, keyword_count, meeting_url])
                
finally:
    cursor.close()
    connection.close()


