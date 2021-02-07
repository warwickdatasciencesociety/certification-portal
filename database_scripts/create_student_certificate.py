import mysql.connector
import os
import hashlib
import random
from dotenv import load_dotenv
import requests

load_dotenv()

mydb = mysql.connector.connect(
    host="127.00.00.1",
    port="32000",
    user="root",
    password=os.environ["SQL_ROOT_PASSWORD"]
)

mycursor = mydb.cursor()
mycursor.execute("USE certificate_portal")


def get_jwt_token():
    # post to http://127.0.0.1:50000/token/auth
    url = "http://127.0.0.1:50000/token/auth"
    data = {'username': 'admin', 'password': os.environ['ADMIN_PASSWORD']}
    x = requests.post(url, json=data)
    
    return x.json()['access_token']

# MENTORS


def add_mentor(fname, lname):
    # check if mentor exists
    # if not exist
    sql = "INSERT INTO mentor (mentor_fname, mentor_lname) VALUES (%s, %s)"
    val = (fname, lname)
    mycursor.execute(sql, val)
    mydb.commit()

def add_mentor_api(access_token, fname, lname):
    url = "http://127.0.0.1:50000/api/crud/mentor"
    headers = {"Authorization": f'JWT {access_token}',
            "Cookie": f'access_token_cookie={access_token}'}

    data = {'mentor_fname': fname, 'mentor_lname': lname}
    request = requests.post(url, json=data, headers=headers)        
    
# STUDENTS
def add_student(fname, lname, email=None):
    if email is not None:
        sql = "INSERT INTO student (student_fname, student_lname, student_email) VALUES (%s, %s, %s)"
        val = (fname, lname, email)
    else:
        sql = "INSERT INTO student (student_fname, student_lname) VALUES (%s, %s)"
        val = (fname, lname)
    mycursor.execute(sql, val)
    mydb.commit()

def add_student_api(access_token, fname, lname, email):
    url = "http://127.0.0.1:50000/api/crud/student"
    headers = {"Authorization": f'JWT {access_token}',
            "Cookie": f'access_token_cookie={access_token}'}

    data = {'student_fname': fname, 'student_lname': lname, 'student_email': email}
    response = requests.post(url, json=data, headers=headers)        
    
    return response.json()['id']
# COURSES


def add_course(course_name, course_details):
    sql = "INSERT INTO course (course_name, course_details) VALUES (%s, %s)"
    val = (course_name, course_details)
    mycursor.execute(sql, val)
    mydb.commit()

def add_course_api(access_token, course_name, course_details):
    url = "http://127.0.0.1:50000/api/crud/course"
    headers = {"Authorization": f'JWT {access_token}',
            "Cookie": f'access_token_cookie={access_token}'}

    data = {'course_name': course_name, 'course_details': course_details}
    request = requests.post(url, json=data, headers=headers)        

def add_certificate(student_id, mentor_id, course_id, access_token):
    # cert_id = random.randint(0000000, 99999999)i
    #sql = "INSERT INTO certificate (student_id, mentor_id, course_id, cert_id) VALUES (%s %s %s %s)"
    #val = (student_id, mentor_id, course_id, cert_id)
    #mycursor.execute(sql, val)
    url = "http://127.0.0.1:50000/api/generate"
    headers = {"Authorization": f'JWT {access_token}',
               "Cookie": f'access_token_cookie={access_token}'}
    data = {
        "student_id": student_id,
        "mentor_id": mentor_id,
        "course_id": course_id}
    x = requests.post(url, json=data, headers=headers)

    print(x.text)
    return x.json()['cert_id']


def pre_load_mentors():
    add_mentor("Tim", "Hargreaves")
    add_mentor("Brandusa", "Draghici")
    add_mentor("Ciarán", "Evans")
    add_mentor("Farhan", "Tariq")
    add_mentor("Gabriel", "Musker")
    add_mentor("Horia", "Druliac")
    add_mentor("Janique", "Krasnowska")
    add_mentor("Lucy", "McArthur")
    add_mentor("Martin", "Smit")
    add_mentor("Raul-Octavian", "Rus")
    add_mentor("Yasser", "Qureshi")


def pre_load_courses():
    add_course("Introduction to Python", "16-hour Asssesed Course")
    add_course(
        "Introduction to Python",
        "16-hour Asssesed Course w/ Additional Pythonic Programming Foundations")
    add_course("Into the Tidyverse", "15-hour Asssesed Course")


def create_certificate(jwt):
    fname = input("STUDENT FNAME: ")
    lname = input("STUDENT LNAME: ")
    mycursor.execute(
        f"SELECT * FROM student WHERE student_fname='{fname}' AND student_lname='{lname}'")
    myresult = mycursor.fetchall()
    if len(myresult) == 0:
        print("**new student identified**")
        email = input("STUDENT EMAIL: ")
        add_student(fname, lname, email)
        student_id = mycursor.lastrowid
    else:
        print("Student(s) with the same name detected")
        for x in myresult:
            print(x)
        x = input("Add new student? [y/n]")
        if x == "y":
            email = input("STUDENT EMAIL: ")
            add_student(fname, lname, email)
            student_id = mycursor.lastrowid
        else:
            student_id = int(input("STUDENT ID: "))
    print(f'student id: {student_id}')

    mycursor.execute("SELECT * FROM mentor")
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)
    mentor_id = int(input("MENTOR ID: "))

    mycursor.execute("SELECT * FROM course")
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)

    course_id = int(input("COURSE ID: "))
    print(add_certificate(student_id, mentor_id, course_id, jwt))

def create_certificate_api(jwt):
    fname = input("STUDENT FNAME: ")
    lname = input("STUDENT LNAME: ")
    mycursor.execute(
        f"SELECT * FROM student WHERE student_fname='{fname}' AND student_lname='{lname}'")
    myresult = mycursor.fetchall()
    if len(myresult) == 0:
        print("**new student identified**")
        email = input("STUDENT EMAIL: ")
        student_id = add_student_api(jwt, fname, lname, email)
        
    else:
        print("Student(s) with the same name detected")
        for x in myresult:
            print(x)
        x = input("Add new student? [y/n]")
        if x == "y":
            email = input("STUDENT EMAIL: ")
            student_id = add_student_api(jwt, fname, lname, email)
        else:
            student_id = int(input("STUDENT ID: "))
    print(f'student id: {student_id}')

    mycursor.execute("SELECT * FROM mentor")
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)
    mentor_id = int(input("MENTOR ID: "))

    mycursor.execute("SELECT * FROM course")
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)

    course_id = int(input("COURSE ID: "))
    print(add_certificate(student_id, mentor_id, course_id, jwt))


jwt = get_jwt_token()

# add_student_api(jwt, "alex", "test", "a.test@gmail.com")
# add_course_api(jwt, "more python", "test")
# add_mentor_api(jwt, "Mr", "Job")

url = 
# print("CERTIFICATE GENERATOR")
# x = input("preload? [y/n]")
# if x == "y":
#     pre_load_mentors()
#     pre_load_courses()
# while(input("add cert [y/n]: ") == "y"):
#     create_certificate(jwt)