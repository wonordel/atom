class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def collide_segment(self, x0, y0, x1, y1, radius, restitution):
        """Проверяет пересечение отрезка [x0,y0]-[x1,y1] с бесконечной стеной,
           возвращает (new_x, new_y, new_vx, new_vy, collided)"""
        # Вертикальная стена
        if abs(self.x1 - self.x2) < 1e-5:
            wall_x = self.x1
            if (x0 - wall_x) * (x1 - wall_x) > 0:
                return x1, y1, None, None, False
            t = (wall_x - x0) / (x1 - x0) if abs(x1 - x0) > 1e-6 else 0
            if not (0 <= t <= 1):
                return x1, y1, None, None, False
            ix = wall_x
            iy = y0 + t * (y1 - y0)
            if abs(ix - wall_x) > radius:
                return x1, y1, None, None, False
            nx = 1.0 if wall_x > 0 else -1.0
            ny = 0.0
            new_x = wall_x + nx * radius
            new_y = iy
            vx = (x1 - x0) / (t + 1e-9)
            vy = (y1 - y0) / (t + 1e-9)
            vdotn = vx * nx + vy * ny
            new_vx = (vx - 2 * vdotn * nx) * restitution
            new_vy = (vy - 2 * vdotn * ny) * restitution
            return new_x, new_y, new_vx, new_vy, True

        # Горизонтальная стена
        elif abs(self.y1 - self.y2) < 1e-5:
            wall_y = self.y1
            if (y0 - wall_y) * (y1 - wall_y) > 0:
                return x1, y1, None, None, False
            t = (wall_y - y0) / (y1 - y0) if abs(y1 - y0) > 1e-6 else 0
            if not (0 <= t <= 1):
                return x1, y1, None, None, False
            ix = x0 + t * (x1 - x0)
            iy = wall_y
            if abs(iy - wall_y) > radius:
                return x1, y1, None, None, False
            nx = 0.0
            ny = 1.0 if wall_y > 0 else -1.0
            new_x = ix
            new_y = wall_y + ny * radius
            vx = (x1 - x0) / (t + 1e-9)
            vy = (y1 - y0) / (t + 1e-9)
            vdotn = vx * nx + vy * ny
            new_vx = (vx - 2 * vdotn * nx) * restitution
            new_vy = (vy - 2 * vdotn * ny) * restitution
            return new_x, new_y, new_vx, new_vy, True

        return x1, y1, None, None, False