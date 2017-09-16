import os
import time
from random import random
from secret import SECRET
from reset import reset
import requests
import sys
import json

LISTENER_ROUTE = 'http://localhost:5000/open-state/listener.php'


def real_time():
    buff = []
    while True:
        buff.append(str(int(time.time())))
        print buff
        if random() < 0.5:
            data = '\n'.join(buff)
            r = requests.post(LISTENER_ROUTE, data={'secret': SECRET, 'data': data})
            print r.status_code, r.reason
            if int(r.status_code) == 200:
                buff = []
        print 'buff:', buff

        time.sleep(1)


def dummy_historical():
    reset()

    start_time = 1431702000  # may 15th 2015
    tim = start_time
    end = int(time.time())

    rang = float(end - start_time)
    iters = 0
    buff = []
    while True:
        iters += 1
        tim += 60 * 15
        if random() < 0.2:
            buff.append(str(tim))
            while random() < 0.8:
                tim += 60 * 15
                buff.append(str(tim))

        if iters % 100 == 0:

            print round(((tim - start_time) / rang) * 100, 2), '% done', '\t\t\t\r',

            sys.stdout.flush()
            while True:
                try:
                    requests.post(LISTENER_ROUTE, data={'secret': SECRET, 'data': '\n'.join(buff)})
                    break
                except:
                    pass
            buff = []

        if tim > end:
            break


def import_real():
    reset()

    with open(os.path.dirname(os.path.realpath(__file__)) + '/data/real_dv.json', 'r') as f:
        d = json.load(f)
    buff = []
    for i in d:
        if len(i) > 2:
            continue
        t = i[0]
        while True:
            buff.append(str(t))
            t += 60 * 15
            if t > i[1]:
                break

    while True:
        try:
            requests.post(LISTENER_ROUTE, data={'secret': SECRET, 'data': '\n'.join(buff)})
            break
        except:
            pass


def usage():
    print 'usage: %s <real|dummy|realtime>' % sys.argv[0].split('/')[-1]
    exit()


if len(sys.argv) < 2:
    usage()

if sys.argv[1] == 'real':
    import_real()
elif sys.argv[1] == 'dummy':
    dummy_historical()
elif sys.argv[1] == 'realtime':
    real_time()
else:
    usage()
