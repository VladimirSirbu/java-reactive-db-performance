from config import wait_to_start, wait_after_kill, test_duration, primer_duration, wait_after_primer
from config import javacmd, wrkcmd, wrktimeout, test_URL
from config import logger
from config import jarfiles
from config import concurrency_levels
import re
import subprocess
import time
import os
import signal

def get_cpu_and_memory(pid, cpu_user_before, cpu_user_after, cpu_kern_before, cpu_kern_after):
    cpu_user_diff = int(cpu_user_after) - int(cpu_user_before)
    cpu_kern_diff = int(cpu_kern_after) - int(cpu_kern_before)

    mem_kb_uss = get_mem_kb_uss(pid)
    mem_kb_pss = get_mem_kb_pss(pid)
    mem_kb_rss = get_mem_kb_rss(pid)

    return f',{cpu_user_diff},{cpu_kern_diff}{mem_kb_uss}{mem_kb_pss}{mem_kb_rss}'

def wrk_data(wrk_output):
    return (
        f",{wrk_output.get('lat_avg')},"
        f"{wrk_output.get('lat_stdev')},"
        f"{wrk_output.get('lat_max')},"
        f"{wrk_output.get('req_avg')},"
        f"{wrk_output.get('req_stdev')},"
        f"{wrk_output.get('req_max')},"
        f"{wrk_output.get('tot_requests')},"
        f"{wrk_output.get('tot_duration')},"
        f"{wrk_output.get('read')},"
        f"{wrk_output.get('err_connect')},"
        f"{wrk_output.get('err_read')},"
        f"{wrk_output.get('err_write')},"
        f"{wrk_output.get('err_timeout')},"
        f"{wrk_output.get('req_sec_tot')},"
        f"{wrk_output.get('read_tot')}"
    )

def wrk_data_failed():
    return ',' + ','.join(['FAILED'] * 20)

def get_bytes(size_str):
    match = re.search(r"^(\d+\.?\d*)(\w+)$", size_str)
    if match is None:
        return size_str
    
    size = float(match.group(1))
    suffix = match.group(2).lower()

    suffix_multipliers = {
        'b': 1,
        'kb': 1024, 'kib': 1024,
        'mb': 1024 ** 2, 'mib': 1024 ** 2,
        'gb': 1024 ** 3, 'gib': 1024 ** 3,
        'tb': 1024 ** 4, 'tib': 1024 ** 4,
        'pb': 1024 ** 5, 'pib': 1024 ** 5
    }

    return size * suffix_multipliers.get(suffix, False)


def get_number(number_str):
    match = re.search(r"^(\d+\.?\d*)(\w*)$", number_str)
    if match is None:
        return number_str
    
    size = float(match.group(1))
    suffix = match.group(2).lower()

    suffix_multipliers = {
        '': 1,   # No suffix
        'k': 1000,
        'm': 1000 ** 2,
        'g': 1000 ** 3,
        't': 1000 ** 4,
        'p': 1000 ** 5
    }

    return size * suffix_multipliers.get(suffix, 1)


def get_ms(time_str):
    match = re.search(r"^(\d+\.?\d*)(\w*)$", time_str)
    if match is None:
        return time_str
    
    size = float(match.group(1))
    suffix = match.group(2).lower()

    suffix_multipliers = {
        'us': 1 / 1000,
        'ms': 1,
        's': 1000,
        'm': 1000 * 60,
        'h': 1000 * 60 * 60,
        '': 1  # No suffix
    }

    return size * suffix_multipliers.get(suffix, 1)


#    Thread Stats   Avg      Stdev     Max   +/- Stdev
#      Latency     6.46ms    6.12ms 132.38ms   91.26%
#      Req/Sec     0.90k   318.35     1.54k    66.28%
#    107960 requests in 1.00m, 129.13MB read
#  Requests/sec:   1797.63
#  Transfer/sec:      2.15MB

def parse_wrk_output(wrk_output):
    retval = {}

    for line in wrk_output.splitlines():
        logger.debug("wrk output: " + line)
        x = re.search("^\s+Latency\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*).*$", line)
        if x is not None:
            retval['lat_avg'] = get_ms(x.group(1))
            retval['lat_stdev'] = get_ms(x.group(2))
            retval['lat_max'] = get_ms(x.group(3))
        x = re.search("^\s+Req/Sec\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*).*$", line)
        if x is not None:
            retval['req_avg'] = get_number(x.group(1))
            retval['req_stdev'] = get_number(x.group(2))
            retval['req_max'] = get_number(x.group(3))
        x = re.search("^\s+(\d+)\ requests in (\d+\.\d+\w*)\,\ (\d+\.\d+\w*)\ read.*$", line)
        if x is not None:
            retval['tot_requests'] = get_number(x.group(1))
            retval['tot_duration'] = get_ms(x.group(2))
            retval['read'] = get_bytes(x.group(3))
        x = re.search("^Requests\/sec\:\s+(\d+\.*\d*).*$", line)
        if x is not None:
            retval['req_sec_tot'] = get_number(x.group(1))
        x = re.search("^Transfer\/sec\:\s+(\d+\.*\d*\w+).*$", line)
        if x is not None:
            retval['read_tot'] = get_bytes(x.group(1))
        x = re.search(
            "^\s+Socket errors:\ connect (\d+\w*)\,\ read (\d+\w*)\,\ write\ (\d+\w*)\,\ timeout\ (\d+\w*).*$", line)
        if x is not None:
            retval['err_connect'] = get_number(x.group(1))
            retval['err_read'] = get_number(x.group(2))
            retval['err_write'] = get_number(x.group(3))
            retval['err_timeout'] = get_number(x.group(4))
    if 'err_connect' not in retval:
        retval['err_connect'] = 0
    if 'err_read' not in retval:
        retval['err_read'] = 0
    if 'err_write' not in retval:
        retval['err_write'] = 0
    if 'err_timeout' not in retval:
        retval['err_timeout'] = 0
    return retval


def get_java_process_pid():
    cmd = 'ps -o pid,sess,cmd afx | egrep "( |/)java.*-SNAPSHOT.*\.jar.*( -f)?$" | awk \'{print $1}\''
    output = subprocess.getoutput(cmd)
    return output


def start_java_process(java_cmd, cpuset):
    cmd = 'taskset -c ' + cpuset + ' ' + java_cmd
    subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(wait_to_start)
    logger.info('Executing command: ' + cmd)
    return get_java_process_pid()


def execute_test_single(cpuset, threads, concurrency, duration):
    logger.info('Executing test with concurrency: ' + str(concurrency) + ', Duration: ' + str(duration) + ', Threads: ' + str(threads))
    cmd = 'taskset -c ' + str(cpuset) + ' ' + wrkcmd + ' --timeout ' + wrktimeout + ' -d' + str(duration) + 's -c' + str(concurrency) + ' -t' + str(threads) + ' ' + test_URL
    process = subprocess.run(cmd.split(' '), check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    logger.debug('Executing test command ' + cmd)
    logger.info('Executing test done')
    return output


def kill_process(pid):
    logger.info('Killing process with PID: ' + pid)
    try:
        os.kill(int(pid), signal.SIGKILL)
    except:
        logger.info('Process not found')
    try:
        # this will fail if the process is not a childprocess
        os.waitpid(int(pid), 0)
    except:
        # Just to be sure the process is really gone
        time.sleep(wait_after_kill)
    return

def validate_files_exist():
    resval = True
    for jarfile in jarfiles:
        filename = jarfile.get('filename')
        if not os.path.isfile(filename):
            print(f'File not found: {filename}')
            resval = False
    return resval

def build_jvmcmd(jar):
    return javacmd + ' ' + '-jar ' + jar


def get_user_cpuusage(pid):
    cmd = 'cat /proc/' + pid + '/stat | cut -d \' \' -f 14'
    output = (subprocess.getoutput(cmd)).replace(' ', ',')
    return output


def get_kern_cpuusage(pid):
    cmd = 'cat /proc/' + pid + '/stat | cut -d \' \' -f 15'
    output = (subprocess.getoutput(cmd)).replace(' ', ',')
    return output

def get_mem_kb_pss(pid):
    cmd = 'cat /proc/' + pid + '/smaps | grep -i pss | awk \'{Total+=$2} END {print Total}\''
    output = (subprocess.getoutput(cmd)).replace(' ', '')
    return ',' + output


def get_mem_kb_rss(pid):
    cmd = 'cat /proc/' + pid + '/smaps | grep -i rss | awk \'{Total+=$2} END {print Total}\''
    output = (subprocess.getoutput(cmd)).replace(' ', '')
    return ',' + output


def get_mem_kb_uss(pid):
    cmd = 'cat /proc/' + pid + '/smaps | grep -i Private | awk \'{Total+=$2} END {print Total}\''
    output = (subprocess.getoutput(cmd)).replace(' ', '')
    return ',' + output


def estimate_duration(num_jarfiles, num_concurrency_levels, test_duration, primer_duration, wait_after_primer, wait_to_start):
    total_iterations = num_jarfiles * num_concurrency_levels
    total_duration = total_iterations * (test_duration + primer_duration + wait_after_primer + wait_to_start)
    return total_duration / 60 / 60  # convert total duration to hours

def get_cpu_num(cpuset):
    return len(cpuset.split(','))

def insert_header(file):
    file.write('description,asyncservice,asyncdriver,cpus_load,cpus_service,concurrency,lat_avg,lat_stdev,lat_max,req_avg,req_stdev,req_max,tot_requests,tot_duration,read,err_connect,err_read,err_write,err_timeout,req_sec_tot,read_tot,user_cpu,kern_cpu,mem_kb_uss,mem_kb_pss,mem_kb_rss,duration\n')
