from datetime import datetime
import requests
import sqlite3


class Utilities:
    @staticmethod
    def queryToList(query: str):
        listed = query.split(',')
        finalList = []
        for item in listed:
            finalList.append(item.strip())
        return finalList
    @staticmethod
    def epochToDatetime(epoch: int):
        date = datetime.fromtimestamp(epoch / 1000)
        return date.strftime('%Y-%m-%d %H:%M:%S')
    @staticmethod
    def fetchAPI(request: str):
        try:
            response = requests.get(request).json()
            return response
        except Exception:
            return None
        
    @staticmethod
    def insertPlayerData(conn, name, timestamp, x, z, balance=None):
        c = conn.cursor()
        
        if balance is None:
            c.execute('''
                INSERT INTO player_data (name, timestamp, x, z)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    timestamp=excluded.timestamp,
                    x=excluded.x,
                    z=excluded.z
            ''', (name, timestamp, x, z))
        else:
            c.execute('''
                INSERT INTO player_data (name, timestamp, x, z, bal)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    timestamp=excluded.timestamp,
                    x=excluded.x,
                    z=excluded.z,
                    bal=excluded.bal
            ''', (name, timestamp, x, z, balance))
        
        conn.commit()
    
    @staticmethod
    def fetchPlayerData(conn, name):
        name = name.lower()
        c = conn.cursor()
        c.execute('SELECT * FROM player_data WHERE name = ?', (name,))
        row = c.fetchone()
        
        if row is not None:
            result = {
                'name': row[0],
                'timestamp': row[1],
                'x': row[2],
                'z': row[3],
                'balance': row[4]
            }
            return result
        else:
            return None
        
    @staticmethod
    def fetchAllPlayerData(conn):
        c = conn.cursor()
        c.execute('SELECT * FROM player_data')
        rows = c.fetchall()
        
        results = []
        for row in rows:
            result = {
                'name': row[0],
                'timestamp': row[1],
                'x': row[2],
                'z': row[3],
                'balance': row[4]
            }
            results.append(result)
        
        return results
    
    @staticmethod
    def DBstart():
        conn = sqlite3.connect('cache.db')
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS player_data (
                name TEXT UNIQUE,
                timestamp INTEGER,
                x INTEGER,
                z INTEGER,
                bal INTEGER
            )
        ''')

        c.execute('CREATE INDEX IF NOT EXISTS idx_name ON player_data (name)')

        conn.commit()
        return conn

    def levenshteinDistance(s1, s2):
        if len(s1) < len(s2):
            return Utilities.levenshteinDistance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    @staticmethod
    def findClosestCommand(target, strings):
        distances = [(s, Utilities.levenshteinDistance(target, s)) for s in strings]
        closest_string = min(distances, key=lambda x: x[1])[0]
        return closest_string
    
    @staticmethod
    def fetch_town_chunk(sublist):
        try:
            result = ','.join(sublist)
            town_chunk = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/towns?query={result}')
        except Exception:
            return None
        return town_chunk
    
    @staticmethod
    def fetch_player_chunk(sublist):
        try:
            result = ','.join(sublist)
            player_chunk = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/players?query={result}')
        except Exception:
            return None
        return player_chunk
    
    @staticmethod
    def fetch_nation_chunk(sublist):
        try:
            result = ','.join(sublist)
            nation_chunk = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/nations?query={result}')
        except Exception:
            return None
        return nation_chunk
    
    @staticmethod
    def listToString(list):
        result = ', '.join(list)
        return str(result)