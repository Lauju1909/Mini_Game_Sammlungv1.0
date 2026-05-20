import pygame
import sys
import os

# Mock the audio and other managers if necessary
class MockAudioManager:
    def speak(self, text, **kwargs): print(f"Speaking: {text}")
    def play_sound(self, name, **kwargs): print(f"Playing: {name}")
    def set_volumes(self, sfx, music): pass
    def set_speech_rate(self, rate): pass
    def set_speech_volume(self, vol): pass

class MockHighscoreManager:
    def __init__(self): pass
    def get_highscores(self, game_id): return []
    def add_highscore(self, game_id, name, score): pass

class MockSettingsManager:
    def __init__(self): pass
    def get(self, key): return None
    def set(self, key, value): pass

# Add core and root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'core'))

# Import games
from games.golden_mic import GoldenMic
from games.beat_reaktor import BeatReaktor
from games.number_guess import NumberGuess
from games.sound_memo import SoundMemo
from games.math_blitz import MathBlitz
from games.key_storm import KeyStorm
from games.simon_says import SimonSays
from games.stereo_catch import StereoCatch
from games.bomb_defuser import BombDefuser
from games.safe_cracker import SafeCracker
from games.audio_maze import AudioMaze
from games.echolot import Echolot
from games.blind_farm import BlindFarm
from games.space_flight import SpaceFlight
from games.word_snake import WordSnake
from games.sound_quiz import SoundQuiz
from games.letter_salad import LetterSalad
from games.capital_hunter import CapitalHunter
from games.audio_bowling import AudioBowling
from games.rps_extreme import RPS_Extreme
from games.code_breaker import CodeBreaker
from games.sound_catch import SoundCatch
from games.speed_dial import SpeedDial
from games.mole_master import MoleMaster
from games.rhythm_master import RhythmMaster
from games.reaction_blitz import ReactionBlitz
from games.audio_archery import AudioArchery
from games.audio_slots import AudioSlots
from games.audio_sequence import AudioSequence
from games.echo_hunter import EchoHunter
from games.animal_radar import AnimalRadar
from games.morse_runner import MorseRunner
from games.ticking_clock import TickingClock
from games.pitch_perfect import PitchPerfect
from games.mystery_door import MysteryDoor
from games.frequency_jammer import FrequencyJammer
from games.stairs_of_fate import StairsOfFate
from games.sound_weaver import SoundWeaver
from games.beat_matcher import BeatMatcher
from games.audio_balance import AudioBalance

games = [
    GoldenMic, BeatReaktor, NumberGuess, SoundMemo, MathBlitz, KeyStorm, SimonSays, StereoCatch,
    BombDefuser, SafeCracker, AudioMaze, Echolot, BlindFarm, SpaceFlight, WordSnake, SoundQuiz,
    LetterSalad, CapitalHunter, AudioBowling, RPS_Extreme, CodeBreaker, SoundCatch, SpeedDial,
    MoleMaster, RhythmMaster, ReactionBlitz, AudioArchery, AudioSlots, AudioSequence, EchoHunter,
    AnimalRadar, MorseRunner, TickingClock, PitchPerfect, MysteryDoor, FrequencyJammer, StairsOfFate,
    SoundWeaver, BeatMatcher, AudioBalance
]

pygame.init()
pygame.display.set_mode((10, 10)) # Small window for testing

audio = MockAudioManager()
highscores = MockHighscoreManager()
settings = MockSettingsManager()

print(f"Testing initialization of {len(games)} games...")

for game_class in games:
    try:
        game = game_class(audio, highscores, settings, "Tester")
        print(f"Successfully initialized: {game_class.__name__}")
    except Exception as e:
        print(f"FAILED to initialize {game_class.__name__}: {e}")

pygame.quit()
