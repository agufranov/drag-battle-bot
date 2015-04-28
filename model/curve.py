# -*- coding: utf-8 -*-
import os
from base64 import b64decode
import struct
import json
import pygal


filename = os.path.join(os.path.dirname(__file__), 'last_curves.txt')

def read_last_curves_file():
    if os.path.isfile(filename):
        data = None
        f = open(filename, 'r')
        try:
            data = json.load(f)
        except:
            pass
        finally:
            f.close()
        return data

def write_last_curves_file(response):
    f = open(filename, 'wb')
    json.dump(response, f)
    f.close()

curve_names = {
    'trq': u'Крутящий момент',
    'rp': u'Мощность',
    'afw': u'Расход воздуха',
    'prs1': u'Наполнение цилиндра',
    'tmp1': u'Температура впуска',
    'prs4': u'Давление выхлопа'
}

def parse_response(response):
    rev_min = 500
    rev_max = int(response['max'])
    points_num = int(response['l'])
    step = (rev_max - rev_min) / (points_num - 1)
    
    curves = {}
    count = len(response['n'])
    for i in xrange(count):
        curve_decoded = b64decode(response['v'][i])
        curve_num_points = len(curve_decoded) / 4
        unpack_format = '<' + 'f' * curve_num_points
        curve_data = struct.unpack(unpack_format, curve_decoded)
        curves[response['n'][i]] = curve_data
    return (curves, rev_min, rev_max, step)

def plot(curves, last_curves):
    curves_data, rev_min, rev_max, step = curves
    for curve_code in curves_data:
        #if curve_code != 'trq':
            #continue
        curve_name = curve_names.get(curve_code) or '[%s]' % curve_code
        curve_data = curves_data[curve_code]
        chart = pygal.Line(fill=True, show_dots=False)
        chart.x_labels = map(str, range(rev_min, rev_max, step))
        chart.title = curve_name
        chart.add(curve_name, curve_data)
        if last_curves:
            last_curves_data, last_rev_min, last_rev_max, last_step = last_curves
            last_curve_data = last_curves_data[curve_code]
            chart.add(curve_name + ' last', last_curve_data)
        chart.render_in_browser()


def go(response):
    last_response = read_last_curves_file()
    write_last_curves_file(response)
    curves = parse_response(response)
    last_curves = None
    if last_response:
        last_curves = parse_response(last_response)
    plot(curves, last_curves)
