import sqlite3

connection = sqlite3.connect("data.db")
curser = connection.cursor()

create_table = "CREATE TABLE users (id int, username text, password text)"
curser.execute(create_table)

user = (1, "Nanda", "Nanda@#$")
insert_query = "INSERT INTO users Values (?,?,?)"
curser.execute(insert_query, user)

usermany = [
    (2,"Shiva","Shiva@#$"),
    (3, "Charles DUhigg", "Charles@#$"),
    (4, "Shelley Zavitz", "Shelley@#$")
]

curser.executemany(insert_query, usermany)

select_query = "SELECT * From users"
for row in curser.execute(select_query):
    print(row)

connection.commit()

connection.close()
