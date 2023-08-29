# DietRecordAnalysis

## 対象環境
- Mac or Linux
- Python 3.8.3 で動作確認できています
- Dockerがインストールされている必要があります


## 手順

### 1. 国会会議録をダウンロードする
```
sh download_record_of_Diet_proceedings.py
```


### 2. MySQLを起動する
```
docker-compose up -d
```


### 3. ダウンロードした国会会議録をMySQLにインポートする
```
sh import_all_diet_record.sh
```

