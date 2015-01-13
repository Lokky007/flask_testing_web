# -*- coding: utf8 -*-
from datetime import datetime
from pony.orm import *

db = Database("postgres", host="localhost", user="postgres",
              password="postgres", database="test")

class Student(db.Entity):
    _table_ = "student"
    id = PrimaryKey(int, auto=True)
    login = Required(str, 20, unique=True)
    jmeno = Required(unicode, 20)
    prijmeni = Required(unicode, 30)
    hash = Required(str, 196)
    akcee = Set("Akce")
    vysledky_testu = Set("Vysledek_testu")

class Akce(db.Entity):
    """číselník akcí, které může uživatel na webu provádět"""
    _table_ = "akce"
    id = PrimaryKey(int, auto=True)
    cas = Required(datetime)
    student = Required(Student)
    test = Optional("Test")
    vysledek_testu = Optional("Vysledek_testu")

class Vysledek_testu(db.Entity):
    _table_ = "vysledek_testu"
    id = PrimaryKey(int, auto=True)
    student = Required(Student)
    test = Required("Test")
    odpovedi = Set("Odpoved")
    akcee = Set(Akce)

class Test(db.Entity):
    _table_ = "test"
    id = PrimaryKey(int, auto=True)
    vysledky_testu = Set(Vysledek_testu)
    otazky_testus = Set("Otazka_testu")
    akcee = Set(Akce)

class Otazka(db.Entity):
    _table_ = "otazka"
    id = PrimaryKey(int, auto=True)
    text = Required(str)
    spravna_odpoved = Required(str)
    odpovedi = Set("Odpoved")
    otazky_testus = Set("Otazka_testu")

class Odpoved(db.Entity):
    _table_ = "odpoved"
    id = PrimaryKey(int, auto=True)
    otazka = Required(Otazka)
    text = Required(unicode)
    vysledek_testu = Required(Vysledek_testu)

class Otazka_testu(db.Entity):
    _table_ = "otazka_testu"
    id = PrimaryKey(int, auto=True)
    test = Required(Test)
    otazka = Required(Otazka)

sql_debug(True)
db.generate_mapping(create_tables=True)