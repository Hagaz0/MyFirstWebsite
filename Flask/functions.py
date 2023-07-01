import re

def is_login(mail):
    reg = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(reg, mail)

def checks(mail, password, repear_pass, name):
    return not (mail == "" or password == "" or repear_pass == "" or name == "")
# def add_user(mail, password, name):
