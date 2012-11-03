#!/usr/bin/env python
#
#Copyright 2012 Steve Pennington
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sqlite3, os

class NotInitializedException(Exception):
    pass

class FileIndex():
    
    def __init__(self, db_path):
        self.db_path = db_path
        
    def _connect_if_exists(self):
        if os.path.isfile(self.db_path):
            return sqlite3.connect(self.db_path)
        else:
            raise NotInitializedException('ram index does not exists. Have you called init?')
    
    def init(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE files (path text PRIMARY KEY, modified integer)
            ''')
        conn.commit()
        conn.close()
    
    def add(self, files):
        '''
        insert files into the index
        file should be a list of 2-tuples where the first value is the file
        path and the second value is the modified timestamp
        
        raises a NotInitializedException if the index has not been created
        '''
        conn = self._connect_if_exists()
        conn.executemany('INSERT OR IGNORE INTO files VALUES (?,?)', files)
        conn.commit()
        conn.close()
        
    def remove(self, file_path):
        '''
        remove a file from the index
        
        raises a NotInitializedException if the index has not been created
        '''
        conn = self._connect_if_exists()
        conn.execute('DELETE FROM files WHERE path=?', (file_path,))
        conn.commit()
        conn.close()
        
    def all(self):
        '''
        retrieve all files in the index
        
        raises a NotInitializedException if the index has not been created
        '''
        conn = self._connect_if_exists()
        cur = conn.cursor()
        cur.execute('SELECT * FROM files')
        rows = cur.fetchall()
        conn.close()
        return rows
    
    def update(self, file_path, modified_time):
        '''
        update the modified time on a file in the index
        
        raises a NotInitializedException if the index has not been created
        '''
        conn = self._connect_if_exists()
        conn.execute('UPDATE files SET modified=? WHERE path=?',
                     (modified_time, file_path))
        conn.commit()
        conn.close()
    