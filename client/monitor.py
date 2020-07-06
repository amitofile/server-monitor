'''
Python node script to fetch all system information
@author Amit P
@since 20200602
@lastedit 20200607
'''

import configparser
import psutil as ps
import socket
import time
import json
import platform
import datetime
import threading
from services.redis as _redis
from services.docker as _docker
from services.streamer as _streamer

config = configparser.ConfigParser()
config.read('config.ini')
udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp.bind(('127.0.0.1', 8082))
node_data = {'node': {}, 'cpu': {}, 'memory': {},
             'disk': {}, 'network': {}, 'processes': {}, 'applications': {}}

if config['CollectInformation']['Node'] == 'true':
    node_data['node']['id'] = config['DEFAULT']['NodeId']
    node_data['node']['name'] = socket.gethostname()
    node_data['node']['os'] = platform.system()
    node_data['node']['version'] = platform.release()

if config['CollectInformation']['CPU'] == 'true':
    node_data['cpu']['count'] = ps.cpu_count()
    node_data['cpu']['freq'] = ps.cpu_freq(percpu=True)


def main():
    if config['CollectInformation']['CPU'] == 'true':
        node_data['cpu']['times'] = ps.cpu_times_percent(
            interval=1, percpu=True)

    if config['CollectInformation']['Memory'] == 'true':
        memory_status = ps.virtual_memory()
        stat = {'total': memory_status.total, 'used': memory_status.used,
                'percent_used': memory_status.percent}
        node_data['memory']['main'] = stat
        memory_status = ps.swap_memory()
        stat = {'total': memory_status.total, 'used': memory_status.used,
                'percent_used': memory_status.percent}
        node_data['memory']['swap'] = stat

    if config['CollectInformation']['Disk'] == 'true':
        node_data['disk']['stat'] = diskInformation()

    if config['CollectInformation']['Network'] == 'true':
        network_stats = networkLatency()
        node_data['network']['up'] = network_stats["traffic_out"]
        node_data['network']['down'] = network_stats["traffic_in"]

    if config['CollectInformation']['Processes'] == 'true':
        process_running = processSortedByMemory()
        node_data['processes']['total'] = len(process_running)
        node_data['processes']['top'] = process_running[:int(
            config['Process']['TopProcessCount'])]
    
    if config['CollectInformation']['Redis'] == 'true':
        node_data['applications']['redis'] = _redis.main()

    if config['CollectInformation']['Docker'] == 'true':
        node_data['applications']['docker'] = _docker.main()

    if config['CollectInformation']['Streamer'] == 'true':
        node_data['applications']['streamer'] = _streamer.main()

    node_data['timestamp'] = datetime.datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%S+00:00")

    broadcast(node_data)


def broadcast(data):
    message = str.encode(json.dumps(data))
    udp.sendto(message, (config['DEFAULT']['MasterIP'],
                         int(config['DEFAULT']['MasterPort'])))


def diskInformation():
    disk_info = ps.disk_partitions()
    disks = []
    for part in disk_info:
        try:
            disk = {
                "name": part.device,
                "type": part.fstype,
                "total_size": ps.disk_usage(part.mountpoint).total,
                "used_size": ps.disk_usage(part.mountpoint).used,
                "percent_used": ps.disk_usage(part.mountpoint).percent
            }
            disks.append(disk)
        except:
            pass
    return disks


def networkLatency():
    net1_out = ps.net_io_counters().bytes_sent
    net1_in = ps.net_io_counters().bytes_recv
    time.sleep(1)
    net2_out = ps.net_io_counters().bytes_sent
    net2_in = ps.net_io_counters().bytes_recv
    if net1_in > net2_in:
        current_in = 0
    else:
        current_in = net2_in - net1_in
    if net1_out > net2_out:
        current_out = 0
    else:
        current_out = net2_out - net1_out
    network = {"traffic_in": current_in, "traffic_out": current_out}
    return network


def processSortedByMemory():
    listOfProcObjects = []
    for proc in ps.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
            pinfo['memory_uses'] = proc.memory_info().vms  # / (1024 * 1024)
            if pinfo['name'] == 'python3':
                continue
            listOfProcObjects.append(pinfo)
        except (ps.NoSuchProcess, ps.AccessDenied, ps.ZombieProcess):
            pass
    # Sort list of dict by key vms i.e. memory usage
    listOfProcObjects = sorted(
        listOfProcObjects, key=lambda procObj: procObj['memory_uses'], reverse=True)
    return listOfProcObjects

def main2():
    data, addr = udp.recvfrom(1024)
    command = data.decode("utf-8")
    switch (command) {
        case "EXCHANGE_SPLITTER_RESTART":
            _streamer.restart('StreamerIOSplitterRestart')
            break;
        case "EXCHANGE_FEEDER_RESTART":
            _streamer.restart('EXCHANGE_FEEDER')
            break;
        case "ORDER_MAIN_RESTART":
            _streamer.restart('SPLITTER')
            break;
        case "ORDER_FEEDER_RESTART":
            _streamer.restart('SPLITTER')
            break;
        case "REDIS_RESTART":
            
            break;
        case "NGINX_RESTART":
            
            break;
        case "DOCKER_RESTART":
            
            break;
    }

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

set_interval(main, 5)
set_interval(main2, 1)
