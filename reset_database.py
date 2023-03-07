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
			name TEXT PRIMARY KEY,
			value NOT NULL UNIQUE
			);'''
cur.execute(query)

query = '''DROP TABLE IF EXISTS Game;'''
cur.execute(query)
query = '''CREATE TABLE Game (
			id INTEGER PRIMARY KEY,
			game_name TEXT NOT NULL UNIQUE
			);'''
cur.execute(query)

query = '''DROP TABLE IF EXISTS Exercise;'''
cur.execute(query)
query = '''CREATE TABLE Exercise (
			id INTEGER PRIMARY KEY,
			ex_name TEXT NOT NULL UNIQUE,
			user_id INTEGER,
			FOREIGN KEY(user_id) REFERENCES users(id)
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
			FOREIGN KEY(ex_id) REFERENCES exercices(id)
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
			FOREIGN KEY(user_id) REFERENCES users(id),
			FOREIGN KEY(game_id) REFERENCES games(id),
			FOREIGN KEY(ex_id) REFERENCES exercices(id)
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
values = ('everybody', 'everybody')
query = "INSERT INTO User (name, value) VALUES (?,?)"
cur.execute(query, values)
conn.commit()

# verify the adding
query = '''SELECt * FROM User;'''
cur.execute(query)
result = cur.fetchall()
print(result)

# add the fist game
values = (0,'ducks')
query = "INSERT INTO Game (id,game_name) VALUES (?,?)"
cur.execute(query, values)
conn.commit()

# verify the adding
query = '''SELECT * FROM Game;'''
cur.execute(query)
result = cur.fetchall()
print(result)

# add the fist exercice
current_user_name ='everybody'
query = """SELECT *
			FROM User
			WHERE name = '""" + current_user_name + """' 
			;"""
cur.execute(query)
current_user_id = cur.fetchall()[0][0]
new_ex_name = 'echauffement'
values = (0,new_ex_name,current_user_id)
query = "INSERT INTO Exercise (id,ex_name,user_id) VALUES (?,?,?)"
cur.execute(query, values)
conn.commit()

# verify the adding
query = '''SELECT * FROM Exercise;'''
cur.execute(query)
result = cur.fetchall()
print(result)