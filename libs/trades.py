from concurrent.futures import ThreadPoolExecutor
import time
from libs.utilities import Utilities

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
                futures.append(executor.submit(Utilities.fetch_player_chunk, sublist))        
            for future in futures:
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
            # print({
            #     'name': player['name'],
            #     'profit': player['profit'],
            #     'potentials': potentials,
            #     'amount': player['difference']
            # })

    Utilities.purgeBalances(conn)

# epoch_last_trade = int(time.time())
# conn = Utilities.DBstart()

# while True:
#     epoch_now = int(time.time())
#     if epoch_now - epoch_last_trade >= 10:
#         epoch_last_trade = epoch_now
#         getTrades(conn)
#     time.sleep(0.2)
