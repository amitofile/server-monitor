import subprocess

def main():
    data = {}
    out = subprocess.Popen(['redis-cli', 'INFO'],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    result = stdout.splitlines()
    for item in result:
        row = item.split(b':')
        if row[0] == b'redis_version':
            data['redis_version'] = (row[1]).decode("utf-8")
        if row[0] == b'redis_mode':
            data['redis_mode'] = (row[1]).decode("utf-8")
        if row[0] == b'process_id':
            data['process_id'] = int(row[1])
        if row[0] == b'tcp_port':
            data['tcp_port'] = int(row[1])
        if row[0] == b'uptime_in_seconds':
            data['uptime_in_seconds'] = int(row[1])
        if row[0] == b'connected_clients':
            data['connected_clients'] = int(row[1])
        if row[0] == b'used_memory':
            data['used_memory'] = int(row[1])
        if row[0] == b'used_memory_peak':
            data['used_memory_peak'] = int(row[1])
        if row[0] == b'total_connections_received':
            data['total_connections_received'] = int(row[1])
        if row[0] == b'role':
            data['role'] = (row[1]).decode("utf-8")
        if row[0] == b'connected_slaves':
            data['connected_slaves'] = int(row[1])
        if row[0] == b'used_cpu_sys':
            data['used_cpu_sys'] = float(row[1])
        if row[0] == b'used_cpu_user':
            data['used_cpu_user'] = float(row[1])
    return data
