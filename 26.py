# Works ---
# 15th March 2021,Monday
# 20th March 2021,Sunday - Mods
# 23rd , 24th March
# Function : Populates  PostgreSQL DB table with random ranged value for test,validation or development

# For PostgreSQL functionalities

# Error : Choice random is not working - treating the whole block as character & selecting accordinly ie 80,90,40 -- resurning 8 or ',' or 0 etc

import psycopg2
import random

# For Configuration Management
from configparser import ConfigParser

# For wildcard Matching
import fnmatch

# - 
CONFIG_FILENAME = 'config.cfg'
parser = ConfigParser()
parser.read(CONFIG_FILENAME)

#---
#dict.get(key, default=None) -> To get default value from a dictionary if no value assigned or missing
#---

try:

	connection = psycopg2.connect(user=parser.get('DATABASE_CONFIG', 'user'),
								password=parser.get('DATABASE_CONFIG', 'password'),
								host=parser.get('DATABASE_CONFIG','host'),
								port=parser.get('DATABASE_CONFIG','port'),
								database=parser.get('DATABASE_CONFIG','database'))
	cursor = connection.cursor()

	Table_Name =  parser.get('DATABASE_CONFIG','table')  # config['postgresql']['host'] - Alternate way


	# ------------------------------ SQL Construction -------------------------------------
	insert_query_pre_section = """ INSERT INTO %s """ % Table_Name
	insert_query_mid_section = "("
	insert_query_mid_section2= ") VALUES ("
	#--------------------------------------------------------------------------------------
	
	# Search only the sections that match the wildcard ie omitt the [DATABASE_CONFIG]
	sections = fnmatch.filter(parser.sections(), 'FIELD_*')  #parser.sections()
	field_list = []
	field_dictionary = {}
	record_to_insert = []
	field_index=0 # How to get ridd of this. - len()
	print('--------------------------------------------------------------------------------')
	#Value=''
	
	# Construct the data structure that constructs & hold the DB Field Parameter List[{Dictionary}]
	# Do not fillup the Value Parameter
	for section in sections:
	
		field_dictionary.clear()
		#field_dictionary = {}
		
		# if enabled option exists in .ini
		if (parser.has_option(section, 'enabled') == True) and (parser.get(section, 'enabled') == '1'):
			
			# ----------- If the 'Name' field exists in ini -------------------
			if (parser.has_option(section, 'name') == True) and (parser.get(section, 'name') != ''):
				# --------------- Dictionary Assignment -------------------
				field_dictionary['Enabled'] = parser.get(section, 'enabled')
				field_dictionary['Name'] = parser.get(section, 'name')
				field_dictionary['Index'] = field_index # ??? This this really needed ???

				# ------------------------------ SQL Construction --------------------------------------
				insert_query_mid_section = insert_query_mid_section + field_dictionary['Name'] + ","
				insert_query_mid_section2 = insert_query_mid_section2 + '%s,'
				#--------------------------------------------------------------------------------------------


				if parser.has_option(section, 'const') == True:
					field_dictionary['Const'] = parser.get(section, 'const')
				#----------------------------------------------------------------------


				if parser.has_option(section, 'choice') == True:
					field_dictionary['Choice'] = parser.get(section, 'choice')
				#----------------------------------------------------------------------


				if parser.has_option(section, 'type') == True:
					field_dictionary['Type'] = parser.get(section, 'type')
				#----------------------------------------------------------------------


				if parser.has_option(section, 'lowerbound') == True:
					field_dictionary['Lowerbound'] = parser.get(section, 'lowerbound')
				#----------------------------------------------------------------------


				if parser.has_option(section, 'upperbound') == True:
					field_dictionary['Upperbound'] = parser.get(section, 'upperbound')
				#----------------------------------------------------------------------

				field_list.append(dict(field_dictionary)) # dict() cast is very important here
				field_index+=1


	print('\n',field_list)
	# ------------------------------ SQL Construction -------------------------------------
	insert_query_final = insert_query_pre_section + insert_query_mid_section + insert_query_mid_section2 + ');'
	insert_query_final = insert_query_final.replace(',)', ')', 2)
	#--------------------------------------------------------------------------------------

	print('\n',insert_query_final)


	MaxRowInsert = 3 # 0 - 10 (MaxRowInsert - 1) - Change it accordingly
	for insertionLoop in range(MaxRowInsert): # Number of records to insert per batch


		# --------- Construct the value list for record insertion ------------
		#print("\nProbe",field_list)
		record_to_insert.clear()
		#record_to_insert= []
		for iterated_list in field_list:
			
			if 'Const' in iterated_list:
				#record_to_insert.append(iterated_list['Const'])
				record_to_insert.append(iterated_list['Const'])


			if 'Choice' in iterated_list:
				random.SystemRandom()
				#print('\nProbe***')
				print(iterated_list['Choice'])
				#record_to_insert.append(random.choice(list(iterated_list['Choice'])))
				#record_to_insert.append(random.choices(list(iterated_list['Choice'])))
				#record_to_insert.append(random.choice(tuple(iterated_list['Choice'])))
				record_to_insert.append(random.choice(iterated_list['Choice']))

			if 'Type' in iterated_list:

				if iterated_list['Type'] == 'random.uniform': 
					if (('Lowerbound' in iterated_list)) and ('Upperbound' in iterated_list):
						random.SystemRandom()
						record_to_insert.append(random.uniform(float(iterated_list['Lowerbound']),float(iterated_list['Upperbound'])))

				if iterated_list['Type'] == 'random.randrange':
					if (('Lowerbound' in iterated_list)) and ('Upperbound' in iterated_list):
						random.SystemRandom()
						record_to_insert.append(random.randrange(int(iterated_list['Lowerbound']),int(iterated_list['Upperbound'])))



		#  ---------- Actual Insertion in DB ----------
		# Parameterized Query
		print('\nrecord_to_insert',record_to_insert)
		cursor.execute(insert_query_final, record_to_insert)
		connection.commit()
		count = cursor.rowcount
		print("\n", count, "Record inserted successfully into table")
		#-----------------------------------------------------



except (Exception,psycopg2.Error) as error:
	print("", error)

finally:
	# closing database connection.
	if connection:
		cursor.close()
		connection.close()
		print("\nPostgreSQL connection is closed")

