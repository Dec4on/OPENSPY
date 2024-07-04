from datetime import datetime, timezone, timedelta
import time
from concurrent.futures import ThreadPoolExecutor
from libs.utilities import Utilities


class Pirate:
    @staticmethod
    def findRuiningTowns(offset=0):
        ger_now = datetime.now(timezone.utc) + timedelta(hours=2)

        if ger_now.hour >= 12:
            next_midday = ger_now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1) + timedelta(days=offset)
        else:
            next_midday = ger_now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=offset)

        time_difference = next_midday - ger_now
        seconds_remaining = int(time_difference.total_seconds())

        epoch_now = int(time.time())

        all_towns = Utilities.fetchAPI('https://api.earthmc.net/v3/aurora/towns')
        town_list = [x['name'] for x in all_towns]
        
        try:
            completed_town_list = []
            with ThreadPoolExecutor(max_workers=40) as executor:
                futures = []
                for i in range(0, len(town_list), 100):
                    sublist = town_list[i:i + 100]
                    futures.append(executor.submit(Utilities.fetch_town_chunk, sublist))
                for index, future in enumerate(futures):
                    completed_town_list.extend(future.result())

            player_fetch_list = []
            for town in completed_town_list:
                if town['status']['isOpen'] and not town['status']['isRuined']:
                    for res in town['residents']:
                        player_fetch_list.append(res['name'])

            completed_player_list = []
            with ThreadPoolExecutor(max_workers=40) as executor:
                futures = []
                for i in range(0, len(player_fetch_list), 100):
                    sublist = player_fetch_list[i:i + 100]
                    futures.append(executor.submit(Utilities.fetch_player_chunk, sublist))        
                for index, future in enumerate(futures):
                    completed_player_list.extend(future.result())
        except Exception:
            return None
        
        completed_player_dict = {}
        for res in completed_player_list:
            completed_player_dict[res['name']] = res

        piratable_towns = []
        for town in completed_town_list:
            if town['status']['isOpen'] and not town['status']['isRuined']:
                try:
                    if town['mayor']['name'].startswith('NPC'):
                        continue

                    if (epoch_now + seconds_remaining) - int(completed_player_dict[town['mayor']['name']]['timestamps']['lastOnline'] / 1000) < 3628800:
                        continue

                    sorted_residents = sorted(town['residents'], key=lambda res: completed_player_dict[res['name']]['timestamps']['lastOnline'], reverse=True)
                    not_ruining = False
                    for res in sorted_residents:
                        if res['name'] == town['mayor']['name']:
                            continue
                        if (epoch_now + seconds_remaining) - int(completed_player_dict[res['name']]['timestamps']['lastOnline'] / 1000) < 3628800:
                            not_ruining = True

                    if not_ruining == True:
                        continue

                    piratable_towns.append(town)
                except Exception:
                    continue

        return piratable_towns