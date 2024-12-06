import csv
import sqlite3
import random
import string
from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash




with open('questions.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    print("CSV Columns:", reader.fieldnames)
    for row in reader:
        print(row)
        break