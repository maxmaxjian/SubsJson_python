import json

filename = 'venv/clock_face_beach_analog_bold.json'
json_file = open(filename).read()
json_obj = json.loads(json_file)
layers = json_obj.get('layers')
# print json.dumps(layers, indent=4)
idx = []
for i in range(len(layers)):
    if layers[i].get('type') == "RotatingHandLayer":
        # print json.dumps(layers[i], indent=4)
        idx.append(i)
print idx
layers = [layers[i] for i in range(len(layers)) if i not in idx]
print json.dumps(layers, indent=4)
# print json.dumps(layers, indent=4)