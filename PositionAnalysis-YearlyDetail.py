import mysql.connector
import csv
import sys
import os

if len(sys.argv) < 4:
    print("Usage: python script.py [START_YEAR] [END_YEAR] [KEYWORD]")
    sys.exit(1)

# コマンドライン引数から西暦の年（開始と終了）とキーワードを取得
start_year = int(sys.argv[1])
end_year = int(sys.argv[2])
keyword = sys.argv[3]

# キーワード名でディレクトリを作成
if not os.path.exists(keyword):
    os.makedirs(keyword)

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

    for year in range(start_year, end_year + 1):
        # SQLクエリを実行
        sql = """
        SELECT
            MeetingRecords.date,
            SpeechRecords.speaker,
            SpeechRecords.speakerGroup,
            SpeechRecords.speakerPosition,
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
        with open(f'{keyword}/{year}.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Date', 'Speaker', 'SpeakerGroup', 'SpeakerPosition', 'Speech', 'Meeting URL'])

            for row in cursor.fetchall():
                date = row[0]
                speaker = row[1]
                speakerGroup = row[2]
                speakerPosition = row[3]
                speech = row[4].replace('\n', ' ')  # 改行コードを削除
                meeting_url = row[5]

                if not speakerPosition or len(speakerPosition)==0:
                    continue
                if keyword.lower() in speakerPosition.lower():
                    csvwriter.writerow([date, speaker, speakerGroup, speakerPosition, speech, meeting_url])

except Exception as e:
    print(f"An error occurred: {type(e).__name__}")
    print(f"Error details: {e}")

finally:
    cursor.close()
    connection.close()

