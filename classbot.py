import os
from datetime import datetime

debug = 1		# 0: Suppress warnings that things are going wrong. 1: Show me English-language warnings. 2: Show everything you are doing.

def loadDictionary(textfile):
	"""This function takes a path to a text file and tries to load it in as a dictionary object -- then return the dictionary object."""
	# Create an empty dictionary to return at the end of the function.
	d = {}
	with open(textfile,"r") as f:	    # Let the file close when we are done with it.
		for line in f:
			entry = line.split(' ',1) 	# Split on the first space in the file, turning it into a list.
			if len(entry) < 2: 
				# If you don't find a key/value pair, then don't try to update the dictionary.
				if debug > 0: print("Bad line in",textfile,"ignored:", line)
			else:
				d[entry[0]] = entry[1].strip()	# The file should have a key value pair separated by a space, so the first is the key and the second is the value.

	if debug >= 2: print('Dictionary loaded from',textfile,'as follows:',d)
	return d

def parseRosters(directory):
	"""This function looks through all the files in the directory passed, and tries to figure out what the current rosters are."""

	input('Fill up the rosters directory with Rosters -- get them by right-clicking and Save Link As... "from SSB" in myWCC for each course. Press any key when ready.')

	# We only want the most recent roster of each CRN. This will hold key: CRN, value: list with [0]:filename, [1]:date.
	RecentRosters = {}

	for filename in os.listdir(directory):
		if debug >=2: print("Parsing file:", filename)
		

		with open(os.path.join(directory,filename),"r", encoding="utf8") as f:	#Let the file close when we are done with it.
			while True:	
				line = f.readline()
				if line == '': break	# Apparently readline returns an empty string only at end of file. 
				
				# Recognize when the date and semester block was discovered.
				elif line.find('<DIV class="staticheaders"') > -1:
					Nameline = f.readline()
					Semesterline = f.readline()
					Dateline = f.readline()

					Semester = Semesterline.strip()[:-4] # The semester is everything except the <br> at the end.
					Date = datetime.strptime(Dateline.strip(), '%b %d,%Y %I:%M %p<br>') # The date also has <br>.			

				# Recognize when we have discovered the CRN.
				if line.find('<ACRONYM title = "Course Reference Number">') > -1:  
					CRNline = f.readline()  # The line before the CRN line contains an ACRONYM tag.
					CRNposition = CRNline.find('?crn=') + 5
					CRN = CRNline[CRNposition:CRNposition+5]
				
					# We don't want to keep parsing this file if it is already known to be an old roster. 
					if CRN in RecentRosters:
						if RecentRosters[CRN][1] > Date:
							break					

				# Recognize when we found a block of student information
				elif line.find("window.status='Student Information';") > -1:
					Nameline = line
					Xline = f.readline()
					for x in range(1,7): useless = f.readline() # several useless lines
					Emailline = f.readline()

					Name = Nameline[Nameline.find('return true">')+13:Nameline.find('</A>')]
					Xnumber = Xline[-22:-13]
					Email = Emailline[Emailline.find('mailto:')+7:Emailline.find('"    target')]
					print("Student parsed: Xnumber",Xnumber,"Name",Name,"Email",Email)
					
			# Now, if this roster is (so far) the most recent roster in the RecentRosters dictionary, then replace it.		
			if CRN in RecentRosters:
				if RecentRosters[CRN][1] < Date:
					RecentRosters[CRN] = [filename,Date]
			else:
				RecentRosters[CRN] = [filename,Date]

			print("File successfully parsed: CRN",CRN,"Date",Date,"Semester",Semester,"in file",filename)

	print(RecentRosters)



if debug > 0: print('Loading settings...')
Settings = loadDictionary('settings.txt')

nextUserRequest=''
while nextUserRequest != 'X':
	nextUserRequest = input('Terrible UI: R for parse rosters, H for parse homeworks, X for exit:').upper()
	
	if nextUserRequest == 'R':
		parseRosters(Settings['Rosters'])
	elif nextUserRequest == 'H':
		print("This doesn't work yet!")
	elif nextUserRequest == 'X':
		print("Bye!")
	else:	 
		print("I don't understand what you wanted.")


