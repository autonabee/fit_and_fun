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

import sqlite3


def get_all_user_tuples():
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT * FROM User;"
    cur.execute(query)
    users = cur.fetchall()
    user_list = []
    for user in users :
        user_list.append((user[1],user[1]))
    cur.close()
    conn.close()
    return(user_list)

def get_all_user_names():
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT user_name FROM User;"
    cur.execute(query)
    users = cur.fetchall()
    users_list = []
    for ex in users :
        users_list.append(ex[0])
    cur.close()
    conn.close()
    return(users_list)

def get_all_exercise_tuples():
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT ex_name FROM Exercise;"
    cur.execute(query)
    exercises = cur.fetchall()
    exercises_list = []
    for ex in exercises :
        exercises_list.append((ex[0], ex[0]))
    cur.close()
    conn.close()
    return(exercises_list)

def get_all_exercise_names():
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT ex_name FROM Exercise;"
    cur.execute(query)
    exercises = cur.fetchall()
    exercises_list = []
    for ex in exercises :
        exercises_list.append(ex[0])
    cur.close()
    conn.close()
    return(exercises_list)

def get_all_game_tuples():
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT display_name, class_name FROM Game;"
    cur.execute(query)
    games = cur.fetchall()
    games_list = []
    for game in games :
        games_list.append((game[0], game[1]))
    cur.close()
    conn.close()
    return(games_list)

def get_data_from_user(user_name):
    """Returns a tuple containing data about the given user
    
    Args:
        user_name (string): name of the user
    Return:
        array containing : [mean_speed(float), nb_speed_values(int), time_played(int), time_max(int)]
    """
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT mean_speed, nb_speed_values, time_played, time_max FROM User WHERE user_name=?"
    cur.execute(query, (user_name,))
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res[0]

def create_new_user(new_user_name):
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT MAX(id) FROM User"
    cur.execute(query)
    new_id = cur.fetchall()[0][0] + 1
    values = (new_id, new_user_name, new_user_name, 0.0, 0, 0, 0)
    query = "INSERT INTO User (id, user_name, value, mean_speed, nb_speed_values, time_played, time_max) VALUES (?,?,?,?,?,?,?)"
    cur.execute(query, values)
    conn.commit()
    cur.close()
    conn.close()

def create_new_exercise(ex_name, user_name):
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT id FROM User WHERE user_name=?"
    cur.execute(query, (user_name,))
    user_id = cur.fetchall()[0][0]
    query = "SELECT MAX(id) FROM Exercise;"
    cur.execute(query)
    new_id = cur.fetchall()[0][0] + 1
    values = (new_id, ex_name, user_id)
    query = "INSERT INTO Exercise (id, ex_name, user_id) VALUES (?,?,?)"
    cur.execute(query, values)
    conn.commit()
    cur.close()
    conn.close()

def create_new_stage(ex_name, time, resistance, difficulte):
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT id FROM Exercise WHERE ex_name=?"
    cur.execute(query, (ex_name,))
    res = cur.fetchall()
    ex_id = res[0][0]
    query = "SELECT MAX(id) FROM Stage;"
    cur.execute(query)
    new_id = cur.fetchall()[0][0] + 1
    values = (new_id, ex_id, time, resistance, difficulte)
    query = "INSERT INTO Stage (id, ex_id, time, resistance, difficulte) VALUES (?,?,?,?,?)"
    cur.execute(query, values)
    conn.commit()
    cur.close()
    conn.close()

def update_data_from_user(user_name, speed_value, time_value):
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT mean_speed, nb_speed_values, time_played, time_max FROM User WHERE user_name=?"
    cur.execute(query, (user_name,))
    res = cur.fetchall()
    mean_speed = res[0][0]
    nb_speed_values = res[0][1]
    time_played = res[0][2]
    time_max = max(time_value, res[0][3])
    if time_played + time_value > 0:
        new_mean_speed = (mean_speed*time_played + speed_value*time_value) / (time_played + time_value)
    else:
        new_mean_speed = mean_speed
    nb_speed_values = nb_speed_values + 1
    time_played = time_played + time_value
    query = "UPDATE User SET mean_speed=?, nb_speed_values=?, time_played=?, time_max=? WHERE user_name=?"
    cur.execute(query, (new_mean_speed, nb_speed_values, time_played, time_max, user_name))
    conn.commit()
    cur.close()
    conn.close()

def delete_all_stages_from_ex(ex_name):
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT id FROM Exercise WHERE ex_name=?"
    cur.execute(query, (ex_name,))
    ex_id = cur.fetchall()[0][0]
    query = "DELETE FROM Stage WHERE ex_id=?"
    cur.execute(query, (ex_id,))
    conn.commit()
    cur.close()
    conn.close()

def delete_exercise(ex_name):
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "DELETE FROM Exercise WHERE ex_name=?"
    cur.execute(query, (ex_name,))
    conn.commit()
    cur.close()
    conn.close()

def delete_user(user_name):
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "DELETE FROM User WHERE user_name=?"
    cur.execute(query, (user_name,))
    conn.commit()
    cur.close()
    conn.close()

def get_all_stages_from_ex(ex_name):
    conn = sqlite3.connect('fit_and_fun.db')
    cur = conn.cursor()
    query = "SELECT id FROM Exercise WHERE ex_name=?"
    cur.execute(query, (ex_name,))
    res = cur.fetchall()
    ex_id = res[0][0]
    query = "SELECT * FROM Stage WHERE ex_id=?"
    cur.execute(query, (ex_id,))
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

# # query to obtain the list of registered games
# def list_games():
#     query = '''SELECT * FROM Game;'''
#     cur.execute(query)
#     games = cur.fetchall()
#     game_list = []
#     for game in games :
#         game_list.append(game[1])
#     return(game_list)

# # query to obtain the highest score
# def high_score():
#     query = '''SELECT MAX(score) FROM Play;'''
#     cur.execute(query)
#     result = cur.fetchall()[0][0]
#     if result != None:
#         high_score = result
#     else :
#         high_score = 0
#     return(high_score)

# # query to obtain the list of registered exercises for the current user
# def list_exercises_current_user():
#     current_user_name = 'player 1'
#     query = '''SELECT * 
#                 FROM Exercise
#                 JOIN User
#                 ON User.id = user_id
#                 WHERE user_name = 'everybody'
#                 OR user_name = ' ''' + current_user_name + ''' '
#                 ;'''
#     cur.execute(query)
#     exercices = cur.fetchall()
#     exercice_list = []
#     for exercice in exercices :
#         exercice_list.append(exercice[1])
#     return(exercice_list)

# # query to obtain the history of the current user
# def history_current_user(current_user_name):
#     query = '''SELECT * 
# 			    FROM Play
# 			    JOIN User
# 			    ON User.id = user_id
# 			    WHERE user_name = ' ''' + current_user_name + ''' '
# 			    ORDER BY date DESC
# 			    LIMIT 20
# 			    ;'''
#     cur.execute(query)
#     history = cur.fetchall()
#     exercice_list = []
#     for exercice in history :
#         exercice_list.append(exercice[1])
#     return(exercice_list)

# # query to obtain the history of last days
# def general_history():
#     n_days = 3
#     query = '''SELECT strftime('%d-%m-%Y', 'now', '-'''+ str(n_days) +''' days');'''
#     cur.execute(query)
#     history_date = cur.fetchall()[0][0]
#     query = '''SELECT * 
# 	    		FROM Play
# 		    	WHERE date >= ' ''' + history_date + ''' ' 
# 			    ORDER BY date DESC
# 			    ;'''
#     cur.execute(query)
#     history = cur.fetchall()
#     exercice_list = []
#     for exercice in history :
#         exercice_list.append(exercice[1])
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