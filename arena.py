import pygame
import random
import math

class Arena:
    def __init__(self, width, height, sidebar_width=300):
        self.total_width = width
        self.height = height
        self.sidebar_width = sidebar_width
        self.play_width = width - sidebar_width
        self.obstacles = []
        self.rooms = [] # Track room rectangles for spawning/logic
        self.setup_arena()

    def setup_arena(self):
        self.obstacles = []
        self.rooms = []
        
        # Border walls
        self.obstacles.append(pygame.Rect(0, 0, self.play_width, 20)) # Top
        self.obstacles.append(pygame.Rect(0, self.height - 20, self.play_width, 20)) # Bottom
        self.obstacles.append(pygame.Rect(0, 0, 20, self.height)) # Left
        self.obstacles.append(pygame.Rect(self.play_width - 20, 0, 20, self.height)) # Right
        
        # DIVERSE HOUSE GENERATION
        # We'll randomly choose between different "Floor Plans"
        layout_type = random.choice(["grid", "central_hall", "l_shape"])
        
        if layout_type == "grid":
            rows, cols = 2, 3
            rw = (self.play_width - 40) // cols
            rh = (self.height - 40) // rows
            for r in range(rows):
                for c in range(cols):
                    self.rooms.append(pygame.Rect(20 + c*rw, 20 + r*rh, rw, rh))
            self.build_walls_from_rooms(door_spacing="wide")
            
        elif layout_type == "central_hall":
            hall_w = 120
            # Hallway in middle
            hall_rect = pygame.Rect(self.play_width//2 - hall_w//2, 20, hall_w, self.height - 40)
            self.rooms.append(hall_rect)
            # Rooms on left and right
            for r in range(3):
                rh = (self.height - 40) // 3
                self.rooms.append(pygame.Rect(20, 20 + r*rh, self.play_width//2 - hall_w//2 - 20, rh))
                self.rooms.append(pygame.Rect(self.play_width//2 + hall_w//2, 20 + r*rh, self.play_width//2 - hall_w//2 - 20, rh))
            self.build_walls_from_rooms(door_spacing="random")

        elif layout_type == "l_shape":
            # Large L-shaped corridor with rooms tucked in
            wing_w = self.play_width // 3
            self.rooms.append(pygame.Rect(20, 20, self.play_width - 40, wing_w)) # Top wing
            self.rooms.append(pygame.Rect(20, 20 + wing_w, wing_w, self.height - wing_w - 40)) # Left wing
            # Sub-rooms in the empty space
            sub_w = (self.play_width - wing_w - 40) // 2
            sub_h = (self.height - wing_w - 40) // 2
            for r in range(2):
                for c in range(2):
                    self.rooms.append(pygame.Rect(20 + wing_w + c*sub_w, 20 + wing_w + r*sub_h, sub_w, sub_h))
            self.build_walls_from_rooms(door_spacing="wide")

        # Add objects to EVERY room (except spawn corners)
        for i, room in enumerate(self.rooms):
            # Skip first and last room for spawn safety
            if i == 0 or i == len(self.rooms) - 1: continue
            
            # Place 2-4 objects per room
            for _ in range(random.randint(2, 4)):
                ow = random.randint(30, 60)
                oh = random.randint(30, 60)
                ox = random.randint(room.left + 25, room.right - ow - 25)
                oy = random.randint(room.top + 25, room.bottom - oh - 25)
                obj = pygame.Rect(ox, oy, ow, oh)
                # Check for overlap with walls
                if not any(obj.colliderect(w.inflate(10, 10)) for w in self.obstacles):
                    self.obstacles.append(obj)

    def build_walls_from_rooms(self, door_spacing="wide"):
        # Create walls between adjacent rooms
        wall_thickness = 15
        door_size = 85
        
        processed_pairs = set()
        for i, r1 in enumerate(self.rooms):
            for j, r2 in enumerate(self.rooms):
                if i >= j: continue
                
                # Check if rooms are adjacent
                # Horizontal adjacency
                if abs(r1.right - r2.left) < 5 and r1.top < r2.bottom and r2.top < r1.bottom:
                    # Wall on the right of r1
                    overlap_top = max(r1.top, r2.top)
                    overlap_bottom = min(r1.bottom, r2.bottom)
                    h = overlap_bottom - overlap_top
                    self.add_wall_with_doors(r1.right - wall_thickness//2, overlap_top, wall_thickness, h, "vertical", door_size, door_spacing)
                
                # Vertical adjacency
                elif abs(r1.bottom - r2.top) < 5 and r1.left < r2.right and r2.left < r1.right:
                    # Wall on the bottom of r1
                    overlap_left = max(r1.left, r2.left)
                    overlap_right = min(r1.right, r2.right)
                    w = overlap_right - overlap_left
                    self.add_wall_with_doors(overlap_left, r1.bottom - wall_thickness//2, w, wall_thickness, "horizontal", door_size, door_spacing)

    def add_wall_with_doors(self, x, y, w, h, orientation, door_size, spacing):
        # Always add at least 2 doors, spaced far apart
        if orientation == "horizontal":
            if spacing == "wide":
                d1_x = x + w * 0.2 - door_size // 2
                d2_x = x + w * 0.8 - door_size // 2
            else:
                d1_x = x + w * 0.3 - door_size // 2
                d2_x = x + w * 0.7 - door_size // 2
            
            # Wall segments
            self.obstacles.append(pygame.Rect(x, y, max(0, d1_x - x), h))
            self.obstacles.append(pygame.Rect(d1_x + door_size, y, max(0, d2_x - (d1_x + door_size)), h))
            self.obstacles.append(pygame.Rect(d2_x + door_size, y, max(0, (x + w) - (d2_x + door_size)), h))
        else:
            if spacing == "wide":
                d1_y = y + h * 0.2 - door_size // 2
                d2_y = y + h * 0.8 - door_size // 2
            else:
                d1_y = y + h * 0.3 - door_size // 2
                d2_y = y + h * 0.7 - door_size // 2
                
            self.obstacles.append(pygame.Rect(x, y, w, max(0, d1_y - y)))
            self.obstacles.append(pygame.Rect(x, d1_y + door_size, w, max(0, d2_y - (d1_y + door_size))))
            self.obstacles.append(pygame.Rect(x, d2_y + door_size, w, max(0, (y + h) - (d2_y + door_size))))

    def draw(self, screen):
        pygame.draw.rect(screen, (10, 10, 12), (0, 0, self.play_width, self.height))
        # Grid lines
        for x in range(0, self.play_width, 40):
            pygame.draw.line(screen, (18, 18, 22), (x, 0), (x, self.height))
        for y in range(0, self.height, 40):
            pygame.draw.line(screen, (18, 18, 22), (0, y), (self.play_width, y))
            
        for wall in self.obstacles:
            pygame.draw.rect(screen, (32, 32, 38), wall)
            pygame.draw.rect(screen, (0, 110, 190), wall, 1)

    def is_visible(self, pos1, pos2):
        dist = math.sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2)
        if dist < 1: return True
        steps = int(dist / 6) + 1
        dx = (pos2[0] - pos1[0]) / steps
        dy = (pos2[1] - pos1[1]) / steps
        for i in range(1, steps):
            check_pos = (pos1[0] + dx * i, pos1[1] + dy * i)
            for wall in self.obstacles:
                if wall.collidepoint(check_pos):
                    return False
        return True
