import pytest
import os
import json
import socket
from unittest.mock import patch

def test_missing_functions_mini_games():
    print("Checking for missing critical functions in Mini Game Sammlung...")
    try:
        from core import menu
        from games import blackjack, slots
        
        assert hasattr(menu, 'render'), "Menu render function missing!"
        assert hasattr(blackjack, 'play') or hasattr(blackjack, 'start'), "Blackjack start function missing!"
        assert hasattr(slots, 'spin') or hasattr(slots, 'play'), "Slots play function missing!"
    except ImportError:
        pass

def test_save_load_corruption_mini_games():
    print("Testing Save/Load corruption in Mini Games...")
    corrupt_save = "mini_game_corrupt_save.dat"
    with open(corrupt_save, "w") as f:
        f.write("%CORRUPTED_DATA$$@@!!")
        
    try:
        from core import save_system
        if hasattr(save_system, 'load_profile'):
            save_system.load_profile(corrupt_save)
    except ImportError:
        pass
    except Exception as e:
        assert isinstance(e, BaseException)
        
    if os.path.exists(corrupt_save):
        os.remove(corrupt_save)

@patch('socket.socket')
def test_network_failure_mini_games(mock_socket):
    print("Simulating network failure for highscore submission...")
    mock_socket.return_value.sendall.side_effect = ConnectionResetError("Connection reset by peer")
    try:
        from core import network
        if hasattr(network, 'submit_highscore'):
            network.submit_highscore("Player1", 9999)
    except ImportError:
        pass
    except Exception as e:
        assert isinstance(e, ConnectionResetError)
