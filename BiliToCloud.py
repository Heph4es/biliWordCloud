import json
import time
import re
import jieba
from matplotlib.image import imread
from wordcloud import wordcloud
from bilibili_api import video
import requests
from bs4 import BeautifulSoup


def getDM(bvid):
    Mode = input("选择模式(1:全弹幕/2:全分词)\n")
    info = video.get_video_info(bvid=bvid)
    data = {
        'bvid': info['bvid'],
        'cid': info['cid'],
        'ownerName': info['owner']['name'],
        'videoName': info['title'],
        'DM': [],
        'mode': ""
    }
    url = "https://api.bilibili.com/x/v1/dm/list.so?oid=" + str(info['cid'])
    response = requests.get(url=url)
    response.encoding = response.apparent_encoding
    select = BeautifulSoup(response.text, 'html.parser')
    DMdata = [s.get_text() for s in select.find("i").find_all('d')]
    if Mode == "1":
        str1 = ' '.join(DMdata)
        data['mode'] = "全弹幕"
    else:
        str1 = ''.join(DMdata)
        str1 = ' '.join(jieba.lcut_for_search(str1))
        data['mode'] = "全分词"
    data['DM'] = str1
    return data


def createWordCloud(data, font_path, mask_path, background_color, max_words):

    if background_color == "-1":
        background_color = "white"
    if max_words == "-1":
        max_words = 300

    if font_path == "-1" and mask_path == "-1":
        w = wordcloud.WordCloud(background_color=background_color,
                                max_words=int(max_words))
    elif font_path == "-1" and mask_path != "-1":
        mask = imread(mask_path)
        w = wordcloud.WordCloud(background_color=background_color, mask=mask,
                                max_words=int(max_words))
    elif font_path != "-1" and mask_path == "-1":
        w = wordcloud.WordCloud(background_color=background_color, font_path=font_path,
                                max_words=int(max_words))
    else:
        mask = imread(mask_path)
        w = wordcloud.WordCloud(background_color=background_color, mask=mask, font_path=font_path, max_words=int(max_words))

    w.generate(data['DM'])

    timec = time.ctime()
    timec = timec.replace(":", "-")
    save_path = "【" + data['ownerName'] + "】" + data['videoName'] + " @BV：" + data['bvid'] + " @时间：" + str(
        timec) + "(词量：" + str(max_words) + " ,分词模式：" + data['mode'] + ")" + ".png"
    blacklist = r"[\/\\\:\*\?\"\<\>\|]"
    save_path = ".\\" + re.sub(blacklist, "", save_path)
    w.to_file(save_path)


createWordCloud(getDM(input("输入正确的BV号\n")), input("输入正确的字体路径[无则输入-1以默认无](否则中文显示可能出现错误)\n"), input("指定词云形状图片的路径["
                                                                                                  "无则输入-1以默认无]\n"),
                input("指定背景色[无则输入-1以默认白色]\n"), input("指定词云词量规模[无则输入-1以默认300]\n"))
