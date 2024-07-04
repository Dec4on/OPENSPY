from concurrent.futures import ThreadPoolExecutor
from libs.utilities import Utilities
import time


class Victims:
    @staticmethod
    def fetch_location(sublist):
        try:
            result = ','.join(sublist)
            response = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/location?query={result}')
        except Exception:
            return None
        return response

    @staticmethod
    def findVictims():
        epoch_now = int(time.time())

        conn = Utilities.DBstart()
        list_player_data = Utilities.fetchAllPlayerData(conn)
        list_player_data = [player for player in list_player_data if epoch_now - player['timestamp'] < 3]
        player_fetch_list = []
        for player in list_player_data:
            x = player['x']
            z = player['z']
            player_fetch_list.append(f'{x};{z}')

        try:
            futures = []
            with ThreadPoolExecutor(max_workers=40) as executor:
                for i in range(0, len(player_fetch_list), 100):
                    sublist = player_fetch_list[i:i + 100]
                    futures.append((i, executor.submit(Victims.fetch_location, sublist)))

                futures.sort(key=lambda x: x[0])
                
                completed_location_list = []
                for _, future in futures:
                    completed_location_list.extend(future.result())
        except Exception as e:
            print(f'exception: {e}')
            return None
        
        victims = []
        index = 0
        for player in completed_location_list:
            if player['isWilderness'] == True:
                x = int(player['location']['x'])
                z = int(player['location']['z'])
                victim = {
                    'name': list_player_data[index]['name'],
                    'x': x,
                    'z': z,
                    'timestamp': list_player_data[index]['timestamp']
                }
                victims.append(victim)
            index += 1

        conn.close()
        return victims