# coding:utf-8
import requests
import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
import sys

def jtalk(t):
    openjtalk = ['open_jtalk']
    mech=['-x','/var/lib/mecab/dic/open-jtalk/naist-jdic']
    htsvoice=['-m','/usr/share/hts-voice/mei/mei_normal.htsvoice']
    speed=['-r','1.0']
    outwav=['-ow','open_jtalk.wav']
    cmd=openjtalk+mech+htsvoice+speed+outwav
    c = subprocess.Popen(cmd,stdin=subprocess.PIPE)
    c.stdin.write(t)
    c.stdin.close()
    c.wait()
    aplay = ['aplay','-q','open_jtalk.wav']
    wr = subprocess.Popen(aplay)

cityName = sys.argv[1]
count = 1
prefId = None

url = "http://weather.livedoor.com/forecast/rss/primary_area.xml"
response = requests.get(url)
root = ET.fromstring(response.text)
for child in root[0][12]:
    if (sys.argv[1] == child.attrib['title']):
        # コマンドライン引数で与えられた県の県庁所在地の天気を返す
        prefId = count-4
        if( prefId < 10):
            cityId = "0" + str(prefId) + "0010"
        else:
            cityId = str(prefId) + "0010"
        break
    count += 1

if(prefId == None):
    print("Error : 見つけられませんでした。")
    print("python alarmWetherInfo.py < ○○県 >　で実行してみてください")
    exit()

url = "http://weather.livedoor.com/forecast/webservice/json/v1?city=" + cityId
response = requests.get(url)
#response_encoding = response.apparent_encoding
data = json.loads(response.text)
forecast = data['forecasts'][0]['telop']
temp_min = data['forecasts'][0]['temperature']['min']
if temp_min == None:
    temp_min = "不明"
else:
    temp_min = data['forecasts'][0]['temperature']['min']['celsius']

temp_max = data['forecasts'][0]['temperature']['max']
if temp_max == None:
    temp_max = "不明"
else:
    temp_max = temp_max = data['forecasts'][0]['temperature']['max']['celsius']

now = datetime.now()
month = '{0:%m}'.format(now)
day = '{0:%d}'.format(now)
hour = '{0:%H}'.format(now)
minute = '{0:%M}'.format(now)
weeks = ["月","火","水","木","金","土","日"]
week = weeks[now.weekday()]

wiki_url = "https://ja.wikipedia.org/w/api.php?format=json&utf8&action=query&prop=revisions&rvprop=content&titles="
wiki_url = wiki_url + mounth+"月"+day+"日"
response = requests.get(wiki_url)
wiki_data = json.loads(response.text)
a = list(wiki_data['query']['pages'].keys())

today_wiki = wiki_data['query']['pages'][a[0]]['revisions'][0]['*']
today_anniv = today_wiki[today_wiki.find("記念日")+16:today_wiki.find("フィクションのできごと")-9]
#　文章中の記号、ノイズ削除
today_anniv = today_anniv.replace("[","")
today_anniv = today_anniv.replace("]","")
today_anniv = today_anniv.replace("<!--","")
today_anniv = "* " + today_anniv

anniv_list = today_anniv.split("\n")
for i in range(len(anniv_list)):
    if(anniv_list[i][0:2] == "* "):
        anniversaries += anniv_list[i] + "。"

today = "本日は"+mounth+"月"+day+"日"+week+"曜日です。"
wether =  cityName+ "の天気は" +forecast+ "。最高気温は" +temp_max+ "、最低気温は" +temp_min + "です。"
text = "おはようございます。"  + today + wether + "本日の記念日は・・・"+anniversaries+"です。"
print(text)
jtalk(text.encode())
