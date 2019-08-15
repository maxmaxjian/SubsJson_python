import json
import copy
import os
from collections import OrderedDict

class handsInline:

    def __init__(self, clockface, path):

        self.out = 'out'+'/'+clockface

        self.clockface = clockface
        self.master_json = json.loads(open(self.clockface).read())
        self.layers = copy.deepcopy(self.master_json.get('layers'))
        self.indx = [i for i in range(len(self.layers)) if self.layers[i]['type'] == 'RotatingHandLayer']

        self.path = path
        files = os.listdir(path)
        begin = len('clock_face_')
        end = self.clockface.find('_', begin)
        end = end if end != -1 else self.clockface.find('.', begin)
        clockname = self.clockface[begin:end]
        handfiles = [files[i] for i in range(len(files)) if files[i].startswith('hand_') and files[i].find(clockname) != -1]
        self.hands = {}
        for handfile in handfiles:
            hand_json = json.loads(open(self.path+handfile).read())
            for hand in hand_json:
                id = hand.get('id')
                item = hand.get('item')
                assert id not in hand, "hand {0} already exists".format(id)
                self.hands[id] = item

    def replace(self, idx):
        layer_copy = copy.deepcopy(self.layers[idx])
        if 'src' in layer_copy:
            hand_id = layer_copy.get('src')
            layer_copy['src'] = self.hands.get(hand_id).get('src')
        elif 'day_src' in layer_copy and 'night_src' in layer_copy:
            day_hand_id = layer_copy.get('day_src')
            night_hand_id = layer_copy.get('night_src')
            day_src = self.hands.get(day_hand_id).get('src')
            night_src = self.hands.get(night_hand_id).get('src')
            assert day_src==night_src, "day_src {0} and night_src {1} use different png files".format(day_src, night_src)
            del layer_copy['day_src']
            del layer_copy['night_src']
            day_tint = self.hands.get(day_hand_id).get('tint')
            night_tint = self.hands.get(night_hand_id).get('tint')
            assert (day_tint!='' and night_tint!='') or (day_tint=='' and night_tint==''), "tint was absent in day_src {0} or night_src {1}".format(day_src, night_src)
            layer_copy['src'] = day_src
            if day_tint!='':
                layer_copy['day_tint'] = day_tint
                layer_copy['night_tint'] = night_tint
        else:
            assert False, "day_src or night_src was absent"
        self.layers[idx] = layer_copy

    def sortJson(self):
        sort_order = {}
        sort_order['layers'] = ['type', 'src', 'mask', 'hand_rotation', 'day_src', 'night_src', 'layout_id', 'day_tint',
                                'night_tint', 'day_opacity', 'night_opacity', 'tick_ms']
        sort_order['date_window'] = ['type', 'day_src', 'night_src', 'center_x', 'center_y', 'bottom_y', 'day_tint',
                                     'night_tint', 'style']
        sort_order['complication_bar'] = ['type', 'position', 'day_tint', 'day_opacity', 'night_tint', 'night_opacity']
        sort_order['complication_alert'] = sort_order['complication_bar']
        main_sort_order = ['id', 'type', 'layers', 'date_window', 'complication_bar', 'complication_alert']

        json_obj = self.master_json
        for key, val in json_obj.iteritems():
            if isinstance(val, list):
                after_sort = [OrderedDict(sorted(item.iteritems(), key=lambda (k, v): sort_order[key].index(k))) for
                              item in val]
                json_obj[key] = after_sort
            elif isinstance(val, dict):
                after_sort = OrderedDict(sorted(val.iteritems(), key=lambda (k, v): sort_order[key].index(k)))
                json_obj[key] = after_sort
        after_json_obj = OrderedDict(sorted(json_obj.iteritems(), key=lambda (k, v): main_sort_order.index(k)))
        self.master_json = after_json_obj

    def writeToJson(self):
        for idx in self.indx:
            self.replace(idx)
        self.master_json['layers'] = self.layers

        self.sortJson()

        # print json.dumps(self.master_json, indent=4)
        with open(self.out, 'w') as f:
            json.dump(self.master_json, f, indent=4)

def main():
    # facefile = 'clock_face_animals_analog_duotone.json'
    files = os.listdir('.')
    facefiles = [files[i] for i in range(len(files)) if files[i].startswith('clock_face_') and files[i].endswith('.json')]
    for facefile in facefiles:
        if facefile not in ['clock_face_garden_hybrid_large.json', 'clock_face_garden_hybrid_simple.json', 'clock_face_garden_hybrid_stacked.json',
                            'clock_face_lava_analog_bold.json', 'clock_face_lava_analog_botanical.json',
                            'clock_face_orbit_analog_planets.json', 'clock_face_orbit_hybrid_simple.json', 'clock_face_orbit_hybrid_stacked.json', 'clock_face_orbit_hybrid_standard_bottom.json']:
            path = '/Users/wejian/devel/homework/src/ClockFaceSelectorLibrary/src/main/res/raw/'
            print "converting {}".format(facefile)
            inliner = handsInline(facefile, path)
            inliner.writeToJson()

if __name__ == "__main__":
    main()
