# -*- encoding: utf-8 -*-
from bottle import route, run, request
import ephem
import json
from datetime import datetime, timedelta

@route('/hello', method = 'GET')
def hello():
    return request.query['aaa']

# <name>は星の名前の英名
@route('/star/<name>', method = 'GET')
def star_position(name):
    # dateパラメータがなければ現在時刻(JST)
    date = datetime.strptime(request.query['date'], '%Y/%m/%d %H:%M:%S') if 'date' in request.query else datetime.now()
    # 経度 パラメータがなければ東京の経度
    longitude = request.query['longitude'] if 'longitude' in request.query else '139.767052'
    # 緯度 パラメータがなければ東京の緯度
    latitude = request.query['latitude'] if 'latitude' in request.query else '35.681167'

    e = ephem.Observer()
    e.lon = longitude
    e.lat = latitude
    # GMTにしたものをephemにセットする
    e.date = to_gmt(date).strftime('%Y/%m/%d %H:%M:%S')

    computed_star = compute_ephem_star(e, star_name = name)
    print(str(e.date))
    print(e.lon)
    print(e.lat)
    return json.dumps({
        'altitude': str(computed_star.alt),
        'azimuth': str(computed_star.az),
        'magnitude': str(computed_star.mag),
        'time': date.strftime('%Y/%m/%d %H:%M:%S')
    }, ensure_ascii=False)

# <names>は星の名前の英名
# Sirius,Caph とカンマ区切り
@route('/stars/<names>', method = 'GET')
def stars_position(names):
    # dateパラメータがなければ現在時刻(JST)
    date = datetime.strptime(request.query['date'], '%Y/%m/%d %H:%M:%S') if 'date' in request.query else datetime.now()
    # 経度 パラメータがなければ東京の経度
    longitude = request.query['longitude'] if 'longitude' in request.query else '139.767052'
    # 緯度 パラメータがなければ東京の緯度
    latitude = request.query['latitude'] if 'latitude' in request.query else '35.681167'

    e = ephem.Observer()
    e.lon = longitude
    e.lat = latitude
    # GMTにしたものをephemにセットする
    e.date = to_gmt(date).strftime('%Y/%m/%d %H:%M:%S')


    star_names = names.split(',')
    ret = {}

    # 各星ごとにデータを出力
    for name in star_names:
        computed_star = compute_ephem_star(e, star_name = name)
        ret[name] = {
            'altitude': str(computed_star.alt),
            'azimuth': str(computed_star.az),
            'magnitude': str(computed_star.mag),
            'time': date.strftime('%Y/%m/%d %H:%M:%S')
        }
    return json.dumps(ret, ensure_ascii=False)

# 星雲・星団等のすべての地平座標
@route('/star_groups/all', method = 'GET')
def stars_groups_all():
    # dateパラメータがなければ現在時刻(JST)
    date = datetime.strptime(request.query['date'], '%Y/%m/%d %H:%M:%S') if 'date' in request.query else datetime.now()
    # 経度 パラメータがなければ東京の経度
    longitude = request.query['longitude'] if 'longitude' in request.query else '139.767052'
    # 緯度 パラメータがなければ東京の緯度
    latitude = request.query['latitude'] if 'latitude' in request.query else '35.681167'

    e = ephem.Observer()
    e.lon = longitude
    e.lat = latitude
    # GMTにしたものをephemにセットする
    e.date = to_gmt(date).strftime('%Y/%m/%d %H:%M:%S')

    ret = {}
    # 星雲等ごとにデータを付与
    for data in xephem_star_data():
        computed_star = compute_xephem_data(e, xephem_data = data)
        ret[computed_star.name] = {
            'altitude': str(computed_star.alt),
            'azimuth': str(computed_star.az),
            'magnitude': str(computed_star.mag),
            'time': date.strftime('%Y/%m/%d %H:%M:%S')
        }
    return json.dumps(ret, ensure_ascii=False)

def compute_ephem_star(e, star_name = None):
    star = ephem.star(star_name)
    star.compute(e)
    return star

# XEhem形式のデータを扱う
def compute_xephem_data(e, xephem_data = None):
    star = ephem.readdb(xephem_data)
    star.compute(e)
    return star

# datetimeクラスをGMTに変換
def to_gmt(date):
    return date - timedelta(hours=9)

# 度分秒を度のみに変換
def to_degrees(degree):
    degree_list = degree.split(':')
    return (
            float(degree_list[0]) +
            float(degree_list[1])/60.0 +
            float(degree_list[2])/3600.0
    )

def xephem_star_data():
    return ["プレセペ星団(M44),f,8:40.4:00,19:59:00,3.7,2000.0,", "プレアデス星団(M45),f,3:47:24,24:07:00,1.6,2000.0,"]

run(host='0.0.0.0', port=5432, debug=False)

