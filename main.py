import pygame
import sys
import time
from settings import *
from simulator import Simulator
from atom import Atom
from ui import UIPanel

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Atoms - LMB add, middle magnet")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 14)

sim = Simulator()
ui = UIPanel(sim)
sim_accumulator = 0.0
sim_steps_this_second = 0
actual_sim_fps = 0
sim_fps_timer = 0.0

key_repeat_delay = 0.2
key_repeat_interval = 0.03
key_timers = {}

def handle_key_continuous():
    current_time = pygame.time.get_ticks() / 1000.0
    keys = pygame.key.get_pressed()
    actions = {
        pygame.K_q: (lambda: setattr(sim, 'strength', sim.strength * 0.95), None, 0.95, None),
        pygame.K_e: (lambda: setattr(sim, 'strength', sim.strength * 1.05), None, 1.05, None),
        pygame.K_w: (lambda: setattr(sim, 'interaction_radius', max(20, sim.interaction_radius * 0.95)), None, 0.95, None),
        pygame.K_s: (lambda: setattr(sim, 'interaction_radius', min(1000, sim.interaction_radius * 1.05)), None, 1.05, None),
        pygame.K_a: (lambda: setattr(sim, 'target_dist', max(10, sim.target_dist * 0.95)), None, 0.95, None),
        pygame.K_d: (lambda: setattr(sim, 'target_dist', min(500, sim.target_dist * 1.05)), None, 1.05, None),
        pygame.K_z: (lambda: setattr(sim, 'damping', max(0.5, sim.damping * 0.98)), None, 0.98, None),
        pygame.K_x: (lambda: setattr(sim, 'damping', min(1.0, sim.damping * 1.02)), None, 1.02, None),
    }
    shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
    for key, (inc_func, dec_func, inc_step, dec_step) in actions.items():
        if keys[key]:
            if key not in key_timers:
                key_timers[key] = current_time
                if inc_func: inc_func()
            else:
                elapsed = current_time - key_timers[key]
                if elapsed > key_repeat_delay:
                    repeats = int((elapsed - key_repeat_delay) // key_repeat_interval) + 1
                    for _ in range(repeats):
                        if inc_func: inc_func()
                    key_timers[key] = current_time - (elapsed - key_repeat_delay) % key_repeat_interval
        else:
            if key in key_timers: del key_timers[key]

running = True
while running:
    dt = clock.tick(max(1, int(sim.render_fps))) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        ui.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                sim.clear_atoms()
            elif event.key == pygame.K_n:
                sim.add_random_atoms(10)
            elif event.key == pygame.K_DELETE:
                sim.clear_atoms()
            elif event.key == pygame.K_b:
                mx, my = pygame.mouse.get_pos()
                if event.mod & pygame.KMOD_SHIFT:
                    sim.add_wall_at_cursor(mx, my, horizontal=True)
                else:
                    sim.add_wall_at_cursor(mx, my, horizontal=False)
            elif event.key == pygame.K_k:
                sim.clear_walls()
            elif event.key == pygame.K_g:
                sim.boundaries_enabled = not sim.boundaries_enabled
                sim.update_active_walls()
            elif event.key == pygame.K_p:
                sim.show_velocities = not sim.show_velocities
            elif event.key == pygame.K_SPACE:
                sim.paused = not sim.paused
            elif event.key == pygame.K_r:
                sim.strength = DEFAULT_STRENGTH
                sim.target_dist = DEFAULT_TARGET_DIST
                sim.interaction_radius = DEFAULT_INTERACTION_RADIUS
                sim.damping = DEFAULT_DAMPING
                sim.wall_bounce = DEFAULT_WALL_BOUNCE
                sim.magnet_strength = MAGNET_STRENGTH
                sim.sim_fps = DEFAULT_SIM_FPS
                sim.render_fps = DEFAULT_RENDER_FPS
                sim.external_attraction = ATTRACT_NONE
                sim.selected_atom_charge = ATOM_NEUTRAL
                sim.charge_forces_enabled = True
                for i, s in enumerate(ui.sliders):
                    if i == 0: s.value = sim.strength
                    elif i == 1: s.value = sim.interaction_radius
                    elif i == 2: s.value = sim.target_dist
                    elif i == 3: s.value = sim.damping
                    elif i == 4: s.value = sim.wall_bounce
                    elif i == 5: s.value = sim.magnet_strength
                    elif i == 6: s.value = sim.sim_fps
                    elif i == 7: s.value = sim.render_fps
            elif event.key == pygame.K_l:
                ui.toggle_language()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if event.button == 1 and mx > UI_WIDTH:   # LMB – add atom at click point
                sim.add_atom(mx, my)
            elif event.button == 3 and mx > UI_WIDTH: # RMB – remove nearest
                sim.remove_nearest_atom(mx, my)

    # Magnet on held middle mouse button (button 2)
    mx, my = pygame.mouse.get_pos()
    sim.set_magnet(pygame.mouse.get_pressed()[1] and mx > UI_WIDTH, mx, my)

    handle_key_continuous()
    ui.update()

    sim_fps_timer += dt
    if sim.paused:
        sim_accumulator = 0.0
    else:
        sim_step = 1.0 / max(1.0, sim.sim_fps)
        sim_accumulator += dt
        steps = 0
        deadline = time.perf_counter() + SIM_TIME_BUDGET_MS / 1000.0
        while (
            sim_accumulator >= sim_step
            and steps < MAX_SIM_STEPS_PER_FRAME
            and time.perf_counter() < deadline
        ):
            sim.update(sim_step)
            sim_accumulator -= sim_step
            steps += 1
        max_accumulator = sim_step * MAX_SIM_STEPS_PER_FRAME
        if sim_accumulator > max_accumulator:
            sim_accumulator = max_accumulator
        sim_steps_this_second += steps

    if sim_fps_timer >= 1.0:
        actual_sim_fps = int(sim_steps_this_second / sim_fps_timer)
        sim_steps_this_second = 0
        sim_fps_timer = 0.0

    screen.fill(BACKGROUND_COLOR)
    # Walls
    for wall in sim.active_walls:
        pygame.draw.line(screen, WALL_COLOR, (wall.x1, wall.y1), (wall.x2, wall.y2), 3)
    # Atoms
    for atom in sim.atoms:
        if atom.charge == ATOM_POSITIVE:
            atom_color = ATOM_POSITIVE_COLOR
            atom_label = "+"
        elif atom.charge == ATOM_NEGATIVE:
            atom_color = ATOM_NEGATIVE_COLOR
            atom_label = "-"
        else:
            atom_color = ATOM_NEUTRAL_COLOR
            atom_label = ""
        atom_pos = (int(atom.x), int(atom.y))
        pygame.draw.circle(screen, atom_color, atom_pos, atom.radius)
        if atom_label:
            label_surf = font.render(atom_label, True, UI_COLOR)
            label_rect = label_surf.get_rect(center=atom_pos)
            screen.blit(label_surf, label_rect)
        if sim.show_velocities:
            sx, sy = atom.vx * 0.5, atom.vy * 0.5
            if sx != 0 or sy != 0:
                pygame.draw.line(screen, VELOCITY_VECTOR_COLOR,
                                 (int(atom.x), int(atom.y)),
                                 (int(atom.x + sx), int(atom.y + sy)), 1)
    ui.draw(screen)
    fps_text = font.render(f"FPS: {int(clock.get_fps())}/{int(sim.render_fps)}", True, UI_COLOR)
    screen.blit(fps_text, (WIDTH - 150, 10))
    sim_fps_text = font.render(f"Sim FPS: {actual_sim_fps}/{int(sim.sim_fps)}", True, UI_COLOR)
    screen.blit(sim_fps_text, (WIDTH - 160, 30))
    pygame.display.flip()

pygame.quit()
sys.exit()