"""
A handy script for extracting all events from a particular year 
from an ICS file into another ICS file.

@author Derek Ruths (druths@networkdynamics.org)

Adjusted by Andre Strobel to process one year in a function
"""

import argparse
import re
import sys, os

def ics_splitter_year(year, input_file, max_events_per_file):
	
	input_file_path, input_file_name = os.path.split(input_file)
	input_file_base, input_file_ext = os.path.splitext(input_file_name)
	output_file_base = input_file_base + "_" + str(year)
	output_directory = os.path.join(input_file_path, input_file_base)
	if not os.path.exists(output_directory):
		os.mkdir(output_directory)
	
	print("===================")
	if not year == "all":
		print("Year %d:" % (year))
	print("Max events per file %d:" % (max_events_per_file))
	print("Extracting %s events from %s" % (year,input_file))
	
	# created_pattern = re.compile('^DTSTART.+%s' % year)
	created_pattern = re.compile('^DTSTART.+:%s' % year)

	# print("%s\n%s\n%s\n%s" % (input_file, input_file_path, input_file_base, input_file_ext))
	# infh = open(input_file, 'r', encoding="Latin-1")
	infh = open(input_file, 'r', encoding="utf8")

	# parsing constants
	BEGIN_CALENDAR = 'BEGIN:VCALENDAR'
	END_CALENDAR = 'END:VCALENDAR'
	BEGIN_EVENT = 'BEGIN:VEVENT'
	END_EVENT = 'END:VEVENT'
	BEGIN_AFTER = 'BEGIN:VTIMEZONE'

	in_preamble = True
	in_event = False
	event_content = None
	event_in_year = False
	bAfter = False

	event_count = 0
	out_event_count = 0
	
	preamble = []
	events = []
	after = []
	
	for counter, line in enumerate(infh):

		# print(counter)

		if (in_preamble and line.startswith(BEGIN_EVENT)):
			in_preamble = False

		if (line.startswith(BEGIN_AFTER) or bAfter):
			bAfter = True
			after.append(line)
		else:
			
			if in_preamble:
				preamble.append(line)
			else:
				
				if line.startswith(BEGIN_EVENT):
					event_content = []
					event_count += 1
					event_in_year = False
					in_event = True

				if in_event:
					if (year == "all") or created_pattern.match(line):
						event_in_year = True
					event_content.append(line)

				if line.startswith(END_EVENT):
					in_event = False

					if event_in_year:
						out_event_count += 1
						events.append(event_content)
	
	for counter in range(1, out_event_count, max_events_per_file):
		
		output_file_name = output_file_base + '_' + str(counter) + input_file_ext
		output_file = os.path.join(output_directory, output_file_name)
		print("Output file name: %s" % (output_file))
		if os.path.exists(output_file):
			print("ERROR: output file already exists! As a safety check, this script will not overwrite an ICS file")
			exit()
		
		outfh = open(output_file, 'w', encoding="utf8")
		
		for pre in preamble:
			outfh.write(pre)
		
		bottom = counter
		top = min(counter+max_events_per_file-1, out_event_count)
		for event in events[bottom:top]:
			outfh.write(''.join(event))
		print("Wrote %d events from %d to %d" % (top-bottom+1,bottom,top))
		
		for aft in after:
			outfh.write(aft)
		
		outfh.close()
	
	# done!
	if (out_event_count > 0):
		print("Wrote %d of %d events" % (out_event_count,event_count))
		print("-------------------")

	return out_event_count