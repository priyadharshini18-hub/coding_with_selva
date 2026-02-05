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

class LogProcessor:

	def __init__(self) :
		self.count = 0
		self.error_count = 0
		self.client_error = defaultdict(int)
		self.server_error = defaultdict(int)
		self.endpoint_error_count = defaultdict(int)

	def read_file(self, file_directory) :

		for f in file_directory.glob('access*.log') :

			with open(f, 'r') as file:
			    for line in file:

			        self.count += 1 # Total number of requests

			        # 191.162.100.1 [2026-01-21:15:20:13.174982-08:00] "POST /api/order HTTP/1.1" 200
			        ip, timestamp, method, endpoint, protocol, return_code = line.split(' ')

			        return_code = int(return_code)

			        # Parse Timestamp
			        date, hour, minute, sec, _ = timestamp.strip('[]').split(':')
			        hour, minute, sec = int(hour), int(minute), int(sec.split('.')[0])
			        year, month, day = map(int, date.split('-'))

			        # Check if server/ client error
			        if 500 <= return_code < 600 :
			        	self.server_error[(year, month, day, hour, minute, sec)] += 1 
			        	self.error_count += 1
			        	self.endpoint_error_count[endpoint] += 1

			        elif 400 <= return_code < 500 :
			        	self.client_error[(year, month, day, hour, minute, sec)] += 1 
			        	self.error_count += 1
			        	self.endpoint_error_count[endpoint] += 1

	def get_top_k_endpoints(self, k) :
		top_k = []
		
		if len(self.endpoint_error_count) < k :
			print('Not enough endpoints!')
			return top_k
		
		sorted_endpt_error_count = sorted(self.endpoint_error_count.items(), key=lambda x:x[1], reverse=True)

		for i in range(k):
			top_k.append(sorted_endpt_error_count[i][0])

		return top_k


	def get_errors_in_time_range(self, start, end, errors) :
		error_cnt = 0
		for key, val in errors.items() :
			if start <= key <= end :
				error_cnt += val

		return error_cnt

lp = LogProcessor()

file_directory = Path('logs')
lp.read_file(file_directory)

print('Total number of requests: Expected=30 Actual=', lp.count)

print('Total number of errors: Expected=12 Actual=', lp.error_count)

top_k_endpts = lp.get_top_k_endpoints(k=2)
print('Top 2 endpoints with errors:', top_k_endpts)

# Number client errors between start and endtime
# Input can't have leading zeros like 01
start = (2026, 1, 21, 16, 25, 00)
end = (2026, 1, 21, 16, 35, 00)
client_error_count = lp.get_errors_in_time_range(start, end, lp.client_error)
print('Number client errors between start and endtime:', client_error_count)


# Number server errors between start and endtime
server_error_count = lp.get_errors_in_time_range(start, end, lp.server_error)
print('Number server errors between start and endtime:', server_error_count)
