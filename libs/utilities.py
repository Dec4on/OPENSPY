from datetime import datetime
import requests
import sqlite3
import json
import time


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
    def insertPlayerData(conn, name, timestamp, x, z):
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO player_data (name, timestamp, x, z)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                timestamp=excluded.timestamp,
                x=excluded.x,
                z=excluded.z
        ''', (name, timestamp, x, z))
        
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
            }
            results.append(result)
        
        return results
    
    @staticmethod
    def numberOfPages(list, items_per_page):
        list = len(list)
        full_pages = list // items_per_page
        
        if list % items_per_page != 0:
            full_pages += 1

        return full_pages
    
    @staticmethod
    def DBstart():
        conn = sqlite3.connect('cache.db')
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS player_data (
                name TEXT UNIQUE,
                timestamp INTEGER,
                x INTEGER,
                z INTEGER
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS player_balances (
                id INTEGER PRIMARY KEY,
                player_name TEXT,
                balance INTEGER,
                timestamp INTEGER,
                x INTEGER,
                z INTEGER,
                FOREIGN KEY(player_name) REFERENCES player_data(name)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS trade_potentials (
                id INTEGER PRIMARY KEY,
                player_name TEXT,
                profit BOOLEAN,
                potentials TEXT,
                amount INTEGER,
                timestamp INTEGER,
                x INTEGER,
                z INTEGER,
                FOREIGN KEY(player_name) REFERENCES player_data(name)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                setting_name TEXT UNIQUE,
                setting_value BOOLEAN
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS caching (
                cache_name TEXT UNIQUE,
                cache_value TEXT,
                timestamp INTEGER
            )
        ''')

        c.execute('CREATE INDEX IF NOT EXISTS idx_player_name ON player_balances (player_name)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON player_balances (timestamp)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_trade_player_name ON trade_potentials (player_name)')

        conn.commit()
        return conn
    
    @staticmethod
    def setSetting(conn, setting_name, setting_value):
        c = conn.cursor()
        c.execute('''
            INSERT INTO settings (setting_name, setting_value)
            VALUES (?, ?)
            ON CONFLICT(setting_name) DO UPDATE SET setting_value=excluded.setting_value
        ''', (setting_name, setting_value))
        conn.commit()

    @staticmethod
    def getSetting(conn, setting_name):
        try:
            c = conn.cursor()
            c.execute('SELECT setting_value FROM settings WHERE setting_name=?', (setting_name,))
            result = c.fetchone()
            return result[0] if result else None
        except Exception:
            return None
        
    @staticmethod
    def setCache(conn, cache_name, cache_value, timestamp):
        cache_value = json.dumps(cache_value)
        c = conn.cursor()
        c.execute('''
            INSERT INTO caching (cache_name, cache_value, timestamp)
            VALUES (?, ?, ?)
            ON CONFLICT(cache_name) DO UPDATE SET cache_value=excluded.cache_value, timestamp=excluded.timestamp
        ''', (cache_name, cache_value, timestamp))
        conn.commit()

    @staticmethod
    def getCache(conn, cache_name):
        try:
            c = conn.cursor()
            c.execute('SELECT cache_value, timestamp FROM caching WHERE cache_name=?', (cache_name,))
            result = c.fetchone()
            if result:
                cache_value = json.loads(result[0])
                timestamp = result[1]
            else:
                cache_value = None
                timestamp = None
            return cache_value, timestamp
        except Exception:
            return None, None

    @staticmethod
    def addBalance(conn, player_name, balance, timestamp, x=None, z=None):
        c = conn.cursor()
        if x is not None and z is not None:
            c.execute('INSERT INTO player_balances (player_name, balance, timestamp, x, z) VALUES (?, ?, ?, ?, ?)',
                    (player_name, balance, timestamp, x, z))
        else:
            c.execute('INSERT INTO player_balances (player_name, balance, timestamp) VALUES (?, ?, ?)',
                    (player_name, balance, timestamp))
        conn.commit()

    @staticmethod
    def getPlayerBalances(conn, player_name):
        c = conn.cursor()
        c.execute('SELECT * FROM player_balances WHERE player_name = ? ORDER BY timestamp ASC', (player_name,))
        rows = c.fetchall()
        balances = []
        for row in rows:
            balance_dict = {
                'id': row[0],
                'player_name': row[1],
                'balance': row[2],
                'timestamp': row[3],
                'x': row[4],
                'z': row[5]
            }
            balances.append(balance_dict)
        return balances

    @staticmethod
    def addTradePotential(conn, player_name, profit, potentials, timestamp, amount, x=None, z=None):
        potentials = json.dumps(potentials)
        c = conn.cursor()
        if x is not None and z is not None:
            c.execute('INSERT INTO trade_potentials (player_name, profit, potentials, timestamp, amount, x, z) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (player_name, profit, potentials, timestamp, amount, x, z))
        else:
            c.execute('INSERT INTO trade_potentials (player_name, profit, potentials, timestamp, amount) VALUES (?, ?, ?, ?, ?)',
                    (player_name, profit, potentials, timestamp, amount))
        conn.commit()

    @staticmethod
    def getAllTradePotentials(conn):
        c = conn.cursor()
        c.execute('SELECT player_name, profit, potentials, amount, timestamp, x, z FROM trade_potentials')
        rows = c.fetchall()
        columns = [column[0] for column in c.description]
        trade_potentials = []
        for row in rows:
            trade_potentials.append(dict(zip(columns, row)))
        return trade_potentials

    @staticmethod
    def delBalances(conn):
        c = conn.cursor()
        
        c.execute('DELETE FROM player_balances')
        
        conn.commit()

    @staticmethod
    def purgeBalances(conn):
        c = conn.cursor()
        
        c.execute('SELECT DISTINCT player_name FROM player_balances')
        player_names = c.fetchall()
        
        for player_name_tuple in player_names:
            player_name = player_name_tuple[0]
            
            c.execute('SELECT id FROM player_balances WHERE player_name = ? ORDER BY timestamp DESC', (player_name,))
            balances = c.fetchall()
            
            if len(balances) > 2:
                for balance_id in balances[2:]:
                    c.execute('DELETE FROM player_balances WHERE id = ?', (balance_id[0],))
        
        conn.commit()

    @staticmethod
    def purgeBalance(conn, player_name):
        c = conn.cursor()

        c.execute('DELETE FROM player_balances WHERE player_name = ?', (player_name,))

        conn.commit()

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
    
    @staticmethod
    def timeAgo(epoch_time):
        current_time = time.time()
        
        diff_seconds = int(current_time - epoch_time)
        
        if diff_seconds < 60:
            return f"{diff_seconds} seconds ago"
        elif diff_seconds < 3600:
            minutes = diff_seconds // 60
            return f"{minutes} minutes ago"
        elif diff_seconds < 86400:
            hours = diff_seconds // 3600
            return f"{hours} hours ago"
        else:
            days = diff_seconds // 86400
            return f"{days} days ago"