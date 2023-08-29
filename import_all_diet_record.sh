#!/bin/bash

# ベースディレクトリのパスを変数に格納
# 例）BASE_DIR="/Users/userhome/download_record_of_Diet_proceedings/dl"
BASE_DIR="./dl"

# ログディレクトリのパスを変数に格納
# 例）LOG_DIR="./log"
LOG_DIR=(LOGファイル出力先ディレクトリを記載してください）

# logディレクトリが存在しない場合、作成
if [ ! -d $LOG_DIR ]; then
    mkdir -p $LOG_DIR
fi

# 年ごとのディレクトリをループで処理
for year in $(ls $BASE_DIR); do
    # meeting_jsonディレクトリのパスを変数に格納
    MEETING_JSON_DIR="$BASE_DIR/$year/meeting_json"

    # meeting_jsonディレクトリが存在するか確認
    if [ -d $MEETING_JSON_DIR ]; then
        # JSONファイルごとにループで処理
        for json_file in $(ls $MEETING_JSON_DIR/*.json); do
            # JSONファイルの名前から拡張子を除去
            json_filename=$(basename -- "$json_file")
            json_name="${json_filename%.*}"

            # dietrecord.pyにJSONファイルを渡して実行し、エラーログを書き出す
            python dietrecord.py $json_file 2>> "$LOG_DIR/$json_name.log"
        done
    fi
done

