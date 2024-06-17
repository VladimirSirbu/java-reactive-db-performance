import logging
from datetime import datetime

##########################################################################################################

# I/O
resultsfile = 'reporting/results/results_' + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + '.log'
outputfile = 'reporting/output/output_' + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + '.log'

##########################################################################################################

# LOGGING
logger = logging.getLogger('start-perf-test')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fh = logging.FileHandler(outputfile)
fh.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(fh)

##########################################################################################################

# CPU
load_generator_cpuset = ['3,5']
service_cpuset = ['2,4']
# 0 and 1 CPU cores is alocated for PostgreSQL database, see the file: /docker-services/docker-compose.yml

##########################################################################################################

# Concurrency
concurrency_levels = ['10', '20', '30', '40', '50', '60', '70', '80', '90', '100']

##########################################################################################################

# JARs path
jarfiles = [     {'filename': 'jars/WEB_MVC_JDBC-0.0.1-SNAPSHOT.jar',
                  'description': 'Web MVC JDBC',
                  'asyncservice': 'no',
                  'asyncdriver': 'no'},
                 {'filename': 'jars/WEB_FLUX_R2DBC-0.0.1-SNAPSHOT.jar',
                  'description': 'WebFlux R2DBC',
                  'asyncservice': 'yes',
                  'asyncdriver': 'yes'},
                 {'filename': 'jars/WEB_MVC_R2DBC-0.0.1-SNAPSHOT.jar',
                  'description': 'Web MVC R2DBC',
                  'asyncservice': 'no',
                  'asyncdriver': 'yes'},
                 {'filename': 'jars/WEB_FLUX_JDBC-0.0.1-SNAPSHOT.jar',
                  'description': 'WebFlux JDBC',
                  'asyncservice': 'yes',
                  'asyncdriver': 'no'},
                 {'filename': 'jars/quarkus-r2dbc-1.0.0-SNAPSHOT-runner.jar',
                  'description': 'Quarkus_R2DBC',
                  'asyncservice': 'yes',
                  'asyncdriver': 'yes'},
                 {'filename': 'jars/VertX_PG_client-1.0.0-SNAPSHOT-fat.jar',
                  'description': 'VertX_PG_client',
                  'asyncservice': 'yes',
                  'asyncdriver': 'yes'}]

##########################################################################################################

# Test configuration
test_duration = 60  # Duration of a single test in seconds
primer_duration = 2  # Duration of the primer phase in seconds
wait_after_primer = 1  # Wait time after primer phase in seconds
wait_to_start = 10  # Wait time before starting the test in seconds
wait_after_kill = 2  # Wait time after killing a process in seconds

# Command configurations
javacmd = '/usr/lib/jvm/java-11-openjdk-amd64/bin/java -Xmx2g -Xms2g'
wrkcmd = 'wrk'
wrktimeout = '20s'

# URL on which requests will be made
test_URL = 'http://localhost:8080/student/all'