import subprocess

def main():
    data = {}
    out = subprocess.Popen(['docker', 'stats', '--no-stream'],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    result = stdout.splitlines()

    for item in result:
        row = item.decode("utf-8")
        cols = row.split()
        if cols[2] == 'NAME':
            continue
        data[cols[1]] = {}
        data[cols[1]]['id'] = cols[0]
        data[cols[1]]['cpu'] = cols[2]
        data[cols[1]]['memory'] = cols[3]
        data[cols[1]]['memory_perc'] = cols[6]
        data[cols[1]]['pid'] = cols[13]
    
    return data
