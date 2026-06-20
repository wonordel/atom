import pygame
from settings import *

FONT_SIZE = 12
SLIDER_H = 16
ROW_DY = 34            # шаг между слайдерами (с учётом подписи сверху)
BTN_H = 18
FINE_BTN_SIZE = 18
COL_GAP = 14           # промежуток между колонками
PAD = 10               # внутренние отступы панели


class Slider:
    def __init__(self, x, y, w, min_val, max_val, initial, label, fmt="{:.1f}", step=None):
        self.rect = pygame.Rect(x, y, w, SLIDER_H)
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
        screen.blit(label_surf, (self.rect.x, self.rect.y - 15))


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
        pygame.draw.rect(screen, UI_COLOR, self.rect, 1)
        text = texts[lang].get(self.text_key, self.text_key)
        text_surf = font.render(text, True, UI_COLOR)
        tw, th = text_surf.get_size()
        # Если текст не влезает - подрезаем, чтобы не наезжать на соседние элементы
        max_w = self.rect.w - 4
        if tw > max_w:
            while tw > max_w and len(text) > 1:
                text = text[:-1]
                text_surf = font.render(text + "…", True, UI_COLOR)
                tw, th = text_surf.get_size()
        screen.blit(text_surf, (self.rect.x + (self.rect.w - tw) // 2, self.rect.y + (self.rect.h - th) // 2))


class UIPanel:
    def __init__(self, sim):
        self.sim = sim
        self.font = pygame.font.SysFont("Arial", FONT_SIZE)
        self.lang = 'ru'

        col_w = (UI_WIDTH - 2 * PAD - COL_GAP) // 2
        left_x = PAD
        right_x = PAD + col_w + COL_GAP

        y0 = 30

        # ---- Слайдеры в две колонки ----
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

        rows_per_col = (len(slider_params) + 1) // 2  # 5 слева, 4 справа

        # Ширина слайдера в колонке минус место для кнопок +/-
        slider_w = col_w - 2 * (FINE_BTN_SIZE + 4)

        self.sliders = []
        self.fine_buttons = []

        for i, (min_v, max_v, init, label, fmt, step) in enumerate(slider_params):
            col = 0 if i < rows_per_col else 1
            row = i if col == 0 else i - rows_per_col
            col_x = left_x if col == 0 else right_x
            y_pos = y0 + row * ROW_DY

            sl = Slider(col_x, y_pos, slider_w, min_v, max_v, init, label, fmt, step)
            self.sliders.append(sl)

            btn_x = col_x + slider_w + 4
            btn_minus = Button(btn_x, y_pos - 1, FINE_BTN_SIZE, SLIDER_H, "-", UI_ACCENT_COLOR)
            btn_plus = Button(btn_x + FINE_BTN_SIZE + 2, y_pos - 1, FINE_BTN_SIZE, SLIDER_H, "+", UI_ACCENT_COLOR)
            self.fine_buttons.append((i, btn_minus, btn_plus))

        sliders_bottom = y0 + rows_per_col * ROW_DY

        # ---- Кнопки режимов взаимодействия (3 в ряд на всю ширину) ----
        mode_y = sliders_bottom + 14
        mode_bw = (UI_WIDTH - 2 * PAD - 2 * 6) // 3
        self.mode_buttons = [
            Button(left_x, mode_y, mode_bw, BTN_H, "mode_repel"),
            Button(left_x + mode_bw + 6, mode_y, mode_bw, BTN_H, "mode_attract"),
            Button(left_x + 2 * (mode_bw + 6), mode_y, mode_bw, BTN_H, "mode_fixed"),
        ]

        # ---- Кнопки действий (2 колонки) ----
        action_y = mode_y + BTN_H + 8
        action_bw = col_w
        self.action_buttons = [
            Button(left_x, action_y, action_bw, BTN_H, "clear_walls"),
            Button(right_x, action_y, action_bw, BTN_H, "clear_atoms"),
        ]

        # ---- Тип атома: 3 кнопки в ряд ----
        charge_y = action_y + BTN_H + 18
        charge_bw = (UI_WIDTH - 2 * PAD - 2 * 6) // 3
        self.charge_buttons = [
            Button(left_x, charge_y, charge_bw, BTN_H, "neutral"),
            Button(left_x + charge_bw + 6, charge_y, charge_bw, BTN_H, "positive"),
            Button(left_x + 2 * (charge_bw + 6), charge_y, charge_bw, BTN_H, "negative"),
        ]
        self.charge_toggle_button = Button(left_x, charge_y + BTN_H + 6, UI_WIDTH - 2 * PAD, BTN_H, "magnet_toggle")

        # ---- Настройки спавна (угол + скорость, применяются к атомам ЛКМ) ----
        spawn_y = charge_y + 2 * BTN_H + 6 + 18
        spawn_params = [
            (SLIDER_SPAWN_ANGLE_MIN, SLIDER_SPAWN_ANGLE_MAX, sim.spawn_angle, "spawn_angle", "{:.0f}°", SLIDER_SPAWN_ANGLE_STEP),
            (SLIDER_SPAWN_SPEED_MIN, SLIDER_SPAWN_SPEED_MAX, sim.spawn_speed, "spawn_speed", "{:.0f}", SLIDER_SPAWN_SPEED_STEP),
        ]
        self.spawn_sliders = []
        self.spawn_fine_buttons = []
        for i, (min_v, max_v, init, label, fmt, step) in enumerate(spawn_params):
            col_x = left_x if i == 0 else right_x
            sl = Slider(col_x, spawn_y, slider_w, min_v, max_v, init, label, fmt, step)
            self.spawn_sliders.append(sl)
            btn_x = col_x + slider_w + 4
            btn_minus = Button(btn_x, spawn_y - 1, FINE_BTN_SIZE, SLIDER_H, "-", UI_ACCENT_COLOR)
            btn_plus = Button(btn_x + FINE_BTN_SIZE + 2, spawn_y - 1, FINE_BTN_SIZE, SLIDER_H, "+", UI_ACCENT_COLOR)
            self.spawn_fine_buttons.append((i, btn_minus, btn_plus))

        spawn_bottom = spawn_y + ROW_DY

        # ---- Внешнее притяжение: 2 колонки x 5 строк ----
        external_y = spawn_bottom + 14

        ext_bw = col_w
        ext_dy = BTN_H + 4
        ext_keys = [
            "attract_none", "attract_left",
            "attract_center", "attract_right",
            "attract_up", "attract_down",
            "attract_left_center", "attract_right_center",
            "attract_top_center", "attract_bottom_center",
        ]
        self.ext_buttons = []
        self.ext_map = [
            ATTRACT_NONE, ATTRACT_LEFT,
            ATTRACT_CENTER, ATTRACT_RIGHT,
            ATTRACT_UP, ATTRACT_DOWN,
            ATTRACT_LEFT_CENTER, ATTRACT_RIGHT_CENTER,
            ATTRACT_TOP_CENTER, ATTRACT_BOTTOM_CENTER,
        ]
        for i, key in enumerate(ext_keys):
            col = i % 2
            row = i // 2
            bx = left_x if col == 0 else right_x
            by = external_y + row * ext_dy
            self.ext_buttons.append(Button(bx, by, ext_bw, BTN_H, key))

        ext_bottom = external_y + 5 * ext_dy

        # ---- Кнопка языка (в углу) ----
        self.lang_button = Button(UI_WIDTH - 70, 6, 60, 20, "language")

        self.all_buttons = (self.mode_buttons + self.action_buttons + self.charge_buttons +
                            [self.charge_toggle_button] + self.ext_buttons + [self.lang_button])
        for _, bm, bp in self.fine_buttons:
            self.all_buttons += (bm, bp)
        for _, bm, bp in self.spawn_fine_buttons:
            self.all_buttons += (bm, bp)

        self.bottom_y = ext_bottom
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
        for s in self.spawn_sliders:
            s.handle_event(event)
        for b in self.all_buttons:
            b.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.lang_button.rect.collidepoint(event.pos):
                self.toggle_language()

    def update(self):
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

        self.sim.spawn_angle = self.spawn_sliders[0].value
        self.sim.spawn_speed = self.spawn_sliders[1].value

        for idx, btn_minus, btn_plus in self.spawn_fine_buttons:
            if btn_minus.update():
                self.spawn_sliders[idx].set_value(self.spawn_sliders[idx].value - self.spawn_sliders[idx].step)
            if btn_plus.update():
                self.spawn_sliders[idx].set_value(self.spawn_sliders[idx].value + self.spawn_sliders[idx].step)

        for idx, btn_minus, btn_plus in self.fine_buttons:
            if btn_minus.update():
                self.sliders[idx].set_value(self.sliders[idx].value - self.sliders[idx].step)
            if btn_plus.update():
                self.sliders[idx].set_value(self.sliders[idx].value + self.sliders[idx].step)

        if self.mode_buttons[0].update():
            self.sim.mode = MODE_REPEL
        if self.mode_buttons[1].update():
            self.sim.mode = MODE_ATTRACT
        if self.mode_buttons[2].update():
            self.sim.mode = MODE_KEEP_DIST

        if self.action_buttons[0].update():
            self.sim.clear_walls()
        if self.action_buttons[1].update():
            self.sim.clear_atoms()

        charge_map = [ATOM_NEUTRAL, ATOM_POSITIVE, ATOM_NEGATIVE]
        for i, btn in enumerate(self.charge_buttons):
            if btn.update():
                self.sim.selected_atom_charge = charge_map[i]

        if self.charge_toggle_button.update():
            self.sim.charge_forces_enabled = not self.sim.charge_forces_enabled

        for i, btn in enumerate(self.ext_buttons):
            if btn.update():
                self.sim.external_attraction = self.ext_map[i]

    def draw(self, screen):
        panel_rect = pygame.Rect(0, 0, UI_WIDTH, HEIGHT)
        pygame.draw.rect(screen, UI_BG_COLOR, panel_rect)
        pygame.draw.line(screen, UI_COLOR, (UI_WIDTH, 0), (UI_WIDTH, HEIGHT), 2)

        title = self.font.render(self.get_text('title'), True, UI_COLOR)
        screen.blit(title, (PAD, 8))
        self.lang_button.draw(screen, self.font, TEXTS, self.lang)

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
        screen.blit(atom_title, (PAD, self.charge_buttons[0].rect.y - 16))
        for i, btn in enumerate(self.charge_buttons):
            charges = [ATOM_NEUTRAL, ATOM_POSITIVE, ATOM_NEGATIVE]
            btn.color = UI_ACCENT_COLOR if self.sim.selected_atom_charge == charges[i] else UI_BG_COLOR
            btn.draw(screen, self.font, TEXTS, self.lang)

        self.charge_toggle_button.color = UI_ACCENT_COLOR if self.sim.charge_forces_enabled else UI_BG_COLOR
        self.charge_toggle_button.draw(screen, self.font, TEXTS, self.lang)

        spawn_title = self.font.render(self.get_text('spawn_settings'), True, UI_COLOR)
        screen.blit(spawn_title, (PAD, self.spawn_sliders[0].rect.y - 16))
        for i, sl in enumerate(self.spawn_sliders):
            sl.draw(screen, self.font, TEXTS, self.lang)
            _, btn_minus, btn_plus = self.spawn_fine_buttons[i]
            btn_minus.draw(screen, self.font, TEXTS, self.lang)
            btn_plus.draw(screen, self.font, TEXTS, self.lang)

        attract_title = self.font.render(self.get_text('external_attraction'), True, UI_COLOR)
        screen.blit(attract_title, (PAD, self.ext_buttons[0].rect.y - 16))

        for i, btn in enumerate(self.ext_buttons):
            btn.color = UI_ACCENT_COLOR if self.sim.external_attraction == self.ext_map[i] else UI_BG_COLOR
            btn.draw(screen, self.font, TEXTS, self.lang)

        # Справка — всегда ниже всех элементов панели
        help_y = self.bottom_y + 16
        for i, line in enumerate(self.help_lines):
            text = self.font.render(line, True, UI_COLOR)
            screen.blit(text, (PAD, help_y + i * 15))
