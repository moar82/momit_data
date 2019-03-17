######Autor: Rodrigo Morales
######This script measure peformance metric of executing an embeded js interpreter with duktape default config. options in terms of
###### of memory, code size and execution time
###### 30 times to have statisticall signficance on execution times
######updated to read configuration from file uses python 3
#!/usr/bin/env python
import csv, os, sys, subprocess, time,  configparser
from collections import deque



class BenchmarkConfiguration ():
    ''' Here we read the configuration from a text file
        TODO: Add the properties of each device:memory capacity, storage capacity
        '''
    def __init__(self) -> None:
        super().__init__()
        '''if there is not  configuration file we create a new one'''
        if os.path.isfile('config_benchmark_on_original.ini') == False:
            self.create_default_configuration_file()
        self.read_configuration_file()

    def create_default_configuration_file(self):
        config = configparser.ConfigParser()
        config['DUKTAPE.OPTIONS'] = {'dukpath':'/home/moar82/duktape-2.3.0'}
        config['PROGRAM.TO.TEST'] = {#'experiment_name':'mandel',
                                    'idf':'default',
                                     'device':'laptop',
                                     'program':'harness',
                                     #'script':'mandel.js',
                                     'jsfunction':'forTest',
                                     'runs':'10'
                                     }
        with open('config_benchmark_on_original.ini', 'w') as configfile:
            config.write(configfile)
    def read_configuration_file(self):
        config = configparser.ConfigParser()
        config.read('config_benchmark_on_original.ini')
        self.duk_path =  config['DUKTAPE.OPTIONS']['dukpath']
        #self.experiment_name = config['PROGRAM.TO.TEST']['experiment_name']
        self.idf = config['PROGRAM.TO.TEST']['idf']
        self.device_benchmarked = config['PROGRAM.TO.TEST']['device']
        self.program = config['PROGRAM.TO.TEST']['program']
        #self.script = config['PROGRAM.TO.TEST']['script']
        self.jsfunction = config['PROGRAM.TO.TEST']['jsfunction']
        self.runs = config['PROGRAM.TO.TEST']['runs']

    def fitem(item):
        item = item.strip()
        try:
            item = float(item)
        except ValueError:
            pass
        return item

if len(sys.argv)<2:
	print ('you should provide one argument for the .js file to benchmark!')
	sys.exit()

script = sys.argv[1]
experiment_name = sys.argv[1].split('.')[0]
bc = BenchmarkConfiguration()
cwd = os.getcwd()  #do not change
idf = bc.idf
device = bc.device_benchmarked
program = bc.program
jsfunction = bc.jsfunction #name of the js function to execute
report_file="results_original_" + idf + "_" + experiment_name+ ".csv"
logFile = cwd+"/logbenchmarkOrg" + "_" + experiment_name+ ".log"
duk_path = bc.duk_path

#####format of the csv output file
# device, program,run, id, value, feature_size, mem_us,  time_usr, time_sys, cpu_perc
### where device is the device where we run the tests
### program is the script executed
### run is the number of run.  This is important since the user time may vary from run to run
### id: NA
### feature_size is the difference of  linux command filestat -c from the compiled code with default parameters
#############and the js interpreter compiled with the id feature
###mem_us is reported by time linux command
###time_usr Total number of CPU-seconds that the process spent in user mode. 
###time_sys is reported by time linux command: Total number of CPU-seconds that the process spent in kernel mode. 
###cpu_perc  Percentage of the CPU that this job got, computed as (%U + %S) / %E. 

### The best would be to create a file to parametrize the following values
### to compute the deltas
# for hello.c file
file_size_org = 0 # do not modify
num_of_runs = 10

def logError (logmessage):
	flog = open (logFile,"a")
	flog.write (logmessage)
	flog.close()
	return

now = time.strftime("%c")
print (now)
logError(now+"\n")
start_time = time.time()


#try:
os.chdir(cwd) ##always start in the original directory
###we save the new options file 
os.system('mkdir -p '+cwd + '/duktape-src/'+idf)
os.system ('cp -f ' + duk_path +'/src/* ' + \
	cwd + '/duktape-src/'+idf+ '/')
###Copy the source code, since I have problems when compiling when the headers are in a different dir
###Now the next step is to compile the code 
os.system('cp -f ' +cwd + '/{' +program+'.c,' + script + '} ' + cwd + '/duktape-src/'+idf+ '/')
os.chdir(cwd + '/duktape-src/'+idf+ '/')
os.system('gcc -std=c99 -o '+ program+ ' -Iduktape-src duktape.c ' + program + '.c -lm')
####Now let's measure the size of the file
returned_out = subprocess.check_output (["stat", "-c", "\"%s\" ",  cwd + '/duktape-src/'+idf+ '/' + program ])
#print (returned_out.decode("utf-8").strip())
file_size_org = int(str(returned_out.decode("utf-8")).strip().replace("\"",""))
####Let's execute it to measure memory and time
####because there is a problem with the way time works
time_lines_count = 1 # how many lines /usr/bin/time produces
freportout = open (cwd+"/"+report_file,"a")
header = ['device', 'program','run', 'id', 'value', 'feature_size', 'mem_us',  'time_usr', 'time_sys', 'cpu_perc']
writer=csv.writer(freportout,quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(header)
for count in range (0, num_of_runs):
	print ('Feature: %s. Run number: %d' %(idf,count))
	print ('./'+program+ ' ' + script + ' '  + jsfunction)
	p = subprocess.Popen(['/usr/bin/time', '-f \" %U , %S , %P\"' ,'./'+program, script,jsfunction]\
		, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	with p.stdout:
		r = deque(iter(p.stdout.readline, b''), maxlen=time_lines_count)
	with p.stderr:
	    q = deque(iter(p.stderr.readline, b''), maxlen=time_lines_count)
	rc = p.wait()
	coltemp = str(b''.join(r).decode().strip()).split(',') + str(b''.join(q).decode().strip()).split(',')
	print (coltemp)
	parsed = False
	try:
		memory_us = int(coltemp[0].replace("\"","").strip())
		parsed=True
	except:
		logError("When executing program: "+ program + ". feature test: "+ idf + ". errorMsg: " + coltemp[0].replace("\"","").strip()+"\n")
		continue
###let's append results to file
	filerow = [device,program,count,idf,'NA',file_size_org,coltemp[0].replace("\"","").strip()\
	,coltemp[1].replace("\"","").strip(),coltemp[2].replace("\"","").strip(),coltemp[3].replace("\"","").strip()]
	writer.writerow(filerow)
freportout.close()
now = time.strftime("%c")
print (now)
logError("ended  " + now +"\n")
endTime = "--- %s seconds ---" % (time.time() - start_time)
print(endTime)
logError(endTime+"\n")
	
