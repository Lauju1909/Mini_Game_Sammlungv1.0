import pygame

class MenuManager:
    def __init__(self, audio_manager):
        self.audio = audio_manager
        self.current_menu = []
        self.index = 0
        self.active = True
        self.on_select_callback = None
        self.on_adjust_callback = None
        self.menu_stack = []
        self.current_title = None

    def set_menu(self, items, title=None, silent=False, interrupt=True):
        self.current_title = title
        if title and not silent:
            # Titel unterbricht, wenn gewünscht
            self.audio.speak(title, interrupt=interrupt, priority=1)
        self.current_menu = items
        self.index = 0
        if not silent:
            # Der erste Punkt sollte NICHT den Titel unterbrechen, den wir gerade gestartet haben.
            # Daher interrupt=False, wenn ein Titel da ist.
            should_interrupt = interrupt if not title else False
            self._announce_current(interrupt=should_interrupt)

    def clear_stack(self):
        self.menu_stack = []

    def push_menu(self, items, title=None, silent=False):
        self.menu_stack.append((list(self.current_menu), self.index, self.on_select_callback, self.on_adjust_callback, self.current_title))
        self.set_menu(items, title, silent=silent)

    def pop_menu(self):
        if self.menu_stack:
            self.current_menu, self.index, self.on_select_callback, self.on_adjust_callback, self.current_title = self.menu_stack.pop()
            if self.current_title:
                self.audio.speak(self.current_title, interrupt=True, priority=1)
            self._announce_current(interrupt=False if self.current_title else True)
            return True
        return False

    def handle_input(self, event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.index > 0:
                    self.index -= 1
                    self.audio.play_sound("click")
                    self._announce_current()
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_DOWN:
                if self.index < len(self.current_menu) - 1:
                    self.index += 1
                    self.audio.play_sound("click")
                    self._announce_current()
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_LEFT:
                if self.on_adjust_callback:
                    self.audio.play_sound("blip")
                    self.on_adjust_callback(self.current_menu[self.index], -1)
            elif event.key == pygame.K_RIGHT:
                if self.on_adjust_callback:
                    self.audio.play_sound("blip")
                    self.on_adjust_callback(self.current_menu[self.index], 1)
            elif event.key == pygame.K_RETURN:
                if self.on_select_callback:
                    self.audio.play_sound("confirm")
                    self.on_select_callback(self.current_menu[self.index])
            elif event.key == pygame.K_ESCAPE:
                if not self.pop_menu():
                    return "quit"
        return None

    def _announce_current(self, interrupt=True):
        if not self.current_menu:
            return
        item = self.current_menu[self.index]
        text = item if isinstance(item, str) else item.get("label", "Unbekannt")
        self.audio.speak(text, interrupt=interrupt)
