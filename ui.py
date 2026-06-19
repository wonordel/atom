import pygame
from settings import *

class Slider:
    def __init__(self, x, y, w, min_val, max_val, initial, label, fmt="{:.1f}", step=None):
        self.rect = pygame.Rect(x, y, w, 20)
        self.min = min_val
        self.max = max_val
        self.value = initial
        self.label = label
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
        label_text = texts[lang].get(self.label, self.label)
        label_text = f"{label_text}: {self.fmt.format(self.value)}"
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
        self.lang = 'ru'
        x = 12
        y0 = 30
        dy = 44                # увеличенный шаг между слайдерами
        slider_w = 280         # немного уменьшили ширину, чтобы влезли кнопки
        btn_size = FINE_TUNE_BUTTON_SIZE

        # Список слайдеров с их параметрами (границы, шаги и т.д.)
        slider_params = [
            (SLIDER_STRENGTH_MIN, SLIDER_STRENGTH_MAX, sim.strength, "strength", "{:.0f}", SLIDER_STRENGTH_STEP),
            (SLIDER_INTERACTION_RADIUS_MIN, SLIDER_INTERACTION_RADIUS_MAX, sim.interaction_radius, "radius", "{:.0f}", SLIDER_INTERACTION_RADIUS_STEP),
            (SLIDER_TARGET_DIST_MIN, SLIDER_TARGET_DIST_MAX, sim.target_dist, "target_dist", "{:.1f}", SLIDER_TARGET_DIST_STEP),
            (SLIDER_DAMPING_MIN, SLIDER_DAMPING_MAX, sim.damping, "damping", "{:.3f}", SLIDER_DAMPING_STEP),
            (SLIDER_WALL_BOUNCE_MIN, SLIDER_WALL_BOUNCE_MAX, sim.wall_bounce, "wall_bounce", "{:.2f}", SLIDER_WALL_BOUNCE_STEP),
            (SLIDER_ATOM_RADIUS_MIN, SLIDER_ATOM_RADIUS_MAX, sim.atom_radius, "atom_radius", "{:.0f}", SLIDER_ATOM_RADIUS_STEP),
            (SLIDER_MAGNET_STRENGTH_MIN, SLIDER_MAGNET_STRENGTH_MAX, sim.magnet_strength, "magnet", "{:.0f}", SLIDER_MAGNET_STRENGTH_STEP),
            (SLIDER_SIM_FPS_MIN, SLIDER_SIM_FPS_MAX, sim.sim_fps, "sim_fps", "{:.0f}", SLIDER_SIM_FPS_STEP),
            (SLIDER_RENDER_FPS_MIN, SLIDER_RENDER_FPS_MAX, sim.render_fps, "render_fps", "{:.0f}", SLIDER_RENDER_FPS_STEP),
        ]

        self.sliders = []
        self.fine_buttons = []  # список кортежей (slider_index, btn_minus, btn_plus)

        for i, (min_v, max_v, init, label, fmt, step) in enumerate(slider_params):
            y_pos = y0 + i * dy
            sl = Slider(x, y_pos, slider_w, min_v, max_v, init, label, fmt, step)
            self.sliders.append(sl)

            # Кнопки + и – справа от слайдера
            btn_x = x + slider_w + 6
            btn_y = y_pos
            btn_minus = Button(btn_x, btn_y, btn_size, 20, "-", UI_ACCENT_COLOR)
            btn_plus = Button(btn_x + btn_size + 4, btn_y, btn_size, 20, "+", UI_ACCENT_COLOR)
            self.fine_buttons.append((i, btn_minus, btn_plus))

        # Кнопки режимов взаимодействия
        mode_y = y0 + 9*dy + 12
        bw = 120
        self.mode_buttons = [
            Button(x, mode_y, bw, 25, "mode_repel"),
            Button(x + bw + 8, mode_y, bw, 25, "mode_attract"),
            Button(x + 2*(bw+8), mode_y, bw, 25, "mode_fixed"),
        ]

        # Кнопки действий
        action_y = mode_y + 25 + 10
        self.action_buttons = [
            Button(x, action_y, slider_w + 2*btn_size + 8, 25, "clear_walls"),
            Button(x, action_y + 30, slider_w + 2*btn_size + 8, 25, "clear_atoms"),
        ]

        # Кнопки выбора заряда
        charge_y = action_y + 30 + 30 + 10
        self.charge_buttons = [
            Button(x, charge_y, bw, 25, "neutral"),
            Button(x + bw + 8, charge_y, bw, 25, "positive"),
            Button(x + 2*(bw+8), charge_y, bw, 25, "negative"),
        ]
        self.charge_toggle_button = Button(x, charge_y + 30, slider_w + 2*btn_size + 8, 25, "magnet_toggle")

        # Кнопки внешнего притяжения
        external_y = charge_y + 30 + 30
        bw2 = 120
        gap = 8
        self.ext_buttons = [
            Button(x, external_y, bw2, 25, "attract_none"),
            Button(x + bw2 + gap, external_y, bw2, 25, "attract_center"),
            Button(x + 2*(bw2+gap), external_y, bw2, 25, "attract_left"),
        ]
        row2_y = external_y + 25 + 4
        self.ext_buttons += [
            Button(x, row2_y, bw2, 25, "attract_right"),
            Button(x + bw2 + gap, row2_y, bw2, 25, "attract_up"),
            Button(x + 2*(bw2+gap), row2_y, bw2, 25, "attract_down"),
        ]
        row3_y = row2_y + 25 + 4
        self.ext_buttons += [
            Button(x, row3_y, bw2, 25, "attract_left_center"),
            Button(x + bw2 + gap, row3_y, bw2, 25, "attract_right_center"),
            Button(x + 2*(bw2+gap), row3_y, bw2, 25, "attract_top_center"),
        ]
        row4_y = row3_y + 25 + 4
        self.ext_buttons.append(Button(x, row4_y, bw2, 25, "attract_bottom_center"))

        # Кнопка языка
        self.lang_button = Button(UI_WIDTH - 100, 6, 80, 24, "language")

        # Собираем все кнопки для обработки и расчёта нижней границы
        self.all_buttons = (self.mode_buttons + self.action_buttons + self.charge_buttons +
                            [self.charge_toggle_button] + self.ext_buttons + [self.lang_button])
        # Добавляем кнопки точной настройки в общий список
        for _, bm, bp in self.fine_buttons:
            self.all_buttons += (bm, bp)

        self.help_lines = []
        self.update_texts()

    def get_text(self, key):
        return TEXTS[self.lang].get(key, key)

    def toggle_language(self):
        self.lang = 'en' if self.lang == 'ru' else 'ru'
        self.update_texts()

    def update_texts(self):
        self.help_lines = TEXTS[self.lang]['help']

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)
        for b in self.all_buttons:
            b.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.lang_button.rect.collidepoint(event.pos):
                self.toggle_language()

    def update(self):
        # Обновление значений слайдеров
        for i, sl in enumerate(self.sliders):
            if i == 0:
                self.sim.strength = sl.value
            elif i == 1:
                self.sim.interaction_radius = sl.value
            elif i == 2:
                self.sim.target_dist = sl.value
            elif i == 3:
                self.sim.damping = sl.value
            elif i == 4:
                self.sim.wall_bounce = sl.value
            elif i == 5:
                self.sim.set_atom_radius(sl.value)
            elif i == 6:
                self.sim.magnet_strength = sl.value
            elif i == 7:
                self.sim.sim_fps = sl.value
            elif i == 8:
                self.sim.render_fps = sl.value

        # Обработка кнопок точной настройки
        for idx, btn_minus, btn_plus in self.fine_buttons:
            if btn_minus.update():
                self.sliders[idx].set_value(self.sliders[idx].value - self.sliders[idx].step)
            if btn_plus.update():
                self.sliders[idx].set_value(self.sliders[idx].value + self.sliders[idx].step)

        # Режимы
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

        # Заряды
        charge_map = [ATOM_NEUTRAL, ATOM_POSITIVE, ATOM_NEGATIVE]
        for i, btn in enumerate(self.charge_buttons):
            if btn.update():
                self.sim.selected_atom_charge = charge_map[i]

        if self.charge_toggle_button.update():
            self.sim.charge_forces_enabled = not self.sim.charge_forces_enabled

        # Внешнее притяжение
        ext_map = [
            ATTRACT_NONE, ATTRACT_CENTER, ATTRACT_LEFT,
            ATTRACT_RIGHT, ATTRACT_UP, ATTRACT_DOWN,
            ATTRACT_LEFT_CENTER, ATTRACT_RIGHT_CENTER,
            ATTRACT_TOP_CENTER, ATTRACT_BOTTOM_CENTER
        ]
        for i, btn in enumerate(self.ext_buttons):
            if btn.update():
                self.sim.external_attraction = ext_map[i]

    def draw(self, screen):
        panel_rect = pygame.Rect(0, 0, UI_WIDTH, HEIGHT)
        pygame.draw.rect(screen, UI_BG_COLOR, panel_rect)
        pygame.draw.line(screen, UI_COLOR, (UI_WIDTH, 0), (UI_WIDTH, HEIGHT), 2)

        title = self.font.render(self.get_text('title'), True, UI_COLOR)
        screen.blit(title, (12, 8))
        self.lang_button.draw(screen, self.font, TEXTS, self.lang)

        # Слайдеры и их кнопки +/-
        for i, sl in enumerate(self.sliders):
            sl.draw(screen, self.font, TEXTS, self.lang)
            _, btn_minus, btn_plus = self.fine_buttons[i]
            btn_minus.draw(screen, self.font, TEXTS, self.lang)
            btn_plus.draw(screen, self.font, TEXTS, self.lang)

        for b in self.mode_buttons:
            b.draw(screen, self.font, TEXTS, self.lang)
        for b in self.action_buttons:
            b.draw(screen, self.font, TEXTS, self.lang)

        atom_title = self.font.render(self.get_text('atom_type'), True, UI_COLOR)
        screen.blit(atom_title, (12, self.charge_buttons[0].rect.y - 20))
        for i, btn in enumerate(self.charge_buttons):
            charges = [ATOM_NEUTRAL, ATOM_POSITIVE, ATOM_NEGATIVE]
            btn.color = UI_ACCENT_COLOR if self.sim.selected_atom_charge == charges[i] else UI_BG_COLOR
            btn.draw(screen, self.font, TEXTS, self.lang)

        self.charge_toggle_button.color = UI_ACCENT_COLOR if self.sim.charge_forces_enabled else UI_BG_COLOR
        self.charge_toggle_button.draw(screen, self.font, TEXTS, self.lang)

        attract_title = self.font.render(self.get_text('external_attraction'), True, UI_COLOR)
        screen.blit(attract_title, (12, self.ext_buttons[0].rect.y - 20))

        ext_modes = [
            ATTRACT_NONE, ATTRACT_CENTER, ATTRACT_LEFT,
            ATTRACT_RIGHT, ATTRACT_UP, ATTRACT_DOWN,
            ATTRACT_LEFT_CENTER, ATTRACT_RIGHT_CENTER,
            ATTRACT_TOP_CENTER, ATTRACT_BOTTOM_CENTER
        ]
        for i, btn in enumerate(self.ext_buttons):
            btn.color = UI_ACCENT_COLOR if self.sim.external_attraction == ext_modes[i] else UI_BG_COLOR
            btn.draw(screen, self.font, TEXTS, self.lang)

        # Справка – всегда ниже всех элементов
        max_bottom = max(b.rect.bottom for b in self.all_buttons)
        help_y = max_bottom + 20
        for i, line in enumerate(self.help_lines):
            text = self.font.render(line, True, UI_COLOR)
            screen.blit(text, (12, help_y + i * 18))