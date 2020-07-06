import subprocess

data = {
    'exchange': {
        'splitter': {'status': 'stopped', 'price': 'off', 'marketdepth': 'off', 'indices': 'off'},
        'feeder': {'status': 'stopped'}
    },
    'order': {
        'main': {'status': 'stopped'},
        'feeder': {'status': 'stopped'}
    }
}

def restart(process):
    out = subprocess.Popen(['forever', 'list'],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    result = stdout.splitlines()
    print(result)

def main():
    data['exchange']['splitter']['status'] = 'stopped'
    data['exchange']['feeder']['status'] = 'stopped'
    data['order']['main']['status'] = 'stopped'
    data['order']['feeder']['status'] = 'stopped'

    out = subprocess.Popen(['netstat', '-ntulp'],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    result = stdout.splitlines()
    for item in result:
        row = item.decode("utf-8")
        cols = row.split()
        if "9540" in cols[3]:
            data['exchange']['splitter']['status'] = 'running'

        if "8087" in cols[3]:
            data['exchange']['feeder']['status'] = 'running'

        if "9550" in cols[3]:
            data['order']['main']['status'] = 'running'

        if "8083" in cols[3]:
            data['order']['feeder']['status'] = 'running'

    return data
