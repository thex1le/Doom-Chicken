# native imports
import time
import argparse
import os
import sys
import requests
import re
from threading import Thread, Lock
import json
from datetime import datetime
# 3rd party imports
from scapy.all import *

def clrscr():
    # Check if Operating System is Mac and Linux or Windows
   if os.name == 'posix':
      _ = os.system('clear')
   else:
      # Else Operating System is Windows (os.name = nt)
      _ = os.system('cls')

class logger(Thread):
    def __init__(self, filename):
        Thread.__init__(self)
        Thread.daemon = True
        self.filename = filename
        self.data = dict()
        self.loop = True
        self.lock = Lock()
    
    def close(self):
        self.loop = False
        self.write_file(self.data)
        
    def append_log(self, log, key):
        self.lock.acquire()
        if key in self.data.keys():
            now = str(datetime.now())
            msg = "{}, {}".format(now, log)
            self.data[key].append(msg)
        else:
            now = str(datetime.now())
            msg = "{}, {}".format(now, log)
            self.data[key] = [msg]
        self.lock.release()

    def write_file(self, data):
        self.lock.acquire()
        with open(self.filename, 'a') as wf:
            wf.write(json.dumps(data))
        self.lock.release()
    
    def run():
        while self.loop is True:
            if len(self.data) >= 100:
                self.write_file(self.data)
                self.data = dict()
            time.sleep(1)
            

class rtt_url(Thread):
    def __init__(self, dst, slp):
        Thread.__init__(self)
        Thread.daemon = True
        self.avg_rtt = [1]
        self.target = dst
        self.slp = int(slp)
        self.last_run = 100
        self.icd = 'no change'
        self.last_status = 0
    
    def run(self):
        while True:
            start = time.time()
            try:
                req = requests.get(self.target)
            except requests.exceptions.MissingSchema:
                req = requests.get('http://' + self.target)
            self.last_status = req.status_code
            end = time.time()
            self.avg_rtt.append(end - start)
            time.sleep(self.slp)
    
    def get_rtt(self):
        if len(self.avg_rtt) >= 10:
            self.avg_rtt.pop(0)
        rtt = round(sum(self.avg_rtt) / len(self.avg_rtt), 2)
        if rtt > self.last_run:
            stat = 'trending up'
        elif rtt < self.last_run:
            stat = 'trending down'
        elif rtt == self.last_run:
            stat = 'showing no change since last check'
        if rtt >= 50:
            stat = 'seems to be unresponsive'
        self.icd = "{} with a page status of {}".format(stat, self.last_status)
        self.last_run = rtt
        return rtt


class rtt_ping(Thread):
    def __init__(self, dst, slp):
        Thread.__init__(self)
        Thread.daemon = True
        self.avg_rtt = [1]
        self.target = dst
        self.slp = int(slp)
        self.last_run = 100
        self.icd = 'no change'

    def run(self):
        while True:
            start = time.time()
            # will wait for 200
            sr1(IP(dst=str(self.target), ttl=200)/ICMP(), 
                    timeout=60, verbose=False)
            end = time.time()
            self.avg_rtt.append(end - start)
            time.sleep(self.slp)
        
    def get_rtt(self):
        if len(self.avg_rtt) >= 10:
            self.avg_rtt.pop(0)
        rtt = round(sum(self.avg_rtt) / len(self.avg_rtt), 2)
        if rtt > self.last_run:
            self.icd = 'trending up'
        elif rtt < self.last_run:
            self.icd = 'trending down'
        elif rtt == self.last_run:
            self.icd = 'showing no change since last check'
        if rtt >= 50:
            self.icd = 'seems to be unresponsive'
        self.last_run = rtt
        return rtt

def is_url(url):
    ret = False
    match_profile = '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})'
    if re.search(match_profile, url):
        ret = True
    return ret

def get_target_list(f_list):
    with open(f_list) as fl:
        data = fl.readlines()
    return data

def chick():
    r = r"""
          __//
        /.__.\
        \ \/ /
     '__/    \
      \-      )
       \_____/
    _____|_|____
         " "
    """
    s = '\033[91m' + r + '\033[0m'
    return s


def rooster(asc=True):
    r = r"""
      .".".".
    (`       `)               _.-=-.
     '._.--.-;             .-`  -'  '.
    .-'`.o )  \           /  .-_.--'  `\
   `;---) \    ;         /  / ;' _-_.-' `
     `;"`  ;    \        ; .  .'   _-' \
      (    )    |        |  / .-.-'    -`
       '-.-'     \       | .' ` '.-'-\`
        /_./\_.|\_\      ;  ' .'-'.-.
        /         '-._    \` /  _;-,
       |         .-=-.;-._ \  -'-,
       \        /      `";`-`,-"`)
        \       \     '-- `\.\
         '.      '._ '-- '--'/
           `-._     `'----'`;
               `'''--.____,/
                      \\  \
                      // /`
                  ___// /__
                (`(`(---"-`)
        """
    s = '\033[91m' + r + '\033[0m'
    if asc is False:
        s = ''
    return s

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Network speeds')
    parser.add_argument('-target_time', type=int, default=1, dest='time', nargs=1, help='Time in sec between checks of the target')
    parser.add_argument('-check_time', type=int, default=5, dest='check', nargs=1, help='Time between checks to threads for updates on target changes')
    parser.add_argument('-log_file', dest='log', nargs=1, required=True, help='Filename to write the log file to')
    parser.add_argument('-ascii_off', dest='ascii', default=True, action='store_false', help='Disable the ascii to the terminal')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-dst', type=str, default=None, dest='dst', nargs=1, help='IP address to check')
    group.add_argument('-file', default=None, dest='file', nargs=1, help='List of IP targets in a file')
    try:
        args = parser.parse_args()
    except:
        print(chick())
        parser.print_help()
        sys.exit(0)
    if os.geteuid() != 0:
        print("You must be root to run this")
        sys.exit(-1)
    thread_list = dict()
    slp = args.time 
    if args.dst is not None:
        tar = args.dst
    if args.file is not None:
        tar = get_target_list(args.file[0])
    l = logger(args.log[0])
    l.start()
    if type(tar) == list:
        for dst in tar:
            if is_url(dst) is False:
                mclass = rtt_ping
            else:
                mclass = rtt_url
            thread_list[dst.strip()]=(mclass(dst.strip(), slp))
    else:
        if is_url(tar) is False:
            mclass = rtt_ping
        else:
            mclass = rtt_url
        thread_list[tar]=(mclass(tar, slp))
    for t in thread_list.keys():
        thread_list[t].start()
    try:
        while True:
            clrscr()
            print("Testing {}\n{}".format(' '.join(list(thread_list.keys())), rooster(args.ascii)))
            for th in thread_list.keys():
                msg = "Average round trip time for {} is {:.2f} and is {}".format(th,
                    thread_list[th].get_rtt(), thread_list[th].icd)
                l.append_log(msg, th)
                print(msg)
            time.sleep(args.check)
    except KeyboardInterrupt:
        l.close()
        l.join()
        sys.exit(0)
