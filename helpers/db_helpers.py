"""
bd_helpers contain all the functions that we will use to
communicate with the database (get, insert and update data).
"""
import sqlite3
from flask import g

# Connecting the sqlite3 database
DATABASE = 'buyit.db'

def get_db():
    """Connects the database"""
    data_base = getattr(g, '_database', None)
    if data_base is None:
        data_base = g._database = sqlite3.connect(DATABASE)
    return data_base


def insert(table, fields=(), values=()):
    """Inserts values into database"""
    cur = get_db()
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(fields),
        ', '.join(['?'] * len(values))
    )
    cur.execute(query, values)
    cur.commit()
    # id = cur.lastrowid
    cur.close()
    return True
    # return id


def db_delete(table, condition):
    """Deletes values in database"""
    cur = get_db()
    query = 'DELETE FROM %s WHERE %s' % (
        table,
        condition
    )
    cur.execute(query)
    cur.commit()
    cur.close()
    return True


def update(table, condition, fields=(), values=()):
    """Update values in the database"""
    cur = get_db()
    concatenated_values = ""
    for i, (field, value) in enumerate(zip(fields, values)):
        if i == 0:
            concatenated_values += "%s = '%s'" %(field, value)
        else:
            concatenated_values += ", %s = '%s'" %(field, value)

    query = 'UPDATE %s SET %s WHERE %s' % (
        table,
        concatenated_values,
        condition
    )
    print(query)
    cur.execute(query)
    cur.commit()
    cur.close()
    return True


def close_connection():
    """Disconnects the database"""
    data_base = getattr(g, '_database', None)
    if data_base is not None:
        data_base.close()


def query_db(query, args=(), one=False):
    """Selects rows from the database"""
    cur = get_db().execute(query, args)
    row_dict = list(makedict(x, cur) for x in cur.fetchall())
    cur.close()
    return (row_dict[0] if row_dict else None) if one else row_dict

def makedict(row, cur):
    """Make a dictionary out of a list"""
    return dict(zip([c[0] for c in cur.description], row))
