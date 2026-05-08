import pygame
import localization

class TextInput:
    def __init__(self, audio_manager, prompt, callback):
        self.audio = audio_manager
        self.prompt = prompt
        self.callback = callback
        self.text = ""
        self.active = True
        self.audio.speak(prompt, priority=2)

    def handle_input(self, event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if len(self.text) > 0:
                    self.active = False
                    self.callback(self.text)
                else:
                    self.audio.speak(localization.get_text("input_empty_error"))
            elif event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
                    self.audio.speak(self.text if self.text else localization.get_text("input_cleared"))
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                self.callback(None)
            else:
                char = event.unicode
                if char.isalnum() or char in " _-":
                    self.text += char
                    self.audio.speak(char)

    def update(self):
        pass
