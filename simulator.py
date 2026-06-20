import math
import random
import sys
from settings import *
from entities import Atom, Wall


# ----------------------------------------------------------------------
# Функция для параллельного вычисления сил для группы атомов (CPU)
# ----------------------------------------------------------------------
def _compute_forces_for_group(args):
    """
    args: (indices, atoms_list, strength, interaction_radius,
           min_dist, mode, target_dist, charge_forces_enabled)
    Возвращает список кортежей (i, fx, fy) для каждого i в indices.
    """
    (indices, atoms, strength, interaction_radius,
     min_dist, mode, target_dist, charge_forces_enabled) = args

    n = len(atoms)
    result = []
    for i in indices:
        a1 = atoms[i]
        fx_total = 0.0
        fy_total = 0.0
        for j in range(n):
            if i == j:
                continue
            a2 = atoms[j]
            dx = a2.x - a1.x
            dy = a2.y - a1.y
            dist_sq = dx*dx + dy*dy
            if dist_sq < 1e-6 or dist_sq > interaction_radius*interaction_radius:
                continue
            dist = math.sqrt(dist_sq)
            r = max(dist, min_dist)
            dir_x = dx / r
            dir_y = dy / r

            if charge_forces_enabled and a1.charge != 0 and a2.charge != 0:
                mag = strength / r
                if a1.charge == a2.charge:
                    fx = -mag * dir_x
                    fy = -mag * dir_y
                else:
                    fx = mag * dir_x
                    fy = mag * dir_y
                fx_total += fx
                fy_total += fy
                continue

            if mode == MODE_REPEL:
                mag = strength / r
                fx = -mag * dir_x
                fy = -mag * dir_y
            elif mode == MODE_ATTRACT:
                mag = strength / r
                fx = mag * dir_x
                fy = mag * dir_y
            else:  # MODE_KEEP_DIST
                delta = r - target_dist
                stiffness = strength * 0.05 / max(target_dist, 1.0)
                max_mag = strength * 2.0 / max(min_dist, 1.0)
                mag = max(-max_mag, min(max_mag, stiffness * delta))
                fx = mag * dir_x
                fy = mag * dir_y

            fx_total += fx
            fy_total += fy

        result.append((i, fx_total, fy_total))
    return result


class Simulator:
    def __init__(self, pool=None):
        self.atoms = []
        self.walls = []
        self.boundaries_enabled = True
        self.mode = MODE_ATTRACT
        self.strength = DEFAULT_STRENGTH
        self.target_dist = DEFAULT_TARGET_DIST
        self.interaction_radius = DEFAULT_INTERACTION_RADIUS
        self.damping = DEFAULT_DAMPING
        self.min_dist = DEFAULT_MIN_DIST
        self.wall_bounce = DEFAULT_WALL_BOUNCE
        self.show_velocities = False
        self.paused = False
        self.magnet_strength = MAGNET_STRENGTH
        self.sim_fps = DEFAULT_SIM_FPS
        self.render_fps = DEFAULT_RENDER_FPS
        self.external_attraction = ATTRACT_NONE
        self.selected_atom_charge = ATOM_NEUTRAL
        self.charge_forces_enabled = True
        self.magnet_active = False
        self.magnet_x = 0
        self.magnet_y = 0
        self.atom_radius = DEFAULT_ATOM_RADIUS
        self.spawn_angle = DEFAULT_SPAWN_ANGLE
        self.spawn_speed = DEFAULT_SPAWN_SPEED

        # Пул процессов (передаётся из main)
        self.pool = pool
        if self.pool is None:
            import multiprocessing as mp
            self.pool = mp.Pool(processes=mp.cpu_count())

        self.boundary_walls = [
            Wall(UI_WIDTH, 0, WIDTH, 0),
            Wall(UI_WIDTH, HEIGHT, WIDTH, HEIGHT),
            Wall(UI_WIDTH, 0, UI_WIDTH, HEIGHT),
            Wall(WIDTH, 0, WIDTH, HEIGHT)
        ]
        self.update_active_walls()
        self.add_random_atoms(40)

    def set_atom_radius(self, new_radius):
        self.atom_radius = new_radius
        for atom in self.atoms:
            atom.radius = new_radius

    def update_active_walls(self):
        if self.boundaries_enabled:
            self.active_walls = self.boundary_walls + self.walls
        else:
            self.active_walls = self.walls[:]

    def add_random_atoms(self, count):
        for _ in range(count):
            x = random.uniform(UI_WIDTH + 50, WIDTH - 50)
            y = random.uniform(50, HEIGHT - 50)
            self.atoms.append(Atom(x, y, charge=ATOM_NEUTRAL, radius=self.atom_radius))

    def add_atom(self, x, y, charge=None):
        if charge is None:
            charge = self.selected_atom_charge
        atom = Atom(x, y, charge=charge, radius=self.atom_radius)
        angle_rad = math.radians(self.spawn_angle)
        atom.vx = math.cos(angle_rad) * self.spawn_speed
        atom.vy = -math.sin(angle_rad) * self.spawn_speed
        self.atoms.append(atom)

    def add_atom_outside(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        margin = random.uniform(30, 100)
        if side == 'top':
            x = random.uniform(-margin, WIDTH + margin)
            y = -margin
        elif side == 'bottom':
            x = random.uniform(-margin, WIDTH + margin)
            y = HEIGHT + margin
        elif side == 'left':
            x = -margin
            y = random.uniform(-margin, HEIGHT + margin)
        else:
            x = WIDTH + margin
            y = random.uniform(-margin, HEIGHT + margin)
        atom = Atom(x, y, charge=ATOM_NEUTRAL, radius=self.atom_radius)
        atom.vx = random.uniform(-50, 50)
        atom.vy = random.uniform(-50, 50)
        self.atoms.append(atom)

    def clear_atoms(self):
        self.atoms.clear()

    def remove_nearest_atom(self, mx, my):
        if not self.atoms:
            return
        nearest = min(self.atoms, key=lambda a: (a.x - mx)**2 + (a.y - my)**2)
        self.atoms.remove(nearest)

    def add_wall_at_cursor(self, mx, my, horizontal=False):
        if horizontal:
            wall = Wall(UI_WIDTH, my, WIDTH, my)
        else:
            wall = Wall(mx, 0, mx, HEIGHT)
        self.walls.append(wall)
        self.update_active_walls()

    def clear_walls(self):
        self.walls.clear()
        self.update_active_walls()

    def compute_force(self, a1, a2):
        # Последовательный расчёт (используется при малом числе атомов)
        dx = a2.x - a1.x
        dy = a2.y - a1.y
        dist_sq = dx*dx + dy*dy
        if dist_sq < 1e-6:
            return 0.0, 0.0
        dist = math.sqrt(dist_sq)
        if dist > self.interaction_radius:
            return 0.0, 0.0
        r = max(dist, self.min_dist)
        dir_x = dx / r
        dir_y = dy / r
        if self.charge_forces_enabled and a1.charge != 0 and a2.charge != 0:
            mag = self.strength / r
            if a1.charge == a2.charge:
                fx = -mag * dir_x
                fy = -mag * dir_y
            else:
                fx = mag * dir_x
                fy = mag * dir_y
            return fx, fy
        if self.mode == MODE_REPEL:
            mag = self.strength / r
            fx = -mag * dir_x
            fy = -mag * dir_y
        elif self.mode == MODE_ATTRACT:
            mag = self.strength / r
            fx = mag * dir_x
            fy = mag * dir_y
        else:
            delta = r - self.target_dist
            stiffness = self.strength * 0.05 / max(self.target_dist, 1.0)
            max_mag = self.strength * 2.0 / max(self.min_dist, 1.0)
            mag = max(-max_mag, min(max_mag, stiffness * delta))
            fx = mag * dir_x
            fy = mag * dir_y
        return fx, fy

    def set_magnet(self, active, mx=0, my=0):
        self.magnet_active = active
        self.magnet_x = mx
        self.magnet_y = my

    def _keep_atom_inside_bounds(self, atom):
        left = UI_WIDTH + atom.radius
        right = WIDTH - atom.radius
        top = atom.radius
        bottom = HEIGHT - atom.radius

        if atom.x < left:
            atom.x = left
            if atom.vx < 0:
                atom.vx = -atom.vx * self.wall_bounce
        elif atom.x > right:
            atom.x = right
            if atom.vx > 0:
                atom.vx = -atom.vx * self.wall_bounce

        if atom.y < top:
            atom.y = top
            if atom.vy < 0:
                atom.vy = -atom.vy * self.wall_bounce
        elif atom.y > bottom:
            atom.y = bottom
            if atom.vy > 0:
                atom.vy = -atom.vy * self.wall_bounce

    def _resolve_atom_collisions(self):
        restitution = 0.2
        for _ in range(4):
            for i in range(len(self.atoms)):
                a = self.atoms[i]
                for j in range(i + 1, len(self.atoms)):
                    b = self.atoms[j]
                    dx = b.x - a.x
                    dy = b.y - a.y
                    min_dist = a.radius + b.radius
                    dist_sq = dx * dx + dy * dy

                    if dist_sq >= min_dist * min_dist:
                        continue

                    if dist_sq < 1e-9:
                        angle = (i * 37 + j * 17) % 360
                        nx = math.cos(math.radians(angle))
                        ny = math.sin(math.radians(angle))
                        dist = 0.0
                    else:
                        dist = math.sqrt(dist_sq)
                        nx = dx / dist
                        ny = dy / dist

                    overlap = min_dist - dist
                    inv_mass_a = 1.0 / a.mass
                    inv_mass_b = 1.0 / b.mass
                    inv_mass_sum = inv_mass_a + inv_mass_b
                    if inv_mass_sum <= 0:
                        continue

                    correction = overlap / inv_mass_sum
                    a.x -= nx * correction * inv_mass_a
                    a.y -= ny * correction * inv_mass_a
                    b.x += nx * correction * inv_mass_b
                    b.y += ny * correction * inv_mass_b

                    rel_vx = b.vx - a.vx
                    rel_vy = b.vy - a.vy
                    vel_along_normal = rel_vx * nx + rel_vy * ny
                    if vel_along_normal < 0:
                        impulse = -(1.0 + restitution) * vel_along_normal / inv_mass_sum
                        impulse_x = impulse * nx
                        impulse_y = impulse * ny
                        a.vx -= impulse_x * inv_mass_a
                        a.vy -= impulse_y * inv_mass_a
                        b.vx += impulse_x * inv_mass_b
                        b.vy += impulse_y * inv_mass_b

            if self.boundaries_enabled:
                for atom in self.atoms:
                    self._keep_atom_inside_bounds(atom)

    def update(self, dt):
        if self.paused:
            return
        dt = max(0.000001, min(dt, 1.0))
        max_speed = 0.0
        for atom in self.atoms:
            s = max(abs(atom.vx), abs(atom.vy))
            if s > max_speed:
                max_speed = s
        n_substeps = max(1, int(math.ceil(max_speed * dt / 5.0))) if max_speed > 0 else 1
        n_substeps = min(n_substeps, 5)
        sub_dt = dt / n_substeps
        for _ in range(n_substeps):
            self._update_step(sub_dt)

    def _update_step(self, dt):
        n = len(self.atoms)
        if n == 0:
            return

        forces_x = [0.0] * n
        forces_y = [0.0] * n

        # Выбор способа расчёта сил (CPU: последовательно или через multiprocessing)
        PARALLEL_THRESHOLD = 80
        if n < PARALLEL_THRESHOLD:
            for i in range(n):
                for j in range(i + 1, n):
                    fx, fy = self.compute_force(self.atoms[i], self.atoms[j])
                    forces_x[i] += fx
                    forces_y[i] += fy
                    forces_x[j] -= fx
                    forces_y[j] -= fy
        else:
            # Разбиваем индексы на группы по числу процессов
            num_procs = self.pool._processes
            indices = list(range(n))
            group_size = max(1, n // num_procs)
            groups = [indices[i:i+group_size] for i in range(0, n, group_size)]
            args_list = []
            for group in groups:
                args = (group, self.atoms, self.strength, self.interaction_radius,
                        self.min_dist, self.mode, self.target_dist, self.charge_forces_enabled)
                args_list.append(args)
            results = self.pool.map(_compute_forces_for_group, args_list)
            for res in results:
                for i, fx, fy in res:
                    forces_x[i] += fx
                    forces_y[i] += fy

        # ---- Внешнее притяжение (последовательно) ----
        if self.external_attraction != ATTRACT_NONE:
            if self.external_attraction == ATTRACT_CENTER:
                cx = (UI_WIDTH + WIDTH) * 0.5
                cy = HEIGHT * 0.5
                for i, atom in enumerate(self.atoms):
                    dx = cx - atom.x
                    dy = cy - atom.y
                    dist_sq = dx*dx + dy*dy
                    if dist_sq < 1e-6:
                        continue
                    dist = math.sqrt(dist_sq)
                    factor = self.strength / dist
                    forces_x[i] += factor * dx
                    forces_y[i] += factor * dy

            elif self.external_attraction == ATTRACT_LEFT:
                for i in range(n):
                    forces_x[i] -= self.strength
            elif self.external_attraction == ATTRACT_RIGHT:
                for i in range(n):
                    forces_x[i] += self.strength
            elif self.external_attraction == ATTRACT_UP:
                for i in range(n):
                    forces_y[i] -= self.strength
            elif self.external_attraction == ATTRACT_DOWN:
                for i in range(n):
                    forces_y[i] += self.strength

            elif self.external_attraction == ATTRACT_LEFT_CENTER:
                tx = float(UI_WIDTH)
                ty = HEIGHT * 0.5
                for i, atom in enumerate(self.atoms):
                    dx = tx - atom.x
                    dy = ty - atom.y
                    dist_sq = dx*dx + dy*dy
                    if dist_sq < 1e-6:
                        continue
                    dist = math.sqrt(dist_sq)
                    factor = self.strength / dist
                    forces_x[i] += factor * dx
                    forces_y[i] += factor * dy

            elif self.external_attraction == ATTRACT_RIGHT_CENTER:
                tx = float(WIDTH)
                ty = HEIGHT * 0.5
                for i, atom in enumerate(self.atoms):
                    dx = tx - atom.x
                    dy = ty - atom.y
                    dist_sq = dx*dx + dy*dy
                    if dist_sq < 1e-6:
                        continue
                    dist = math.sqrt(dist_sq)
                    factor = self.strength / dist
                    forces_x[i] += factor * dx
                    forces_y[i] += factor * dy

            elif self.external_attraction == ATTRACT_TOP_CENTER:
                tx = (UI_WIDTH + WIDTH) * 0.5
                ty = 0.0
                for i, atom in enumerate(self.atoms):
                    dx = tx - atom.x
                    dy = ty - atom.y
                    dist_sq = dx*dx + dy*dy
                    if dist_sq < 1e-6:
                        continue
                    dist = math.sqrt(dist_sq)
                    factor = self.strength / dist
                    forces_x[i] += factor * dx
                    forces_y[i] += factor * dy

            elif self.external_attraction == ATTRACT_BOTTOM_CENTER:
                tx = (UI_WIDTH + WIDTH) * 0.5
                ty = float(HEIGHT)
                for i, atom in enumerate(self.atoms):
                    dx = tx - atom.x
                    dy = ty - atom.y
                    dist_sq = dx*dx + dy*dy
                    if dist_sq < 1e-6:
                        continue
                    dist = math.sqrt(dist_sq)
                    factor = self.strength / dist
                    forces_x[i] += factor * dx
                    forces_y[i] += factor * dy

        # ---- Магнит ----
        if self.magnet_active:
            for i, atom in enumerate(self.atoms):
                dx = self.magnet_x - atom.x
                dy = self.magnet_y - atom.y
                dist_sq = dx*dx + dy*dy
                if dist_sq < 1e-6:
                    continue
                dist = math.sqrt(dist_sq)
                mag = self.magnet_strength / (dist + 20.0)
                mag = min(mag, 2000.0) * DEFAULT_SIM_FPS
                forces_x[i] += mag * dx / dist
                forces_y[i] += mag * dy / dist

        # ---- Обновление скоростей и позиций ----
        damping_factor = self.damping ** (dt * DEFAULT_SIM_FPS)
        for i, atom in enumerate(self.atoms):
            ax = forces_x[i] / atom.mass
            ay = forces_y[i] / atom.mass
            atom.vx += ax * dt
            atom.vy += ay * dt
            atom.vx *= damping_factor
            atom.vy *= damping_factor
            old_x, old_y = atom.x, atom.y
            new_x = atom.x + atom.vx * dt
            new_y = atom.y + atom.vy * dt
            for wall in self.active_walls:
                nx, ny, nvx, nvy, hit = wall.collide_segment(old_x, old_y, new_x, new_y, atom.radius, self.wall_bounce)
                if hit:
                    new_x, new_y = nx, ny
                    atom.vx, atom.vy = nvx, nvy
                    break
            atom.x, atom.y = new_x, new_y
            if self.boundaries_enabled:
                self._keep_atom_inside_bounds(atom)
            else:
                if atom.x < 0: atom.x = 0; atom.vx = -atom.vx * 0.5
                if atom.x > WIDTH: atom.x = WIDTH; atom.vx = -atom.vx * 0.5
                if atom.y < 0: atom.y = 0; atom.vy = -atom.vy * 0.5
                if atom.y > HEIGHT: atom.y = HEIGHT; atom.vy = -atom.vy * 0.5

        self._resolve_atom_collisions()