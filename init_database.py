##To execute once, creation of the db
# table users

import sqlite3

# Establish a connection to the database
conn = sqlite3.connect('fit_and_fun.db')

# Create a cursor object to execute SQL queries
cur = conn.cursor()


# Define the SQL query to create the table
query = '''DROP TABLE IF EXISTS users;'''
# Execute the SQL query
cur.execute(query)

query = '''CREATE TABLE users (
			id INTEGER PRIMARY KEY,
			user_name TEXT NOT NULL UNIQUE
			);'''
cur.execute(query)

# table games

query = '''DROP TABLE IF EXISTS games;'''
cur.execute(query)

query = '''CREATE TABLE games (
			id INTEGER PRIMARY KEY,
			game_name TEXT NOT NULL UNIQUE
			);'''
cur.execute(query)

# table exercices

query = '''DROP TABLE IF EXISTS exercices;'''
cur.execute(query)

query = '''CREATE TABLE exercices (
			id INTEGER PRIMARY KEY,
			ex_name TEXT NOT NULL UNIQUE,
			user_id INTEGER,
			FOREIGN KEY(user_id) REFERENCES users(id)
			);'''
cur.execute(query)

# table profiles

query = '''DROP TABLE IF EXISTS profiles;'''
cur.execute(query)

query = '''CREATE TABLE profiles (
			id INTEGER PRIMARY KEY,
			ex_id INTEGER,
			speed INTEGER,
			torque INTEGER,
			t_init REAL,
			t_f REAL,
			FOREIGN KEY(ex_id) REFERENCES exercices(id)
			);'''
cur.execute(query)

# tables play

query = '''DROP TABLE IF EXISTS play;'''
cur.execute(query)

query = '''CREATE TABLE play (
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
values = (0,'everybody')
query = "INSERT INTO users (id,user_name) VALUES (?,?)"
cur.execute(query, values)
conn.commit()

# verify the adding
query = '''SELECt * FROM users;'''
cur.execute(query)
result = cur.fetchall()
print(result)

# add the fist game
values = (0,'ducks')
query = "INSERT INTO games (id,game_name) VALUES (?,?)"
cur.execute(query, values)
conn.commit()

# verify the adding
query = '''SELECT * FROM games;'''
cur.execute(query)
result = cur.fetchall()
print(result)

# add the fist exercice
current_user_name ='everybody'
query = """SELECT *
			FROM users
			WHERE user_name = '""" + current_user_name + """' 
			;"""
cur.execute(query)
current_user_id = cur.fetchall()[0][0]
new_ex_name = 'echauffement'
values = (0,new_ex_name,current_user_id)
query = "INSERT INTO exercices (id,ex_name,user_id) VALUES (?,?,?)"
cur.execute(query, values)
conn.commit()

# verify the adding
query = '''SELECT * FROM exercices;'''
cur.execute(query)
result = cur.fetchall()
print(result)