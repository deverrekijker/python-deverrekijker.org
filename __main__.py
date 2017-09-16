import base64
import datetime
import io
import json
import os
from matplotlib import pyplot as plt
import time
import numpy
from flask import Flask
from flask import render_template
from flask import request
from matplotlib import colors

import index_constants
from secret import SECRET

app = Flask(__name__)

DATA_DIR = os.path.dirname(os.path.realpath(__file__)) + '/data/'
DATA_PATH = DATA_DIR + 'data.json'
LAST_SIGNAL_PATH = DATA_DIR + 'last_signal.json'
HOURS_GMT_DISTANCE = 2
GRANULARITY = 15 * 60  # one block for every 15 minutes


@app.route('/')
def index():
    return render_template('index.html', c=index_constants, maintenance=False)


@app.route('/graph')
def graph():
    # h*cking time zones
    # h*cking summer time adjustments
    # ????
    # not sure if this was resolved in the js/css graph either
    # problems: - ticks for date and hour of day
    #           - make sure the time shifting is all right



    try:

        if not os.path.isfile(DATA_PATH):
            return 'No data to plot :/'

        with open(DATA_PATH, 'r') as f:
            d = json.load(f)

        first_ts = d['start'] * 15 * 60
        seconds_since_midnight = first_ts % (60 * 60 * 24)
        shift = seconds_since_midnight / (15 * 60) + 4 * HOURS_GMT_DISTANCE

        print shift

        blocks = d['opens'][-1] - shift
        rows = blocks / (4 * 24) + 1

        data = numpy.zeros(shape=(rows, 24 * 4))

        for i in d['opens']:
            try:
                data[len(data) - ((i + shift) / (24 * 4)), (i + shift) % (24 * 4)] = 1
            except:
                pass

        img = io.BytesIO()

        print data.shape

        # create discrete colormap
        cmap = colors.ListedColormap(['gray', 'lightgreen'])
        bounds = [0, 0.5, 1]
        norm = colors.BoundaryNorm(bounds, cmap.N)

        fig, ax = plt.subplots()
        ax.imshow(data, cmap=cmap, norm=norm)

        # draw gridlines
        ax.grid(which='major', axis='x', linestyle='-', color='w', linewidth=1)

        ax.set_xticks(numpy.arange(0, 24 * 4, 12))
        # ax.set_yticks(numpy.arange(0, rows, 1))

        # ax.figure(figsize=(1,1))
        # ax.set_aspect('equal')
        fig.set_size_inches(30, 60, forward=True)

        plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0)

        img.seek(0)

        plot_url = base64.b64encode(img.getvalue()).decode()

        return '<img src="data:image/png;base64,{}">'.format(plot_url)
    except Exception as e:
        print e.message


@app.route('/resources/<kind>/<path>')
def load_resource(kind, path):
    return render_template('%s/%s' % (kind, path))


@app.route('/current', methods=['POST'])
def current_open_info():
    if not os.path.isfile(LAST_SIGNAL_PATH):
        return json.dumps({'is_open': False, 'last_signal': 0})
    with open(LAST_SIGNAL_PATH, 'r') as f:
        last_signal_timestamp = json.load(f)
        last_signal_human_readable = datetime.datetime.fromtimestamp(last_signal_timestamp).strftime('%d.%m.%Y %H:%M')

        return json.dumps({
            'is_open': time.time() - last_signal_timestamp < 5 * 60,
            'last_signal': last_signal_human_readable
        })


# ugly and misleading route (no php is involved here), to avoid having to update the pi
@app.route('/open-state/listener.php', methods=['POST'])
def receive_signal():
    received_datapoints = [int(float(i)) for i in request.form['data'].split('\n')]

    # not very secure but not very sensitive or important data either
    assert request.form['secret'] == SECRET

    assert len(received_datapoints) > 0

    if os.path.isfile(DATA_PATH):
        with open(DATA_PATH, 'r') as f:
            data = json.load(f)
            data['opens'] = set(data['opens'])
    else:
        data = {'start': received_datapoints[0] / GRANULARITY, 'opens': set([])}

    data['opens'] = sorted(
        list(data['opens'].union(set([i / GRANULARITY - data['start'] for i in received_datapoints]))))

    with open(DATA_PATH, 'w') as f:
        json.dump(data, f)

    with open(LAST_SIGNAL_PATH, 'w') as f:
        json.dump(received_datapoints[-1], f)

    return 'okidok'


if __name__ == '__main__':
    app.run()
