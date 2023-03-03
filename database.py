import sqlite3


# Establish a connection to the database
conn = sqlite3.connect('fit_and_fun.db')

# Create a cursor object to execute SQL queries
cur = conn.cursor()

# query to obtain the list of registered users
def obtain_users_list():
    query = '''SELECT * FROM users;'''
    cur.execute(query)
    users = cur.fetchall()
    user_list = [('Invite','Invite')]
    for user in users :
        user_list.append((user[1],user[1]))
    return(user_list)

# query to create a new user
def create_new_user_in_db(new_user_name):
    query = '''SELECT MAX(id) FROM users;'''
    cur.execute(query)
    new_id = cur.fetchall()[0][0] + 1
    values = (new_id,new_user_name)
    query = "INSERT INTO users (id,user_name) VALUES (?,?)"
    cur.execute(query, values)
    conn.commit()

# query to obtain the list of registered games
def list_games():
    query = '''SELECT * FROM games;'''
    cur.execute(query)
    games = cur.fetchall()
    game_list = []
    for game in games :
        game_list.append(game[1])
    return(game_list)

# query to obtain the highest score
def high_score():
    query = '''SELECT MAX(score) FROM play;'''
    cur.execute(query)
    result = cur.fetchall()[0][0]
    if result != None:
        high_score = result
    else :
        high_score = 0
    return(high_score)

# query to obtain the list of registered exercises for the current user
def list_exercises_current_user():
    current_user_name = 'player 1'
    query = '''SELECT * 
                FROM exercices
                JOIN users
                ON users.id = user_id
                WHERE user_name = 'everybody'
                OR user_name = ' ''' + current_user_name + ''' '
                ;'''
    cur.execute(query)
    exercices = cur.fetchall()
    exercice_list = []
    for exercice in exercices :
        exercice_list.append(exercice[1])
    return(exercice_list)

# query to obtain the history of the current user
def history_current_user(current_user_name):
    query = '''SELECT * 
			    FROM play
			    JOIN users
			    ON users.id = user_id
			    WHERE user_name = ' ''' + current_user_name + ''' '
			    ORDER BY date DESC
			    LIMIT 20
			    ;'''
    cur.execute(query)
    history = cur.fetchall()
    exercice_list = []
    for exercice in history :
        exercice_list.append(exercice[1])
    return(exercice_list)

# query to obtain the history of last days
def general_history():
    n_days = 3
    query = '''SELECT strftime('%d-%m-%Y', 'now', '-'''+ str(n_days) +''' days');'''
    cur.execute(query)
    history_date = cur.fetchall()[0][0]
    query = '''SELECT * 
	    		FROM play
		    	WHERE date >= ' ''' + history_date + ''' ' 
			    ORDER BY date DESC
			    ;'''
    cur.execute(query)
    history = cur.fetchall()
    exercice_list = []
    for exercice in history :
        exercice_list.append(exercice[1])
    return exercice_list

# # query to add the finished game (automatically done)
# query = '''SELECT MAX(id) FROM play;'''
# cur.execute(query)
# result = cur.fetchall()[0][0]
# if result != None :
# 	new_id = result + 1
# else :
# 	new_id = 0

# current_user_name = 'player 1'
# query = """SELECT *
# 				FROM users
# 				WHERE user_name = '""" + current_user_name + """'
# 				;"""
# cur.execute(query)
# current_user_id = cur.fetchall()[0][0]

# current_game_name = 'ducks'
# query = """SELECT *
# 				FROM games
# 				WHERE game_name = '""" + current_game_name + """'
# 				;"""
# cur.execute(query)
# current_game_id = cur.fetchall()[0][0]

# current_ex_name = 'echauffement'
# query = """SELECT *
# 				FROM exercices
# 				WHERE ex_name = '""" + current_ex_name + """'
# 				;"""
# cur.execute(query)
# current_ex_id = cur.fetchall()[0][0]

# query = '''SELECT strftime('%d-%m-%Y', 'now');'''
# cur.execute(query)
# date = cur.fetchall()[0][0]

# score = 1000
# t_tot = 1000
# distance = 1000
# avg_speed = 10
# avg_power = 10

# values = (new_id,current_game_id,current_user_id,current_ex_id,date,score,t_tot,distance,avg_speed,avg_power,)
# query = "INSERT INTO play (id,game_id,user_id,ex_id,date,score,t_tot,distance,avg_speed,avg_power) VALUES (?,?,?,?,?,?,?,?,?,?)"
# cur.execute(query, values)
# conn.commit()

# Close the cursor and database connection
cur.close()
conn.close()