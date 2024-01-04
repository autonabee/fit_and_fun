# This file is a part of Fit & Fun
#
# Copyright (C) 2023 Inria/Autonabee
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

##To execute once, creation of the db
# table users

import sqlite3

# Establish a connection to the database
conn = sqlite3.connect('fit_and_fun.db')

# Create a cursor object to execute SQL queries
cur = conn.cursor()


query = '''DROP TABLE IF EXISTS User;'''
cur.execute(query)
query = '''CREATE TABLE User (
			id INTEGER PRIMARY KEY,
			user_name TEXT NOT NULL UNIQUE,
			value NOT NULL UNIQUE,
			mean_speed REAL,
			nb_speed_values INTEGER,
			time_played INTEGER,
			time_max INTEGER
			);'''
cur.execute(query)

query = '''DROP TABLE IF EXISTS Game;'''
cur.execute(query)
query = '''CREATE TABLE Game (
			id INTEGER PRIMARY KEY,
			display_name TEXT NOT NULL UNIQUE,
			class_name TEXT NOT NULL UNIQUE
			);'''
cur.execute(query)

query = '''DROP TABLE IF EXISTS Exercise;'''
cur.execute(query)
query = '''CREATE TABLE Exercise (
			id INTEGER PRIMARY KEY,
			ex_name TEXT NOT NULL UNIQUE,
			user_id INTEGER,
			FOREIGN KEY(user_id) REFERENCES User(id)
			);'''
cur.execute(query)

query = '''DROP TABLE IF EXISTS Stage;'''
cur.execute(query)
query = '''CREATE TABLE Stage (
			ex_id INTEGER,
			id INTEGER,
			time INTEGER,
			resistance INTEGER,
			difficulte INTEGER,
			PRIMARY KEY(ex_id, id),
			FOREIGN KEY(ex_id) REFERENCES Exercise(id)
			);'''
cur.execute(query)

query = '''DROP TABLE IF EXISTS Profile;'''
cur.execute(query)
query = '''CREATE TABLE Profile (
			id INTEGER PRIMARY KEY,
			ex_id INTEGER,
			speed INTEGER,
			torque INTEGER,
			t_init REAL,
			t_f REAL,
			FOREIGN KEY(ex_id) REFERENCES Exercise(id)
			);'''
cur.execute(query)

query = '''DROP TABLE IF EXISTS Sequence;'''
cur.execute(query)
query = '''CREATE TABLE Sequence (
			id INTEGER PRIMARY KEY,
			user_id INTEGER,
			game_id INTEGER,
			ex_id INTEGER,
			date DATE,
			score INTEGER,
			t_tot REAL NOT NULL,
			distance INTEGER,
			avg_speed REAL,
			avg_power REAL,
			FOREIGN KEY(user_id) REFERENCES User(id),
			FOREIGN KEY(game_id) REFERENCES Game(id),
			FOREIGN KEY(ex_id) REFERENCES Exercise(id)
			);'''
cur.execute(query)

# Commit the changes to the database
conn.commit()


# Define the SQL query to retrieve column information for a table
query = '''SELECT name FROM sqlite_master WHERE type='table';'''
cur.execute(query)

# Fetch all the tables from the result set
tables = cur.fetchall()

# Print the tables information
for table in tables:
	print('	' + str(table[0]))

	# Define the SQL query to retrieve column information for a table
	query = '''PRAGMA table_info('''+str(table[0])+''');'''

	# Execute the SQL query
	cur.execute(query)

	# Fetch all the columns from the tables
	columns = cur.fetchall()

	# Print the columns
	for column in columns:
		print(column[1])
	
	print('')

# add the user by default
values = (0, 'everybody', 'everybody', 0.0, 0, 0, 0)
query = "INSERT INTO User (id, user_name, value, mean_speed, nb_speed_values, time_played, time_max) VALUES (?,?,?,?,?,?,?)"
cur.execute(query, values)
conn.commit()

# verify the adding
query = '''SELECt * FROM User;'''
cur.execute(query)
result = cur.fetchall()
print(result)

# add the fist game
values = (0,'What The Duck', 'GameCanoe')
query = "INSERT INTO Game (id, display_name, class_name) VALUES (?,?,?)"
cur.execute(query, values)
values = (1,'Boring text', 'GameData')
query = "INSERT INTO Game (id, display_name, class_name) VALUES (?,?,?)"
cur.execute(query, values)
conn.commit()

# verify the adding
query = '''SELECT * FROM Game;'''
cur.execute(query)
result = cur.fetchall()
print(result)

# add the first exercice
current_user_name ='everybody'
query = """SELECT *
			FROM User
			WHERE user_name = '""" + current_user_name + """' 
			;"""
cur.execute(query)
current_user_id = cur.fetchall()[0][0]
new_ex_name = 'Echauffement'
values = (0,new_ex_name,current_user_id)
query = "INSERT INTO Exercise (id,ex_name,user_id) VALUES (?,?,?)"
cur.execute(query, values)
# with 1 stage
values = (0, 0, 90, 1, 1)
query = "INSERT INTO Stage (id,ex_id,time,resistance, difficulte) VALUES (?,?,?,?,?)"
cur.execute(query, values)
conn.commit()

# verify the adding
query = '''SELECT * FROM Exercise;'''
cur.execute(query)
result = cur.fetchall()
print(result)
query = '''SELECT * FROM Stage;'''
cur.execute(query)
result = cur.fetchall()
print(result)