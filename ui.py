import pygame
from settings import *

class Slider:
    def __init__(self, x, y, w, min_val, max_val, initial, label, fmt="{:.1f}", step=None):
        self.rect = pygame.Rect(x, y, w, 20)
        self.min = min_val
        self.max = max_val
        self.value = initial
        self.label = label  # ключ текста
        self.fmt = fmt
        self.step = step
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._set_from_pos(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_pos(event.pos[0])
        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.rect.collidepoint(mx, my):
                step = self.step if self.step is not None else (self.max - self.min) / 100.0
                self.set_value(self.value + event.y * step)

    def _set_from_pos(self, mouse_x):
        t = (mouse_x - self.rect.x) / self.rect.width
        t = max(0.0, min(1.0, t))
        self.set_value(self.min + t * (self.max - self.min))

    def set_value(self, value):
        value = max(self.min, min(self.max, value))
        if self.step is not None:
            value = round(value / self.step) * self.step
        self.value = value

    def draw(self, screen, font, texts, lang):
        pygame.draw.rect(screen, UI_BG_COLOR, self.rect)
        fill_w = (self.value - self.min) / (self.max - self.min) * self.rect.width
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
        pygame.draw.rect(screen, UI_ACCENT_COLOR, fill_rect)
        pygame.draw.rect(screen, UI_COLOR, self.rect, 1)
        label_text = f"{texts[lang][self.label]}: {self.fmt.format(self.value)}"
        label_surf = font.render(label_text, True, UI_COLOR)
        screen.blit(label_surf, (self.rect.x, self.rect.y - 18))

class Button:
    def __init__(self, x, y, w, h, text_key, color=UI_ACCENT_COLOR):
        self.rect = pygame.Rect(x, y, w, h)
        self.text_key = text_key
        self.color = color
        self.clicked = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False

    def update(self):
        val = self.clicked
        self.clicked = False
        return val

    def draw(self, screen, font, texts, lang):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, UI_COLOR, self.rect, 2)
        text = texts[lang].get(self.text_key, self.text_key)
        text_surf = font.render(text, True, UI_COLOR)
        tw, th = text_surf.get_size()
        screen.blit(text_surf, (self.rect.x + (self.rect.w - tw)//2, self.rect.y + (self.rect.h - th)//2))

class UIPanel:
    def __init__(self, sim):
        self.sim = sim
        self.font = pygame.font.SysFont("Arial", 14)
        self.lang = 'ru'  # по умолчанию русский
        x = 12
        y = 34
        self.sliders = [
            Slider(x, y, 220, 0, 10000, sim.strength, "strength", fmt="{:.0f}"),
            Slider(x, y+40, 220, 20, 1000, sim.interaction_radius, "radius", fmt="{:.0f}"),
            Slider(x, y+80, 220, 10, 500, sim.target_dist, "target_dist", fmt="{:.1f}"),
            Slider(x, y+120, 220, 0.5, 1.0, sim.damping, "damping", fmt="{:.3f}"),
            Slider(x, y+160, 220, 0.0, 2.0, sim.wall_bounce, "wall_bounce", fmt="{:.2f}"),
            Slider(x, y+200, 220, 200, 20000, sim.magnet_strength, "magnet", fmt="{:.0f}"),
            Slider(x, y+240, 220, 1, 2000, sim.sim_fps, "sim_fps", fmt="{:.0f}", step=1),
            Slider(x, y+280, 220, 30, 240, sim.render_fps, "render_fps", fmt="{:.0f}", step=1),
        ]
        # Кнопки режимов взаимодействия
        self.mode_buttons = [
            Button(x, y+330, 100, 30, "mode_repel"),
            Button(x+110, y+330, 100, 30, "mode_attract"),
            Button(x+220, y+330, 100, 30, "mode_fixed"),
        ]
        # Кнопки действий
        self.action_buttons = [
            Button(x, y+370, 220, 30, "clear_walls"),
            Button(x, y+410, 220, 30, "clear_atoms"),
        ]
        # Кнопки регулировки Sim FPS (+/-)
        self.fps_buttons = [
            Button(x+235, y+234, 32, 30, "-"),
            Button(x+275, y+234, 32, 30, "+"),
        ]
        # Кнопки выбора заряда атома
        self.charge_buttons = [
            Button(x, y+475, 100, 28, "neutral"),
            Button(x+110, y+475, 100, 28, "positive"),
            Button(x+220, y+475, 100, 28, "negative"),
        ]
        # Кнопка включения/выключения кулоновских сил
        self.charge_toggle_button = Button(x, y+515, 220, 28, "magnet_toggle")
        # Кнопки внешнего притяжения (новые режимы)
        self.external_buttons = [
            Button(x, y+585, 100, 28, "attract_none"),
            Button(x+110, y+585, 100, 28, "attract_center"),
            Button(x+220, y+585, 100, 28, "attract_top"),
            Button(x, y+620, 100, 28, "attract_bottom"),
            Button(x+110, y+620, 100, 28, "attract_left"),
            Button(x+220, y+620, 100, 28, "attract_right"),
        ]
        # Кнопка переключения языка – помещаем в правый верхний угол
        self.lang_button = Button(UI_WIDTH - 100, 6, 80, 24, "language")

        # Собираем все кнопки в один список для удобства обработки событий и расчёта отступов
        self.all_buttons = (self.mode_buttons + self.action_buttons + self.fps_buttons +
                            self.charge_buttons + [self.charge_toggle_button] +
                            self.external_buttons + [self.lang_button])

        self.help_lines = []  # будет заполнено из TEXTS
        self.update_texts()  # установить начальные тексты

    def get_text(self, key):
        return TEXTS[self.lang].get(key, key)

    def toggle_language(self):
        self.lang = 'en' if self.lang == 'ru' else 'ru'
        self.update_texts()

    def update_texts(self):
        # Обновляем справку в зависимости от языка
        self.help_lines = TEXTS[self.lang]['help']

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)
        for b in self.all_buttons:
            b.handle_event(event)
        # Обработка нажатия на кнопку языка отдельно (чтобы не дублировать)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.lang_button.rect.collidepoint(event.pos):
                self.toggle_language()

    def update(self):
        self.sim.strength = self.sliders[0].value
        self.sim.interaction_radius = self.sliders[1].value
        self.sim.target_dist = self.sliders[2].value
        self.sim.damping = self.sliders[3].value
        self.sim.wall_bounce = self.sliders[4].value
        self.sim.magnet_strength = self.sliders[5].value
        self.sim.sim_fps = self.sliders[6].value
        self.sim.render_fps = self.sliders[7].value

        # Режимы взаимодействия
        if self.mode_buttons[0].update():
            self.sim.mode = MODE_REPEL
        if self.mode_buttons[1].update():
            self.sim.mode = MODE_ATTRACT
        if self.mode_buttons[2].update():
            self.sim.mode = MODE_KEEP_DIST

        # Действия
        if self.action_buttons[0].update():
            self.sim.clear_walls()
        if self.action_buttons[1].update():
            self.sim.clear_atoms()

        # FPS +/- (для sim_fps)
        if self.fps_buttons[0].update():
            self.sliders[6].set_value(self.sliders[6].value - 1)
            self.sim.sim_fps = self.sliders[6].value
        if self.fps_buttons[1].update():
            self.sliders[6].set_value(self.sliders[6].value + 1)
            self.sim.sim_fps = self.sliders[6].value

        # Заряд атома
        charge_map = [ATOM_NEUTRAL, ATOM_POSITIVE, ATOM_NEGATIVE]
        for i, btn in enumerate(self.charge_buttons):
            if btn.update():
                self.sim.selected_atom_charge = charge_map[i]

        # Включение/выключение кулоновских сил
        if self.charge_toggle_button.update():
            self.sim.charge_forces_enabled = not self.sim.charge_forces_enabled

        # Внешнее притяжение (новые режимы)
        external_map = [
            ATTRACT_NONE,
            ATTRACT_CENTER,
            ATTRACT_TOP_CENTER,
            ATTRACT_BOTTOM_CENTER,
            ATTRACT_LEFT_CENTER,
            ATTRACT_RIGHT_CENTER
        ]
        for i, btn in enumerate(self.external_buttons):
            if btn.update():
                self.sim.external_attraction = external_map[i]

        # Кнопка языка обрабатывается в handle_event

    def draw(self, screen):
        panel_rect = pygame.Rect(0, 0, UI_WIDTH, HEIGHT)
        pygame.draw.rect(screen, UI_BG_COLOR, panel_rect)
        pygame.draw.line(screen, UI_COLOR, (UI_WIDTH, 0), (UI_WIDTH, HEIGHT), 2)

        # Заголовок (слева)
        title = self.font.render(self.get_text('title'), True, UI_COLOR)
        screen.blit(title, (12, 8))

        # Кнопка языка (справа вверху)
        self.lang_button.draw(screen, self.font, TEXTS, self.lang)

        # Слайдеры
        for s in self.sliders:
            s.draw(screen, self.font, TEXTS, self.lang)

        # Кнопки режимов взаимодействия
        for b in self.mode_buttons:
            b.draw(screen, self.font, TEXTS, self.lang)

        # Кнопки действий
        for b in self.action_buttons:
            b.draw(screen, self.font, TEXTS, self.lang)

        # FPS кнопки
        for b in self.fps_buttons:
            b.draw(screen, self.font, TEXTS, self.lang)

        # Заголовок "Тип атома"
        atom_title = self.font.render(self.get_text('atom_type'), True, UI_COLOR)
        screen.blit(atom_title, (12, 488))

        # Кнопки заряда
        for i, btn in enumerate(self.charge_buttons):
            charges = [ATOM_NEUTRAL, ATOM_POSITIVE, ATOM_NEGATIVE]
            if self.sim.selected_atom_charge == charges[i]:
                btn.color = UI_ACCENT_COLOR
            else:
                btn.color = UI_BG_COLOR
            btn.draw(screen, self.font, TEXTS, self.lang)

        # Кнопка включения кулоновских сил
        self.charge_toggle_button.color = UI_ACCENT_COLOR if self.sim.charge_forces_enabled else UI_BG_COLOR
        self.charge_toggle_button.draw(screen, self.font, TEXTS, self.lang)

        # Заголовок "Внешнее притяжение"
        attract_title = self.font.render(self.get_text('external_attraction'), True, UI_COLOR)
        screen.blit(attract_title, (12, 596))

        # Кнопки внешнего притяжения
        external_modes = [
            ATTRACT_NONE,
            ATTRACT_CENTER,
            ATTRACT_TOP_CENTER,
            ATTRACT_BOTTOM_CENTER,
            ATTRACT_LEFT_CENTER,
            ATTRACT_RIGHT_CENTER
        ]
        for i, btn in enumerate(self.external_buttons):
            if self.sim.external_attraction == external_modes[i]:
                btn.color = UI_ACCENT_COLOR
            else:
                btn.color = UI_BG_COLOR
            btn.draw(screen, self.font, TEXTS, self.lang)

        # Справка – позиция вычисляется динамически
        max_bottom = max(b.rect.bottom for b in self.all_buttons)
        help_y = max_bottom + 20
        for i, line in enumerate(self.help_lines):
            text = self.font.render(line, True, UI_COLOR)
            screen.blit(text, (12, help_y + i * 18))