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

    def draw(self, screen, font):
        pygame.draw.rect(screen, UI_BG_COLOR, self.rect)
        fill_w = (self.value - self.min) / (self.max - self.min) * self.rect.width
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
        pygame.draw.rect(screen, UI_ACCENT_COLOR, fill_rect)
        pygame.draw.rect(screen, UI_COLOR, self.rect, 1)
        label_text = f"{self.label}: {self.fmt.format(self.value)}"
        label_surf = font.render(label_text, True, UI_COLOR)
        screen.blit(label_surf, (self.rect.x, self.rect.y - 18))

class Button:
    def __init__(self, x, y, w, h, text, color=UI_ACCENT_COLOR):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
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

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, UI_COLOR, self.rect, 2)
        text_surf = font.render(self.text, True, UI_COLOR)
        tw, th = text_surf.get_size()
        screen.blit(text_surf, (self.rect.x + (self.rect.w - tw)//2, self.rect.y + (self.rect.h - th)//2))

class UIPanel:
    def __init__(self, sim):
        self.sim = sim
        self.font = pygame.font.SysFont("Arial", 14)
        x = 12
        y = 34
        self.sliders = [
            Slider(x, y, 220, 0, 10000, sim.strength, "Strength", fmt="{:.0f}"),
            Slider(x, y+40, 220, 20, 1000, sim.interaction_radius, "Radius", fmt="{:.0f}"),
            Slider(x, y+80, 220, 10, 500, sim.target_dist, "Target Dist", fmt="{:.1f}"),
            Slider(x, y+120, 220, 0.5, 1.0, sim.damping, "Damping", fmt="{:.3f}"),
            Slider(x, y+160, 220, 0.0, 2.0, sim.wall_bounce, "Wall Bounce", fmt="{:.2f}"),
            Slider(x, y+200, 220, 200, 20000, sim.magnet_strength, "Magnet", fmt="{:.0f}"),
            Slider(x, y+240, 220, 1, 2000, sim.sim_fps, "Sim FPS", fmt="{:.0f}", step=1),
            Slider(x, y+280, 220, 30, 240, sim.render_fps, "Render FPS", fmt="{:.0f}", step=1),
        ]
        self.buttons = [
            Button(x, y+330, 100, 30, "Repel"),
            Button(x+110, y+330, 100, 30, "Attract"),
            Button(x+220, y+330, 100, 30, "Fixed"),
            Button(x, y+370, 220, 30, "Clear walls"),
            Button(x, y+410, 220, 30, "Clear atoms"),
            Button(x+235, y+234, 32, 30, "-"),
            Button(x+275, y+234, 32, 30, "+"),
            Button(x, y+475, 100, 28, "Neutral"),
            Button(x+110, y+475, 100, 28, "Red +"),
            Button(x+220, y+475, 100, 28, "Blue -"),
            Button(x, y+515, 220, 28, "Magnet +/-"),
            Button(x, y+585, 100, 28, "None"),
            Button(x+110, y+585, 100, 28, "Center"),
            Button(x+220, y+585, 100, 28, "Left"),
            Button(x, y+620, 100, 28, "Right"),
            Button(x+110, y+620, 100, 28, "Up"),
            Button(x+220, y+620, 100, 28, "Down"),
        ]
        self.charge_buttons = [
            (self.buttons[7], ATOM_NEUTRAL),
            (self.buttons[8], ATOM_POSITIVE),
            (self.buttons[9], ATOM_NEGATIVE),
        ]
        self.charge_toggle_button = self.buttons[10]
        self.external_buttons = [
            (self.buttons[11], ATTRACT_NONE),
            (self.buttons[12], ATTRACT_CENTER),
            (self.buttons[13], ATTRACT_LEFT),
            (self.buttons[14], ATTRACT_RIGHT),
            (self.buttons[15], ATTRACT_UP),
            (self.buttons[16], ATTRACT_DOWN),
        ]
        self.help_lines = [
            "Mouse:",
            "LMB - add selected atom",
            "Middle - cursor magnet",
            "RMB - remove nearest",
            "",
            "Keys:",
            "C/Delete - clear atoms",
            "N - add 10 atoms",
            "B / Shift+B - wall",
            "K - clear walls",
            "G - boundaries",
            "P - velocities",
            "Space - pause",
            "R - reset settings",
        ]

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)
        for b in self.buttons:
            b.handle_event(event)

    def update(self):
        self.sim.strength = self.sliders[0].value
        self.sim.interaction_radius = self.sliders[1].value
        self.sim.target_dist = self.sliders[2].value
        self.sim.damping = self.sliders[3].value
        self.sim.wall_bounce = self.sliders[4].value
        self.sim.magnet_strength = self.sliders[5].value
        self.sim.sim_fps = self.sliders[6].value
        self.sim.render_fps = self.sliders[7].value

        if self.buttons[0].update():
            self.sim.mode = MODE_REPEL
        if self.buttons[1].update():
            self.sim.mode = MODE_ATTRACT
        if self.buttons[2].update():
            self.sim.mode = MODE_KEEP_DIST
        if self.buttons[3].update():
            self.sim.clear_walls()
        if self.buttons[4].update():
            self.sim.clear_atoms()
        if self.buttons[5].update():
            self.sliders[6].set_value(self.sliders[6].value - 1)
            self.sim.sim_fps = self.sliders[6].value
        if self.buttons[6].update():
            self.sliders[6].set_value(self.sliders[6].value + 1)
            self.sim.sim_fps = self.sliders[6].value
        for button, atom_charge in self.charge_buttons:
            if button.update():
                self.sim.selected_atom_charge = atom_charge
        if self.charge_toggle_button.update():
            self.sim.charge_forces_enabled = not self.sim.charge_forces_enabled
        for button, attraction_mode in self.external_buttons:
            if button.update():
                self.sim.external_attraction = attraction_mode

    def draw(self, screen):
        panel_rect = pygame.Rect(0, 0, UI_WIDTH, HEIGHT)
        pygame.draw.rect(screen, UI_BG_COLOR, panel_rect)
        pygame.draw.line(screen, UI_COLOR, (UI_WIDTH, 0), (UI_WIDTH, HEIGHT), 2)
        title = self.font.render("Settings", True, UI_COLOR)
        screen.blit(title, (12, 8))
        for s in self.sliders:
            s.draw(screen, self.font)
        atom_title = self.font.render("Atom type", True, UI_COLOR)
        screen.blit(atom_title, (12, 488))
        attract_title = self.font.render("External attraction", True, UI_COLOR)
        screen.blit(attract_title, (12, 596))
        for button, atom_charge in self.charge_buttons:
            button.color = UI_ACCENT_COLOR if self.sim.selected_atom_charge == atom_charge else UI_BG_COLOR
        self.charge_toggle_button.color = UI_ACCENT_COLOR if self.sim.charge_forces_enabled else UI_BG_COLOR
        for button, attraction_mode in self.external_buttons:
            button.color = UI_ACCENT_COLOR if self.sim.external_attraction == attraction_mode else UI_BG_COLOR
        for b in self.buttons:
            b.draw(screen, self.font)
        help_y = max(button.rect.bottom for button in self.buttons) + 24
        for i, line in enumerate(self.help_lines):
            text = self.font.render(line, True, UI_COLOR)
            screen.blit(text, (12, help_y + i * 18))