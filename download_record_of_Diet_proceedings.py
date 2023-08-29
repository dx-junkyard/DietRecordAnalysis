# -*- coding: utf-8 -*-

import pandas as pd
import urllib.parse
import requests
import xml.etree.ElementTree as ET
import datetime as dt
import time
import os

class SpeechSummary:
    def __init__(self,year_str, issue_id, srecord_json):
        self.year = year_str
        self.issueID = issue_id
        self.speechID = srecord_json["speechID"]
        self.speechOrder = srecord_json["speechOrder"]
        self.speaker = srecord_json["speaker"]
        self.speakerYomi = srecord_json["speakerYomi"]
        self.speakerGroup = srecord_json["speakerGroup"]
        self.speakerPosition = srecord_json["speakerPosition"]
        self.speakerRole = srecord_json["speakerRole"]
#        self.speech = srecord_json["speech"]
        self.startPage = srecord_json["startPage"]
        self.createTime = srecord_json["createTime"]
        self.updateTime = srecord_json["updateTime"]
        self.speechURL = srecord_json["speechURL"]
    def writeSpeechSummary(self, dir_name, filename_extention=".csv"):
        with open(dir_name + "/speech_" +  self.year + filename_extention,'a') as f:
            w_list = []
            w_list.append(str(self.issueID))
            if self.speechOrder == None:
                w_list.append("")
            else:
                w_list.append(str(self.speechOrder))
            if self.speaker == None:
                w_list.append("")
            else:
                w_list.append(self.speaker)
            if self.speakerYomi == None:
                w_list.append("")
            else:
                w_list.append(self.speakerYomi)
            if self.speakerGroup == None:
                w_list.append("")
            else:
                w_list.append(self.speakerGroup)
            if self.speakerPosition == None:
                w_list.append("")
            else:
                w_list.append(self.speakerPosition)
            if self.speakerRole == None:
                w_list.append("")
            else:
                w_list.append(self.speakerRole)
            if self.startPage == None:
                w_list.append("")
            else:
                w_list.append(str(self.startPage))
            if self.createTime == None:
                w_list.append("")
            else:
                w_list.append(self.createTime)
            if self.updateTime == None:
                w_list.append("")
            else:
                w_list.append(self.updateTime)
            if self.speechURL == None:
                w_list.append("")
            else:
                w_list.append(self.speechURL)
            f.write(",".join(w_list)+"\n")
    def showSpeechRecord(self):
        print(self.speechID + " [" + str(self.speechOrder) + "] / " + self.speaker + " / " + self.speech)

class SpeechRecord:
    def __init__(self,year_str, srecord_json):
        self.year = year_str
        self.speechID = srecord_json["speechID"]
        self.speech = srecord_json["speech"]
    def writeSpeechRecord(self, dir_name, filename_extention=".txt"):
        with open(dir_name + "/speech/" +  self.speechID + filename_extention,'w') as f:
            f.write(self.speech)
    

class MeetingRecord:
    def __init__(self, year_str,  mrecord_json):
        self.org_json = mrecord_json
        self.issueID = mrecord_json["issueID"]
        self.imageKind = mrecord_json["imageKind"]
        self.searchObject = mrecord_json["searchObject"]
        self.session = mrecord_json["session"]
        self.nameOfHouse = mrecord_json["nameOfHouse"]
        self.nameOfMeeting = mrecord_json["nameOfMeeting"]
        self.issue = mrecord_json["issue"]
        self.date = mrecord_json["date"]
        self.closing = mrecord_json["closing"]
        self.meetingURL = mrecord_json["meetingURL"]
        self.pdfURL = mrecord_json["pdfURL"]
        self.speechRecords = []
        self.speechSummaries = []
        #self.filename = self.date + "_" + self.issueID
        self.filename = year_str
        for srecord_json in mrecord_json["speechRecord"]:
            speechRecord = SpeechRecord(year_str,srecord_json)
            speechSummary = SpeechSummary(year_str,self.issueID,srecord_json)
            self.speechRecords.append(speechRecord)
            self.speechSummaries.append(speechSummary)
    def writeMeetingRecord(self, dir_name, filename_extention=".txt"):
        with open(dir_name + "/meeting_" +  self.filename + filename_extention,'a') as f:
            w_list = []
            w_list.append(str(self.issueID))
            w_list.append(self.imageKind)
            w_list.append(str(self.searchObject))
            w_list.append(str(self.session))
            w_list.append(self.nameOfHouse)
            w_list.append(self.nameOfMeeting)
            w_list.append(str(self.issue))
            w_list.append(self.date)
            w_list.append(self.meetingURL)
            w_list.append(self.pdfURL)
            f.write(",".join(w_list)+"\n")
        for sr in self.speechRecords:
            sr.writeSpeechRecord(dir_name,filename_extention)
        for ss in self.speechSummaries:
            ss.writeSpeechSummary(dir_name,filename_extention)
        with open(dir_name + "/meeting_json/" +  self.date + "_" + self.issueID + ".json",'w') as f_json:
            f_json.write(str(self.org_json))
    def showMeetingRecord(self):
        print("meeting_date : " + self.date)
        print("file name : " + self.filename)
        for sr in self.speechRecords:
            sr.showSpeechRecord()

class Meeting:
    def __init__(self,year_str, response_json):
        self.numberOfRecords = response_json["numberOfRecords"]
        self.numberOfReturn = response_json["numberOfReturn"]
        self.startRecord = response_json["startRecord"]
        self.nextRecordPosition = response_json["nextRecordPosition"]
        self.meetingRecords = []
        for mrecord_json in response_json["meetingRecord"]:
            meetingRecord = MeetingRecord(year_str,mrecord_json)
            self.meetingRecords.append(meetingRecord)

    def setOutput(self, dir_name, filename_extention=".csv"):
        self.dirName = dir_name
        self.filenameExtention = filename_extention

class MeetingManager:
    def __init__(self,dir_name):
        self.meeting_list = []
        self.dir_name = dir_name
    def getRecordOfDiet(self,url, params: dict):
        parameter = '?' + urllib.parse.quote('maximumRecords=10'
                                + '&startRecord=' + str(params['startRecord'])
                                + '&from=' + params['from']
                                + '&until=' + params['until']
                                + '&recordPacking=json')
        response = requests.get(url + parameter)
        return response.json()
    def getEndDate(self,start_date, days):
        # 開始日付と終了日付の取得
        from_dt = dt.datetime.strptime(start_date, '%Y-%m-%d')
        print("from : " + from_dt.strftime('%Y-%m-%d'))
        end_dt = from_dt + dt.timedelta(days=days)
        end_date = end_dt.strftime('%Y-%m-%d')
        return end_date
    def getYear(self,date_str):
        date_dt = dt.datetime.strptime(date_str, '%Y-%m-%d')
        year_str = date_dt.strftime('%Y')
        return year_str
    def setDir(self,year_str):
        self.dir_name += "/" + year_str
        os.makedirs(self.dir_name)
        #os.makedirs(self.dir_name + "/meeting/")
        os.makedirs(self.dir_name + "/meeting_json/")
        os.makedirs(self.dir_name + "/speech/")
    def getMeetings(self,start_date, days):
        end_date = self.getEndDate(start_date, days)
        year_str = self.getYear(start_date)
        self.setDir(year_str)
        #
        url = 'http://kokkai.ndl.go.jp/api/1.0/meeting'
        ret_n = 1
        total_n = 0
        next_pos = 0
        startRecord = 1
        while ret_n > 0:
            params = {'startRecord': startRecord, 'from': start_date, 'until': end_date}
            response_json = self.getRecordOfDiet(url, params)
            meeting = Meeting(year_str, response_json)
            for mrecord in meeting.meetingRecords:
                mrecord.writeMeetingRecord("./dl/" + year_str,".csv")
            if meeting == None:
                return
            #self.meeting_list.extend(meeting.meetingRecords)
            ret_n = response_json["numberOfReturn"]
            next_pos = response_json["nextRecordPosition"]
            if next_pos == None:
                print("get end of issue None")
                break
            total_n = response_json["numberOfRecords"]
            startRecord = next_pos
            time.sleep(1)
            print("[" + str(startRecord) + "/" + str(total_n) + "]  " + "sleep 2sec....")
    def showMeetings(self):
        for m in self.meeting_list:
            m.showMeetingRecord()

if __name__ == '__main__':

    # 開始日付の指定    
    from_int = 2016
    for i in range(1):
        from_year = str(from_int + i)
        from_str = from_year + '-01-01'
        # 何日後まで？
        days=365

        mm = MeetingManager("./dl")
        mm.getMeetings(from_str,days)
        print("fin:" + from_year)


