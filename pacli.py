#! /usr/bin/env python

import getpass

import cryptacular.core
import cryptacular.pbkdf2
import cryptacular.bcrypt

import peewee

import model

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
      "ls"   : user_list,
      "add"  : user_add,
      "rm"   : user_remove,
      "info" : user_info
    }
    goto(mapper, args)

def user_list(*args):
    model.paladar_db.connect()
    users = model.User.select()
    print("{0} users.".format(users.count()))
    for user in users:
        print("  {0}".format(user.handle))
    model.paladar_db.close()

def user_add(*args):
    model.paladar_db.connect()
    user = model.User()
    ok = False
    while not ok:
        handle = input("Handle: ")
        try:
            model.User.get(model.User.handle == handle)
            print("Username '{0}' is already taken.".format(handle))
        except peewee.DoesNotExist:
            ok = True
    user.handle = handle
    user.name = input("Name: ")
    user.email = input("email: ")
    password = getpass.getpass("Password: ")
    user.hashed_password = delegator.encode(password)
    user.save()
    model.paladar_db.close()

def user_remove(*args):
    model.paladar_db.connect()
    for handle in args:
        print(handle)
        try:
            user = model.User.get(model.User.handle == handle)
        except peewee.DoesNotExist:
            user = None
        if user is None:
            print("  This user does not exist.")
            continue            
        user.delete_instance()
        print("  Removed succesfully.")
    model.paladar_db.close()

def user_info(*args):
    model.paladar_db.connect()
    for handle in args:
        print(handle)
        try:
            user = model.User.get(model.User.handle == handle)
        except peewee.DoesNotExist:
            user = None
        if user is None:
            print("  This user does not exist.")
            continue
        print("  Name: {0}".format(user.name))
        print("  email: {0}".format(user.email))
        print("  Language: {0}".format(user.language))
        print("  Timezone: {0}".format(user.timezone))
        print("  Hashed Password: {0}".format(user.hashed_password))
        print("  Corpus Length: {0}".format(user.corpuslen))
    model.paladar_db.close()

if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    mapper = {
      "user": user
    }
    goto(mapper, args)
