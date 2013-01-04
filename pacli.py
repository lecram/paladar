#! /usr/bin/env python

import getpass

import model

import cryptacular.core
import cryptacular.pbkdf2
import cryptacular.bcrypt

pbkdf2 = cryptacular.pbkdf2.PBKDF2PasswordManager()
bcrypt = cryptacular.bcrypt.BCRYPTPasswordManager()
delegator = cryptacular.core.DelegatingPasswordManager(preferred=pbkdf2, fallbacks=(bcrypt,))

def unknown(label):
    print("Unknown command: {0}.".format(label))

def empty(mapper):
    print("Available commands:")
    for cmd in mapper:
        print("  {0}".format(cmd))

def goto(mapper, args):
    args = list(args)
    if args:
        label = args.pop(0)
        if label in mapper:
            mapper[label](*args)
        else:
            unknown(label)
    else:
        empty(mapper)

def user(*args):
    mapper = {
      "ls" : user_list,
      "add": user_add,
      "rm" : user_remove
    }
    goto(mapper, args)

def user_list(*args):
    model.paladar_db.connect()
    users = model.User.select()
    print("{0} users.".format(users.count()))
    for user in users:
        print("  {0}".format(user.handle))

def user_add(*args):
    model.paladar_db.connect()
    user = model.User()
    user.handle = input("Handle: ")
    user.name = input("Name: ")
    user.email = input("email: ")
    password = getpass.getpass("Password: ")
    user.hashed_password = delegator.encode(password)
    user.save()

def user_remove(*args):
    model.paladar_db.connect()
    user = model.User.get(User.handle == args[0])
    user.delete_instance()

if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    mapper = {
      "user": user
    }
    goto(mapper, args)
