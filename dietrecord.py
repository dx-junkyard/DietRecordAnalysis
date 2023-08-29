import argparse
import json
import mysql.connector
import glob

def importDiet(json_file):
    # MySQLに接続
    conn = mysql.connector.connect(
        host='localhost',
        user='dietrecord',
        password='dietrecord',
        database='dietrecorddb'
    )
    cursor = conn.cursor()
    
    for file_name in glob.glob(json_file):
        with open(file_name, 'r', encoding='utf-8') as f:
            predata = f.read()
            data = ""
            try:
                predata = predata.replace("'", '"')
                predata = predata.replace("None", "null")
                data = json.loads(predata)
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                print(f"Faulty data: {predata[e.pos-10:e.pos+10]}")  # エラー位置の周辺のデータを出力
    
    
        # MeetingRecordsテーブルにデータを挿入
        try:
            cursor.execute("""
                INSERT INTO MeetingRecords (issueID, imageKind, searchObject, session, nameOfHouse, nameOfMeeting, issue, date, closing, meetingURL, pdfURL)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (data['issueID'],data['imageKind'],data['searchObject'],data['session'],
            data['nameOfHouse'], data['nameOfMeeting'], data['issue'], data['date'],
            data['closing'], data['meetingURL'], data['pdfURL']
            ))
        except mysql.connector.errors.ProgrammingError as e:
            print(f"(1) An error occurred: {e}")
            print("  data detail : " + str(data))
        meeting_id = cursor.lastrowid
    
        # SpeechRecordsテーブルにデータを挿入
        for speech in data['speechRecord']:
            try:
                cursor.execute("""
                    INSERT INTO SpeechRecords (meeting_id, speechID, speechOrder, speaker, speakerYomi, speakerGroup, speakerPosition, speakerRole, speech, startPage, createTime, updateTime, speechURL)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    meeting_id, speech['speechID'], speech['speechOrder'], speech['speaker'],
                    speech['speakerYomi'], speech['speakerGroup'], speech['speakerPosition'],
                    speech['speakerRole'], speech['speech'], speech['startPage'],
                    speech['createTime'], speech['updateTime'], speech['speechURL']
                ))
            except mysql.connector.errors.ProgrammingError as e:
                print(f"(2) An error occurred: {e}")
                print("  speech detail : " + str(speech))
    
        # 変更をコミット
        conn.commit()
    
    # MySQLから切断
    cursor.close()
    conn.close()
   

def main():
    parser = argparse.ArgumentParser(description='Process some JSON files.')
    parser.add_argument('json_file_path', help='Path to the JSON file')

    args = parser.parse_args()

    # JSONファイルを読み込む
    importDiet(args.json_file_path)

if __name__ == "__main__":
    main() 
