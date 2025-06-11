import sqlite3

def CREATE_TABLE():
    conn=sqlite3.connect("students_data.db")
    cur=conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS students(
                id INTEGER PRIMARY KEY ,
                name TEXT NOT NULL,
                family TEXT NOT NULL,
                age INTEGER NOT NULL,
                grade INTEGER NOT NULL
                )''')
    conn.commit()
    conn.close()

def INSERT_STUDENTS(name,family,age,grade):
    conn=sqlite3.connect("students_data.db")
    cur=conn.cursor()
    cur.execute("INSERT INTO students(name,family,age,grade) VALUES(?,?,?,?)",(name,family,age,grade))
    conn.commit()
    conn.close()

def SEARCH_STUDENTS(student_id):
    conn = sqlite3.connect("students_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE name LIKE ? OR family LIKE ?", (f"%{student_id}%", f"%{student_id}%"))
    rows = c.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "family": row[2], "age": row[3], "grade": row[4]} for row in rows]


def UPDATE_STUDENTS(student_id,new_name,new_family,new_age,new_grade):
    conn=sqlite3.connect("students_data.db")
    cur=conn.cursor()
    cur.execute("UPDATE students SET name=?,family=?,age=?,grade=? WHERE id=?",(new_name,new_family,new_age,new_grade,student_id))
    conn.commit()
    conn.close()

def DELETE_STUDENTS(student_id):
    conn=sqlite3.connect("students_data.db")
    cur=conn.cursor()
    cur.execute("DELETE FROM students WHERE id=?",(student_id,))
    conn.commit()
    conn.close()

def SHOW_ALL_STUDENTS():
    conn=sqlite3.connect("students_data.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM students")
    data=cur.fetchall()
    conn.close()
    students_list = []
    for row in data:
        students_list.append({
            "id": row[0],
            "name": row[1],
            "family": row[2],
            "age": row[3],
            "grade": row[4]
        })
    return students_list


