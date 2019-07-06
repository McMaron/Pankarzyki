import csv
import urllib.request
import sqlite3
import os

from flask import redirect, render_template, request, session
from functools import wraps

def seccheck(s):
    delims="\"'`{};:[]()<>"
    forbidden = []
    for d in delims:
        if d in s:
            forbidden.append(d)
    if len(forbidden) > 0:
        return 0
    else:
        return 1




