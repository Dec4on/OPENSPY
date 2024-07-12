from concurrent.futures import ThreadPoolExecutor
import time
from libs.utilities import Utilities
import requests

ignore_players = []

def fetch_player_chunk(sublist, max_retries=2, delay=1.5):
    global ignore_players

    sublist = [x for x in sublist if x not in ignore_players]

    attempt = 0
    while attempt < max_retries:
        try:
            result = ','.join(sublist)
            player_chunk = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/players?query={result}')
            if player_chunk is not None:
                for player in player_chunk:
                    if player is None:
                        print(player)
                return player_chunk
        except Exception:
            pass
        attempt += 1
        time.sleep(delay)
    
    result = []
    for x in sublist:
        response = requests.get(f'https://api.earthmc.net/v3/aurora/players?query={x}')
        if response.status_code == 404:
            ignore_players.append(x)
            continue
        result.append(response.json()[0])
        
    return result


def getTrades(conn):
    trade_size = 1
    try:
        player_fetch_list = Utilities.fetchAPI('http://melo.pylex.xyz:9155/api/online_players')
        if not player_fetch_list:
            return None
        
        player_list = []
        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = []
            for i in range(0, len(player_fetch_list), 100):
                sublist = player_fetch_list[i:i + 100]
                futures.append(executor.submit(fetch_player_chunk, sublist))        
            for future in futures:
                if future.result():
                    player_list.extend(future.result())
    except Exception:
        return None

    timestamp = int(time.time())

    for player in player_list:
        player_data = Utilities.fetchPlayerData(conn, player['name'])
        if player_data and player_data['x'] is not None and player_data['z'] is not None:
            Utilities.addBalance(conn, player['name'], player['stats']['balance'], timestamp, player_data['x'], player_data['z'])
            continue
        Utilities.addBalance(conn, player['name'], player['stats']['balance'], timestamp)

    differences = []
    for player in player_list:
        balances = Utilities.getPlayerBalances(conn, player['name'])

        if len(balances) >= 2:
            now_balance = balances[-1]
            last_balance = balances[-2]

            difference = abs(now_balance['balance'] - last_balance['balance'])
            if difference < trade_size:
                continue
            profit = now_balance['balance'] > last_balance['balance']

            differences.append({
                'difference': difference,
                'profit': profit,
                'name': player['name'],
                'timestamp': now_balance['timestamp'],
                'x': now_balance['x'],
                'z': now_balance['z']
            })

    for player in differences:
        potentials = []
        for bal in differences:
            if player['difference'] == bal['difference'] and player['profit'] != bal['profit']:
                potentials.append(bal['name'])

        if potentials:
            Utilities.addTradePotential(conn, player['name'], player['profit'], potentials, player['timestamp'], player['difference'], player['x'], player['z'])

    Utilities.purgeBalances(conn)