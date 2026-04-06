import pygame

class Arena:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.obstacles = []
        self.setup_arena()

    def setup_arena(self):
        # Symmetrical walls for cover
        # Format: (x, y, width, height)
        # Center walls
        self.obstacles.append(pygame.Rect(self.width // 2 - 20, 100, 40, 150))
        self.obstacles.append(pygame.Rect(self.width // 2 - 20, self.height - 250, 40, 150))
        
        # Player side cover
        self.obstacles.append(pygame.Rect(200, 200, 30, 100))
        self.obstacles.append(pygame.Rect(200, self.height - 300, 30, 100))
        
        # AI side cover
        self.obstacles.append(pygame.Rect(self.width - 230, 200, 30, 100))
        self.obstacles.append(pygame.Rect(self.width - 230, self.height - 300, 30, 100))
        
        # Border walls (optional, let's keep it simple)
        # Top/Bottom/Left/Right
        self.border_walls = [
            pygame.Rect(0, 0, self.width, 20),
            pygame.Rect(0, self.height - 20, self.width, 20),
            pygame.Rect(0, 0, 20, self.height),
            pygame.Rect(self.width - 20, 0, 20, self.height)
        ]
        self.obstacles.extend(self.border_walls)

    def draw(self, screen):
        # Draw background
        screen.fill((30, 30, 30))
        
        # Draw grid for tactical feel
        grid_size = 50
        for x in range(0, self.width, grid_size):
            pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, self.height))
        for y in range(0, self.height, grid_size):
            pygame.draw.line(screen, (40, 40, 40), (0, y), (self.width, y))
            
        # Draw obstacles
        for wall in self.obstacles:
            pygame.draw.rect(screen, (80, 80, 80), wall)
            # Add a slight highlight to walls
            pygame.draw.rect(screen, (100, 100, 100), wall, 2)

    def is_visible(self, pos1, pos2):
        # Check if line of sight between pos1 and pos2 is clear of obstacles
        # Very simple raycast
        steps = 20
        dx = (pos2[0] - pos1[0]) / steps
        dy = (pos2[1] - pos1[1]) / steps
        for i in range(1, steps):
            check_pos = (pos1[0] + dx * i, pos1[1] + dy * i)
            for wall in self.obstacles:
                if wall.collidepoint(check_pos):
                    return False
        return True
