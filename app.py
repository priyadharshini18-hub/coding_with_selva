# Read all access logs from logs directory and answer the following questions

# 1. Total number of requests
# 2. Number of errors
# 3. Top k endpoints with errors
# 4. Number client errors between start and endtime
# 5. Number server errors between start and endtime

# 191.162.100.1 [2026-01-21:15:20:13.174982-08:00] "POST /api/order HTTP/1.1" 200
# 191.162.100.1 [2026-01-21:15:25:13.174982-08:00] "POST /api/order HTTP/1.2" 400
# 191.162.100.1 [2026-01-21:15:30:13.174982-08:00] "POST /api/order HTTP/1.1" 500
# 191.162.100.100 [2026-01-21:16:40:13.174982-08:00] "POST /api/auth HTTP/1.1" 200
# 191.162.100.100 [2026-01-21:16:50:13.174982-08:00] "POST /api/checkout HTTP/1.1" 200

from collections import defaultdict
import heapq
import glob
from pathlib import Path

count = 0
error_count = 0
client_error = defaultdict(int)
server_error = defaultdict(int)
endpoint_error_count = defaultdict(int)


# Open the file and iterate through each line
# files = []
# for i in range(6):
# 	files.append('access'+str(i)+'.log')

def read_file() :
	global count, error_count
	file_directory = Path('logs')

	for f in file_directory.glob('access*.log') :

		with open(f, 'r') as file:
		    for line in file:

		        count += 1 # Total number of requests

		        # 191.162.100.1 [2026-01-21:15:20:13.174982-08:00] "POST /api/order HTTP/1.1" 200
		        ip, timestamp, method, endpoint, protocol, return_code = tuple(line.split(' ')) 
		        
		        # print('ip=', ip) # 191.162.100.1
		        # print('time=', timestamp) # [2026-01-21:15:20:13.174982-08:00]
		        # print('method=', method) # "POST
		        # print('endpoint=', endpoint) # /api/order
		        # print('protocol=', protocol) # HTTP/1.1"
		        # print('return_code=', return_code) # 200


		        return_code = int(return_code)

		        # Parse Timestamp
		        date, hour, minute, sec, _ = tuple(timestamp.strip('[]').split(':'))
		        hour, minute, sec = int(hour), int(minute), int(sec.split('.')[0])
		        year, month, day = map(int, date.split('-'))

		        # print('year=', year) # 2026
		        # print('month=', month) # 01
		        # print('day=', day) # 21
		        # print('hour=', hour) # 15
		        # print('minute=', minute) # 20
		        # print('sec=', sec) # 30
		        

		        # Check if server/ client error
		        if 500 <= return_code < 600 :
		        	server_error[(year, month, day, hour, minute, sec)] += 1 
		        	error_count += 1
		        	endpoint_error_count[endpoint] += 1

		        elif 400 <= return_code < 500 :
		        	client_error[(year, month, day, hour, minute, sec)] += 1 
		        	error_count += 1
		        	endpoint_error_count[endpoint] += 1

def get_top_k_endpoints(k) :
	if len(endpoint_error_count) < k :
		print('Not enough endpoints!')
		return
	sorted_endpt_error_count = sorted(endpoint_error_count.items(), key=lambda x:x[1], reverse=True)

	print('Top k endpoints with errors:')
	for i in range(k):
		print(sorted_endpt_error_count[i][0])


def get_errors_in_time_range(start, end, errors) :
	error_count = 0
	for key, val in errors.items() :
		if start <= key <= end :
			error_count += val

	return error_count

read_file()

print('Total number of requests:', count)

print('Total number of errors:', error_count)

get_top_k_endpoints(2)

# Number client errors between start and endtime
# Input can't have leading zeros like 01
start = (2026, 1, 21, 16, 25, 00)
end = (2026, 1, 21, 16, 35, 00)
client_error_count = get_errors_in_time_range(start, end, client_error)
print('Number client errors between start and endtime:', client_error_count)


# Number server errors between start and endtime
server_error_count = get_errors_in_time_range(start, end, server_error)
print('Number server errors between start and endtime:', server_error_count)
