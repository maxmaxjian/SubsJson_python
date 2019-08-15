import json
import copy
import os
from collections import OrderedDict

class JsonSubs:
    def __init__(self, path, clockface, clockhands):
        # os.chdir('venv')
        self.path = path
        self.face = clockface
        self.hands = clockhands
        # words = self.face.split('.')
        # words[0] += '_modified'
        # self.out = '.'.join(words)
        # # print self.out
        self.out = self.face
        json_file = open(self.path+self.face).read()
        self.json_obj = json.loads(json_file)
        self.layers = copy.deepcopy(self.json_obj.get('layers'))
        self.indx = []
        for i in range(len(self.layers)):
            if self.layers[i].get('type') == 'RotatingHandLayer':
                self.indx.append(i)

    def appendforlayerat(self, i):
        # print os.getcwd()
        layer = self.layers[i]
        if 'day_src' in layer and 'night_src' in layer:
            day_src_file = self.path+layer.get('day_src')+'.json'
            night_src_file = self.path+layer.get('night_src')+'.json'
            day_file_obj = json.loads(open(day_src_file).read())
            night_file_obj = json.loads(open(night_src_file).read())
            # if (len(day_file_obj) == len(night_file_obj)):
            assert len(day_file_obj) == len(night_file_obj), "day and night have different number of layers in "+day_src_file
            for i in range(len(day_file_obj)):
                layer_copy = copy.deepcopy(layer)
                layer_copy['day_src'] = day_file_obj[i].get('id')
                layer_copy['night_src'] = night_file_obj[i].get('id')
                self.layers.append(layer_copy)
            # sort_order = ['type', 'hand_rotation', 'day_src', 'night_src', 'tick_ms', 'src', 'day_tint', 'night_tint']
            # sorted_layers = [OrderedDict(sorted(item.iteritems(), key=lambda (k,v): sort_order.index(k))) for item in self.layers]
            # # print json.dumps(sorted_layers, indent=4)
            # self.layers = sorted_layers
        elif 'src' in layer:
            src_file = self.path+layer.get('src')+'.json'
            src_file_obj = json.loads(open(src_file).read())
            for i in range(len(src_file_obj)):
                layer_copy = copy.deepcopy(layer)
                layer_copy['src'] = src_file_obj[i].get('id')
                self.layers.append(layer_copy)



    def appendlayers(self):
        for i in self.indx:
            self.appendforlayerat(i)
        self.layers = [self.layers[i] for i in range(len(self.layers)) if i not in self.indx]

    def updateJsonfile(self):
        self.json_obj['layers'] = self.layers
        sort_order = {}
        sort_order['layers'] = ['type', 'src', 'mask', 'hand_rotation', 'day_src', 'night_src', 'tick_ms', 'layout_id', 'day_tint', 'night_tint', 'day_opacity', 'night_opacity']
        sort_order['date_window'] = ['type', 'day_src', 'night_src', 'center_x', 'center_y', 'bottom_y', 'day_tint', 'night_tint', 'style']
        sort_order['complication_bar'] = ['type','position','day_tint','day_opacity','night_tint','night_opacity']
        sort_order['complication_alert'] = sort_order['complication_bar']
        main_sort_order = ['id','type','layers','date_window','complication_bar','complication_alert']
        json_obj = self.json_obj
        for key, val in json_obj.iteritems():
            if isinstance(val, list):
                after_sort = [OrderedDict(sorted(item.iteritems(), key=lambda (k,v): sort_order[key].index(k))) for item in val]
                json_obj[key] = after_sort
            elif isinstance(val, dict):
                after_sort = OrderedDict(sorted(val.iteritems(), key=lambda (k,v): sort_order[key].index(k)))
                json_obj[key] = after_sort
        after_json_obj = OrderedDict(sorted(json_obj.iteritems(), key=lambda (k,v): main_sort_order.index(k)))
        self.json_obj = after_json_obj

        # print json.dumps(self.json_obj, indent=4)
        with open(self.out, 'w') as f:
            json.dump(self.json_obj, f, indent=4)


def main():
    # print os.getcwd()
    path = '/Users/wejian/devel/homework/src/ClockFaceSelectorLibrary/src/main/res/raw/'
    files = os.listdir(path)
    facefiles = [files[i] for i in range(len(files)) if files[i].startswith('clock_face')]
    handfiles = [files[i] for i in range(len(files)) if files[i].startswith('hand_')]
    for facefile in facefiles:
        if facefile != 'clock_face_vibrant_analog_duotone.json':
            start=len('clock_face_')
            end=facefile.find('_', start)
            end = end if end != -1 else len(facefile)
            clockname = facefile[start:end]
            if (clockname != 'animals'):
                print "parsing "+facefile
                hands = [handfiles[i] for i in range(len(handfiles)) if handfiles[i].find(clockname) != -1]
                jsonsubs = JsonSubs(path, facefile, hands)
                jsonsubs.appendlayers()
                jsonsubs.updateJsonfile()

if __name__ == '__main__':
    main()