from libs.utilities import Utilities
import time


def send_notification(title, message):
    from plyer import notification # type: ignore

    notification.notify(
        title=title,
        message=message,
        app_name='OpenSpy',
        timeout=10
    )

def protectPlayerCheck(conn, player):
    all_player_data = Utilities.fetchAllPlayerData(conn)

    target_player_data = None
    for plr in all_player_data:
        if plr['name'].lower() == player.lower():
            target_player_data = plr

    if not target_player_data:
        return
    
    x = target_player_data['x']
    z = target_player_data['z']
    epoch_now = int(time.time()) 

    threats = []
    for plr in all_player_data:
        x2 = plr['x']
        z2 = plr['z']

        distance = ((x - x2) ** 2 + (z - z2) ** 2) ** 0.5
        if distance < 300 and epoch_now - plr['timestamp'] and plr['name'].lower() != player.lower():
            threats.append(plr['name'])
    
    if threats:
        threats_string = Utilities.listToString(threats)
        send_notification(f"Players Approaching {player}", f"Player(s): {threats_string}.")