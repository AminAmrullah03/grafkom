import pygame
import cairo
import numpy as np
import random

# Game settings
GAME_WIDTH = 700
GAME_HEIGHT = 700
SPEED = 5
SPACE_SIZE = 25
SNAKE_COLORS = [(0, 255, 0), (0, 0, 255)]  #Player 1, Player 2
FOOD_COLOR = (255, 0, 0)  
BACKGROUND_COLOR = (0, 0, 0)


class Snake:
    def __init__(self, color, start_x, start_y):
        self.body = [[start_x, start_y]]
        self.color = color
        self.direction = "up"
        self.growing = False

    def move(self):
        x, y = self.body[0]
        if self.direction == "up":
            y -= SPACE_SIZE
        elif self.direction == "down":
            y += SPACE_SIZE
        elif self.direction == "left":
            x -= SPACE_SIZE
        elif self.direction == "right":
            x += SPACE_SIZE

        new_head = [x, y]
        self.body.insert(0, new_head)

        if not self.growing:
            self.body.pop()
        else:
            self.growing = False

    def grow(self):
        self.growing = True

    def check_collision(self, other_snake):
        head = self.body[0]
        # collision dengan tepi
        if head[0] < 0 or head[0] >= GAME_WIDTH or head[1] < 0 or head[1] >= GAME_HEIGHT:
            return True
        # collision dengan badan
        if head in self.body[1:]:
            return True
        # collision dengan ular lain
        if head in other_snake.body:
            return True
        return False

    def draw(self, ctx):
        for segment in self.body:
            x, y = segment
            ctx.rectangle(x, y, SPACE_SIZE, SPACE_SIZE)
            ctx.set_source_rgb(*[c / 255 for c in self.color])
            ctx.fill()

class Food:
    def __init__(self):
        self.position = [
            random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE,
            random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE,
        ]

    def draw(self, ctx):
        x, y = self.position
        ctx.arc(x + SPACE_SIZE / 2, y + SPACE_SIZE / 2, SPACE_SIZE / 2, 0, 2 * 3.14159)
        ctx.set_source_rgb(*[c / 255 for c in FOOD_COLOR])
        ctx.fill()


def main():
    pygame.init()
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    pygame.display.set_caption("Snake PvP")
    clock = pygame.time.Clock()

    def reset_game():
        return Snake(SNAKE_COLORS[0], GAME_WIDTH // 4, GAME_HEIGHT // 2), \
               Snake(SNAKE_COLORS[1], 3 * GAME_WIDTH // 4, GAME_HEIGHT // 2), \
               Food(), True, None

    running = True
    snake1, snake2, food, paused, winner = reset_game()

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, GAME_WIDTH, GAME_HEIGHT)
    ctx = cairo.Context(surface)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if paused and event.key == pygame.K_SPACE:
                    if winner:
                        snake1, snake2, food, paused, winner = reset_game()
                    else:
                        paused = False

                # Player 1 
                if event.key == pygame.K_w and snake1.direction != "down":
                    snake1.direction = "up"
                if event.key == pygame.K_s and snake1.direction != "up":
                    snake1.direction = "down"
                if event.key == pygame.K_a and snake1.direction != "right":
                    snake1.direction = "left"
                if event.key == pygame.K_d and snake1.direction != "left":
                    snake1.direction = "right"
                # Player 2 
                if event.key == pygame.K_UP and snake2.direction != "down":
                    snake2.direction = "up"
                if event.key == pygame.K_DOWN and snake2.direction != "up":
                    snake2.direction = "down"
                if event.key == pygame.K_LEFT and snake2.direction != "right":
                    snake2.direction = "left"
                if event.key == pygame.K_RIGHT and snake2.direction != "left":
                    snake2.direction = "right"

        if paused:
            screen.fill(BACKGROUND_COLOR)
            font = pygame.font.SysFont("calibri", 40)
            text = font.render("Tekan SPASI Untuk Start" if not winner else f"{winner} Wins!", True, (255, 255, 255))
            screen.blit(text, (GAME_WIDTH // 2 - text.get_width() // 2, GAME_HEIGHT // 2 - text.get_height() // 2))
            pygame.display.flip()
            clock.tick(60)
            continue

        snake1.move()
        snake2.move()

        if snake1.body[0] == food.position:
            snake1.grow()
            food = Food()
        if snake2.body[0] == food.position:
            snake2.grow()
            food = Food()

        if snake1.check_collision(snake2):
            winner = "Player 2"
            paused = True
        if snake2.check_collision(snake1):
            winner = "Player 1"
            paused = True

        # Clear canvas
        ctx.rectangle(0, 0, GAME_WIDTH, GAME_HEIGHT)
        ctx.set_source_rgb(*[c / 255 for c in BACKGROUND_COLOR])
        ctx.fill()

        food.draw(ctx)
        snake1.draw(ctx)
        snake2.draw(ctx)

        # Convert ARGB32 ke RGB24 karena ada masalah di pewarnaan
        buffer = surface.get_data()
        img_array = np.frombuffer(buffer, np.uint8).reshape((GAME_HEIGHT, GAME_WIDTH, 4))
        img_rgb = img_array[:, :, [2, 1, 0]]  # Swap chanel R dan B

        pygame_surface = pygame.image.frombuffer(img_rgb.tobytes(), (GAME_WIDTH, GAME_HEIGHT), "RGB")
        screen.blit(pygame_surface, (0, 0))
        pygame.display.flip()
        fps = SPEED
        clock.tick(fps)

    pygame.quit()

if __name__ == "__main__":
    main()