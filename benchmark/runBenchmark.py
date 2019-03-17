######Autor: Rodrigo Morales
######This script peform the benchmark for config options of duktape in terms
###### of memory, code size and execution time
######It is useful when you want to measure the impact of a set of features separately
import sys, csv, os, subprocess, time
from collections import deque

cwd = os.getcwd() #do not change
filewithfeatures ='confOpt_timeAndPerformance.csv'
feature = "" #do not change
idf = "" #do not change
#fileoutname ="" #name of the configuration file
device ="laptop"
program ="harness" #name of the c executable that embeds the JS engine
script  ="primeSimple.js" #name of the script that we execute
jsfunction = "forTest" #name of the js function to execute
report_file="results_benchmark_primeSimple"+ filewithfeatures.split(".")[0] + ".csv"
####When using  ROM built-in objects, it is necessary to provide an additional parameter to the python's duktape configuration tool
useROM=False
####force to recompile
recompileDukTape = True

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

### The best would be to create a file to parametrize the following values
### to compute the deltas
# for hello.c file
file_size_org = 555896.00 #B
mem_us_org = 104816.00 #B
use_time_avg =0.82 #in seconds, median for the original system
num_of_runs = 10
logFile = cwd+"/logbenchmark_primeSimple" + filewithfeatures.split(".")[0] +".log"


feature_size = 0.00 # do not change
printheader = 1 # do not change

def logError (logmessage):
	flog = open (logFile,"a")
	flog.write (logmessage)
	flog.close()
	return

now = time.strftime("%c")
print (now)
logError(now+"\n")
logError("features file: "+ filewithfeatures +"\n")
start_time = time.time()

with open (filewithfeatures) as csvfile:
	readCSV = csv.reader(csvfile, delimiter=',')
	next(readCSV)###to skip the header
	for row in readCSV:
        # in this case we will start measuring properties related to
        # ecma5
	    if len(row)>1:
	    	#try:
				if 1==1:#"ECMAScript" not in row[5]: ##this if can only be valid if we want to analyze certain features
	          	  ###we need to run 30 times to record time
					os.chdir(cwd) ##always start in the original directory
					feature_value = str(row[4]).lower()
					feature = row[1]+": "+ feature_value
					idf = row[0]
					###we save the new options file 
					os.system('mkdir -p '+cwd + '/configFiles/'+idf)
					fileoutname = "configFiles/"+idf+"/"+idf+".yaml" 
					fout = open (fileoutname,"w")
					fout.write (feature)
					fout.close()
					os.system('mkdir -p '+cwd + '/duktape-src/'+idf)
					#print ('python /home/moar82/duktape-2.2.1/tools/configure.py --output-directory ' + cwd + '/duktape-src/'+idf+ ' --option-file ' + cwd +"/" + fileoutname)
					if recompileDukTape==True:
						###duktape does not recompile if there are other files in the dir than the ones he produces
						###so we need to remove any file from the dir in advance
						os.system('rm ' + cwd + '/duktape-src/'+idf+'/*')
					###only if duktape.h does not exist
					dukHeader=cwd + '/duktape-src/'+idf+'/duktape.h'
					if os.path.isfile(dukHeader)==False:
						if useROM==False:
							os.system ('python /home/moar82/duktape-2.2.1/tools/configure.py --output-directory ' + \
								cwd + '/duktape-src/'+idf+ ' --option-file ' + cwd +"/" + fileoutname)
						else:
							os.system ('python /home/moar82/duktape-2.2.1/tools/configure.py --output-directory ' + \
							cwd + '/duktape-src/'+idf+ ' --rom-support --option-file ' + cwd +"/" + fileoutname)
					###Copy the source code, since I have problems when compiling when the headers are in a different dir
					###Now the next step is to compile the code 
					os.system('cp -f ' +cwd + '/{' +program+'.c,' + script + '} ' + cwd + '/duktape-src/'+idf+ '/')
					os.chdir(cwd + '/duktape-src/'+idf+ '/')
					compileSucc = os.system('gcc -std=c99 -o '+ program+ ' -Iduktape-src duktape.c ' + program + '.c -lm')
					if compileSucc!=0:
						continue
					####Now let's measure the size of the file
					returned_out = subprocess.check_output (["stat", "-c", "\"%s\"", program ])
					parsed = False
					try:
						feature_size = float(returned_out.decode("utf-8").replace("\"","").strip())
						parsed = True
					except ValueError:
						#here we should log an error with the correspoding feature
						logError("When compiling program: "+ program + ". feature test: "+ feature + ". errorMsg: " + returned_out.decode("utf-8").replace("\"","").strip()+"\n")
						continue
					feature_size_delta = (feature_size - file_size_org) / file_size_org
					size_diff = file_size_org - feature_size
					####Let's execute it to measure memory and time
					time_lines_count = 1 # how many lines /usr/bin/time produces
					freportout = open (cwd+'/'+report_file,"a")
					header = ['device', 'program', 'run', 'id', 'value', 'feature_size', 'mem_us',  'time_usr', 'time_sys',\
					 'cpu_perc', 'size_delta', 'mem_delta','time_delta','size_diff', 'mem_diff','time_diff' ]
					writer=csv.writer(freportout,quoting=csv.QUOTE_NONNUMERIC)
					if printheader==1:
						writer.writerow(header)
						printheader = 0
					for count in range (0, num_of_runs):
						print 'Feature: %s. Value: %s. Run number: %d' %(idf,feature_value,count)
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
						print coltemp
						try:
							memory_us = float(coltemp[0].replace("\"","").strip())
							parsed=True
						except:
							logError("When executing program: "+ program + ". feature test: "+ feature + ". errorMsg: " + coltemp[0].replace("\"","").strip()+"\n")
							continue
						mem_diff =  mem_us_org - memory_us
						memory_us_delta=(memory_us-mem_us_org)/mem_us_org
						time_us = float(coltemp[1].replace("\"","").strip())
						time_diff = use_time_avg - time_us
						if use_time_avg!=0:
							time_delta = (time_us-use_time_avg)/use_time_avg
						else:
							time_delta = 0
						filerow = [device,program,count,idf,feature_value,feature_size,coltemp[0].replace("\"","").strip(), \
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
	
