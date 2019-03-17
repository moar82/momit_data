###### Autor: Rodrigo Morales
###### This script peform the benchmark for config options of duktape in terms
###### It is useful when you want to impact the effect of multiple features at the same time
###### of memory, code size and execution time for the duktape features provided in a separated file
###### parameters: configuration.yaml file (optional)  for example from duktapedir/config/examples/low_memory.yaml
###### if no parameters are provided, then you need to set the following variables: (filewithfeatures, features2TestFile)
import sys, csv, os, subprocess, time, configparser
from collections import deque

cwd = os.getcwd() #do not change

'''Read configuration settings '''
config = configparser.ConfigParser()
config.read('config_benchmark.ini')
dukpath = config['DUKTAPE.OPTIONS']['dukpath']
####These set values are only valid when no parameter is added to the call of the script
####The idea is to provide filewithfeatures, that contains the following features :
#######id,propertiy,default,activated in,value in,category
#######1,DUK_USE_ALLOW_UNDEFINED_BEHAVIOR,FALSE,low_memory.yaml,TRUE,Platform and portability options
filewithfeatures = config['USE.FEATURES.FILE']['filewithfeatures']
features2TestFile = config['USE.FEATURES.FILE']['features2TestFile'] ###the features we are interested to test
idf = features2TestFile.split('.')[0] # do not modify. name of the configuration file created with the features in "features2TestFile"

####When using  ROM built-in objects, it is necessary to provide an additional parameter to the python's duktape configuration tool
useROM=config['DUKTAPE.OPTIONS']['useROM']

####force to recompile
recompileDukTape = config['DUKTAPE.OPTIONS']['recompileDukTape']

device = config['PROGRAM.TO.TEST']['device']
program = config['PROGRAM.TO.TEST']['program'] #name of the c executable that embeds the JS engine
script  = config['PROGRAM.TO.TEST']['script'] #name of the script that we execute
print('Warning: running script ' + script + ' with selected config options')
jsfunction = config['PROGRAM.TO.TEST']['jsfunction'] #name of the js function to execute
num_of_runs = int (config['PROGRAM.TO.TEST']['runs'])
report_file="results_benchmark_"+ script.split(".")[0]+"_" + features2TestFile +".csv"
benchmark_file =   config['PROGRAM.TO.TEST']['prefix_benchmark_file'] + script.split('.')[0] + '.csv'

#####format of the csv output file
# device, program, id, value, feature_size, mem_us,  time_usr, time_sys, cpu_perc
### where device is the device where we run the tests
### program is the script executed
### id is the id column in the confopt tab in the google spreadsheet "Concordia Post-Doc research plan"
### value is the memory in bytes measured by mallinfo including the harness overhead
### feature_size is the difference of  linux command filestat -c from the compiled code with default parameters
#############and the js interpreter compiled with the id feature
###mem_us is reported by time linux command
###time_usr Total number of CPU-seconds that the process spent in user mode. 
###time_sys is reported by time linux command: Total number of CPU-seconds that the process spent in kernel mode. 
###cpu_perc  Percentage of the CPU that this job got, computed as (%U + %S) / %E. 

'''Read file output of benchmark project'''
with open (benchmark_file,'r') as pmeasurescsv:
    csvreader = csv.reader(pmeasurescsv)
    '''skip the header'''
    next(csvreader)
    for row in csvreader:
        file_size_org = float(row[0])
        mem_us_org = float(row[1])
        use_time_avg = float(row[2])


logFile = cwd+"/logbenchmark_"+ script.split(".")[0] + "_" + idf +".log"

feature_size = 0.00 # do not change
printheader = 1 # do not change
fileoutname = "" #do not change

def logError (logmessage):
	flog = open (logFile,"a")
	flog.write (logmessage)
	flog.close()
	return


def generateConffileFromIds():
	features2Test=[]##do not modify
	##First we need to open the filewithFeatures and file with solution
	with open (features2TestFile,'r') as txtfile:
		for line in txtfile:
			features2Test.append(str(line).strip())
	feature2TestwithValues =[] ##do not modify
	###Now search only the desired features on filewithfeatures
	print("features from solution file:",features2Test)
	with open (filewithfeatures) as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		next(readCSV)
		for row in readCSV:
			if len(row)>1:
				for ft in features2Test:
					if ft == row[0]: 		          	  
						feature_value = str(row[4]).lower()
						feature = row[1]+": "+ feature_value
						feature2TestwithValues.append(feature)
						break;
						print ("features parsed:",feature2TestwithValues)
	###we save the new options file 
	os.system('mkdir -p '+cwd + '/configFiles/'+idf)
	fileoutname = "configFiles/"+idf+"/"+idf+".yaml" 
	fout = open (fileoutname,"w")
	for feature in feature2TestwithValues:
		fout.write (feature + "\n")
	fout.close()
	return fileoutname


compileFrom_yamlFile = False

if len(sys.argv)>1:
	print ("Argument received: "+sys.argv[1])
	compileFrom_yamlFile = True
	filewithfeatures =sys.argv[1]
	features2TestFile=sys.argv[1] ###the features we are interested to test
	idf = sys.argv[1].split('.')[0] # do not modify. name of the configuration file created with the features in "features2TestFile"
	fileoutname =features2TestFile
	report_file="results_benchmark_"+ script.split(".")[0]+"_" + idf +".csv"
	logFile = cwd+"/logbenchmark_"+ script.split(".")[0] + "_" + idf +".log"
	#we proceed to compile based on the inputs file

else:
	fileoutname = generateConffileFromIds()

now = time.strftime("%c")
print (now)
logError(now+"\n")
logError("features file: "+ filewithfeatures +"\n")
start_time = time.time()

os.system('mkdir -p '+cwd + '/duktape-src/'+idf)
#print ('python /home/moar82/duktape-2.2.1/tools/configure.py --output-directory ' + cwd + '/duktape-src/'+idf+ ' --option-file ' + cwd +"/" + fileoutname)
###only if duktape.h does not exist
if recompileDukTape=='True':
	###duktape does not recompile if there are other files in the dir than the ones he produces
	###so we need to remove any file from the dir in advance
	os.system('rm ' + cwd + '/duktape-src/'+idf+'/*')
dukHeader=cwd + '/duktape-src/'+idf+'/duktape.h'
if os.path.isfile(dukHeader)==False:
	if useROM=='True':
		os.system ('python ' + dukpath  + '/tools/configure.py --output-directory ' + \
		cwd + '/duktape-src/'+idf+ ' --rom-support --option-file ' + cwd +"/" + fileoutname)
	else:
		os.system ('python ' + dukpath + '/tools/configure.py --output-directory ' + \
	 	cwd + '/duktape-src/'+idf+ ' --option-file ' + cwd +"/" + fileoutname)

###Copy the source code, since I have problems when compiling when the headers are in a different dir
###Now the next step is to compile the code 
os.system('cp -f ' +cwd + '/{' +program+'.c,' + script + '} ' + cwd + '/duktape-src/'+idf+ '/')
os.chdir(cwd + '/duktape-src/'+idf+ '/')
compileSucc = os.system('gcc -std=c99 -o '+ program+ ' -Iduktape-src duktape.c ' + program + '.c -lm')
if compileSucc!=0:
	logError("When compiling program: "+ program + ". features set: "+ features2TestFile + "\n")
	sys.exit()
####Now let's measure the size of the file
returned_out = subprocess.check_output (["stat", "-c", "\"%s\"", program ])
parsed = False
try:
	feature_size = float(returned_out.decode("utf-8").replace("\"","").strip())
	parsed = True
except ValueError:
	#here we should log an error with the correspoding feature
	logError("When measuring file size: "+ program + ". features set: "+ features2TestFile + ". errorMsg: " + returned_out.decode("utf-8").replace("\"","").strip()+"\n")
	sys.exit()
feature_size_delta = (feature_size - file_size_org) / file_size_org
size_diff = file_size_org - feature_size
####Let's execute it to measure memory and time
time_lines_count = 1 # how many lines /usr/bin/time produces
freportout = open (cwd+'/'+report_file,"a")
header = ['device', 'program', 'run', 'id', 'feature_size', 'mem_us',  'time_usr', 'time_sys',\
 'cpu_perc', 'size_delta', 'mem_delta','time_delta','size_diff', 'mem_diff','time_diff' ]
writer=csv.writer(freportout,quoting=csv.QUOTE_NONNUMERIC)
if printheader==1:
	writer.writerow(header)
	printheader = 0
for count in range (0, num_of_runs):
	print ('Configuration File: %s. Run number: %d' %(idf,count))
	p = subprocess.Popen(['/usr/bin/time', '-f \" %U , %S , %P\"',\
		'./'+ program, script , jsfunction], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	with p.stdout:
	  	r = deque(iter(p.stdout.readline, b''), maxlen=time_lines_count)
	with p.stderr:
	    q = deque(iter(p.stderr.readline, b''), maxlen=time_lines_count)
	rc = p.wait()
	#print(b''.join(q).decode().strip())
	coltemp = str(b''.join(r).decode().strip()).split(',') + str(b''.join(q).decode().strip()).split(',')
	###let's append results to file
	#os.chdir(cwd)
	print (coltemp)
	try:
		memory_us = float(coltemp[0].replace("\"","").strip())
		parsed=True
	except:
		logError("When executing program: "+ program + ". features set: "+ features2TestFile + ". errorMsg: " + coltemp[0].replace("\"","").strip()+"\n")
		continue
	mem_diff =  mem_us_org - memory_us
	memory_us_delta=(memory_us-mem_us_org)/mem_us_org
	time_us = float(coltemp[1].replace("\"","").strip())
	time_diff = use_time_avg - time_us
	if use_time_avg!=0:
		time_delta = (time_us-use_time_avg)/use_time_avg
	else:
		time_delta = 0
	filerow = [device,program,count,idf,feature_size,coltemp[0].replace("\"","").strip(), \
	 coltemp[1].replace("\"","").strip(),coltemp[2].replace("\"","").strip(),coltemp[3].replace("\"","").strip(),feature_size_delta,memory_us_delta,time_delta,\
	 size_diff,mem_diff,time_diff]
	writer.writerow(filerow)
freportout.close()
		# except OSError as err:
		# 		print("OS error: {0}".format(err))
		# except ValueError:
		# 		print("Could not convert data to an integer.")
		# except:
		# 		print("Unexpected error:", sys.exc_info()[0])
	
now = time.strftime("%c")
print (now)
logError("ended " + now +"\n")
endTime = "--- %s seconds ---" % (time.time() - start_time)
print(endTime)
logError(endTime+"\n")
	
''' Configuration ini example '''
''' Do not delete '''
# [DUKTAPE.OPTIONS]
# dukpath = /home/moar82/duktape-2.3.0
# useROM = True
# recompileDukTape = True
# [USE.FEATURES.FILE]  ''' This section is only valid when you do not provide parameters (e.g., using a number
# of feature from filewithfeatures based on combinedTopMemorySavingFeatures.txt) '''
# filewithfeatures = confOpt.csv
# features2TestFile = combinedTopMemorySavingFeatures.txt
# [PROGRAM.TO.TEST]
# idf = optimize
# device = laptop
# program = harness
# jsfunction = .
# script = crypto-aes.js
# runs = 10
# prefix_benchmark_file = median_results_original_default_ ''' this file contains the measurement
# of running the same script using default duktape values, generated using runBenchmarkOnOriginal.py '''
