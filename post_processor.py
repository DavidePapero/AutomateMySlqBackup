"""Copyright 2025 Infantino Davide

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


# import pymysql
# import pymysql.cursors
# import pymysql.connections
# import typing


DBCONFIG : dict = {
    'user':'hyppo-python',
    'password': 'hyppo-python-password',
    'host': 'database-hyppo.rds.amazonaws.com',
    'database': 'hyppo',
    'port': 3306,
    'use_unicode': True,
    'connect_timeout': 60,
    'ssl_disabled': True,
    'compress': False,
    'read_timeout': 120,
    'write_timeout': 120,
    #'cursorclass': pymysql.cursors.Cursor
    'cursorclass':pymysql.cursors.DictCursor
}

def postProcessBackupFile(name : str, strerror : str = '', start : bool = False):
    pass
    # try:
    #     with pymysql.connect(**DBCONFIG) as cnx:
    #         with cnx.cursor() as cursor:
    #             if start:
    #                 query = "INSERT INTO xxx (name, firstRun) VALUES(%s, NOW() ) ON DUPLICATE KEY UPDATE firstRun = VALUES(firstRun);"
    #                 cursor.execute(query,(name,))
    #             else:
    #                 if strerror == '':
    #                     query = "INSERT INTO xxx (name, lastRun, status) VALUES(%s, NOW(), 'Ok') ON DUPLICATE KEY UPDATE lastRun = VALUES(lastRun), status = VALUES(status);"
    #                     cursor.execute(query,(name,))
    #                 else:
    #                     query = "INSERT INTO xx (name, status, exception, exceptionDate) VALUES(%s, 'Ko', %s, NOW()) ON DUPLICATE KEY UPDATE exception = VALUES(exception), exceptionDate = VALUES(exceptionDate), status = VALUES(status);"
    #                     cursor.execute(query,(name, strerror))
    #             cnx.commit()
    # except Exception as why:
    #     print(why)

def StartBackupProcess(name : str):
    postProcessBackupFile(name, start=True)