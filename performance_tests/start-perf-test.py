from config import logger
from config import resultsfile
from config import load_generator_cpuset, service_cpuset
from config import concurrency_levels
from config import jarfiles
from config import test_duration, primer_duration, wait_after_primer, wait_to_start, wrktimeout
from config import wrkcmd, test_URL
import utils as u
import subprocess
import time

def start_perf_tests():
    logger.info(f'The estimated duration of the performance tests is: {u.estimate_duration(len(jarfiles), len(concurrency_levels), test_duration, primer_duration, wait_after_primer, wait_to_start)} hours')
    logger.info(f'The results will be saved in the logfile: {resultsfile}')

    cpuset_load = load_generator_cpuset[0]
    cpuset_service = service_cpuset[0]
    
    cpunum_load = str(u.get_cpu_num(cpuset_load))
    cpunum_service = str(u.get_cpu_num(cpuset_service))

    concurrency_local = [concurrency for concurrency in concurrency_levels if int(concurrency) >= int(cpunum_load)]
   
    with open(resultsfile, 'a') as results_file:
        u.insert_header(results_file)
    for jarfile in jarfiles:
        jvmcmd = u.build_jvmcmd(jarfile.get('filename'))
        logger.info(f'Processing command: {jvmcmd}')
        logger.info(f'Number of CPUs allocated for load generation: {cpunum_load}')    
        logger.info(f'Number of CPUs allocated for service: {cpunum_service}')
        for concurrency in concurrency_local:
            jvm_outputline = jarfile.get('description') + ',' + jarfile.get('asyncservice') + ',' + jarfile.get('asyncdriver') + ',' + cpunum_load + ',' + cpunum_service + ',' + concurrency
            logger.info(f'Number of concurrent requests: {concurrency}')

            pid = u.start_java_process(jvmcmd, cpuset_service)
            logger.info(f'Java process PID is: {pid}')

            try:
                output_primer = execute_test_single(cpuset_load, cpunum_load, concurrency, primer_duration)
                time.sleep(wait_after_primer)
                cpu_user_before = u.get_user_cpuusage(pid)
                cpu_kern_before = u.get_kern_cpuusage(pid)
                output_test = execute_test_single(cpuset_load, cpunum_load, concurrency, test_duration)
                cpu_user_after = u.get_user_cpuusage(pid)
                cpu_kern_after = u.get_kern_cpuusage(pid)
                wrk_output = u.parse_wrk_output(output_test)
                logger.debug("wrk_output: " + str(wrk_output))
                if str(wrk_output.get('read_tot')) == '0.0':
                    raise Exception('No bytes read. Test failed.')
                cpu_and_mem = u.get_cpu_and_memory(pid, cpu_user_before, cpu_user_after, cpu_kern_before, cpu_kern_after)
                logger.info('CPU and memory: ' + cpu_and_mem)
                outputline = jvm_outputline + u.wrk_data(wrk_output) + cpu_and_mem
            except Exception as inst:
                logger.warning("Test failed. Writing 'FAILED' status to the results file.")
                logger.error("Error: " + str(inst))
                outputline = jvm_outputline + u.wrk_data_failed()

            outputline = outputline + ',' + str(test_duration)
            with open(resultsfile, 'a') as results_file:
                results_file.write(outputline + '\n')
            u.kill_process(pid)
    return

def execute_test_single(cpuset, threads, concurrency, duration):
    logger.info('Executing test with Concurrency: ' + str(concurrency) + ', Duration: ' + str(duration) + ', Threads: ' + str(threads))
    cmd = 'taskset -c ' + str(cpuset) + ' ' + wrkcmd + ' --timeout ' + wrktimeout + ' -d' + str(duration) + 's -c' + str(concurrency) + ' -t' + str(threads) + ' ' + test_URL
    process = subprocess.run(cmd.split(' '), check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    logger.debug('Executing test command: ' + cmd)
    logger.info('Executing test done')
    return output


def main():
    if not u.validate_files_exist():
        logger.error('Requirements not satisfied. Exiting')
        exit(1)
    else:
        logger.info('Requirements satisfied')

    print(start_perf_tests())
    logger.info('Test execution finished')


if __name__ == '__main__':
    main()