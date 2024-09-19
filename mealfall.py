import pygame, random, os

pygame.init()

player_size = 80
font_size = 32
food_size = 45
font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), font_size)
ADD_FOOD = pygame.USEREVENT + 1

class Mealfall:
    def __init__(self, width=720, height=900):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width,height))
        pygame.display.set_caption("Mealfall")
        self.clock = pygame.time.Clock()
        self.player = pygame.Vector2(width / 2, height - player_size)
        self.player_img = pygame.image.load("player_sprite.png").convert_alpha()
        self.food_img = pygame.image.load("food.png").convert_alpha()
        self.yuck_img = pygame.image.load("yuck.png").convert_alpha()
        self.running = True
        self.reset() # Run this to initialize the rest of the variables.
    
    def reset(self):
        # Reset everything back to its default state.
        self.dt = 0
        self.score = 0
        self.misses = 0
        self.food_dropped = 0
        self.food_every_ms = 3000
        self.yucks = []
        self.foods = []
        self.player = pygame.Vector2(self.width / 2, self.height - player_size)
        pygame.time.set_timer(ADD_FOOD, self.food_every_ms)
    
    def add_food_or_yuck(self):
        # Roll a random number, if its 5 then drop a yuck
        # otherwise drop normal food.
        item = pygame.Vector2(random.randrange(0,self.width), 0)
        roll = random.randrange(0,3)
        if roll == 2:
            self.yucks.append(item)
        else:
            self.foods.append(item)
        
        # Increase the amount of food dropped.
        # This also kind of acts as the score,
        # since we can minus it with the misses to
        # get the amount of food we have eaten.
        self.food_dropped += 1

        # After 5 items, slowly decrease the timer.
        # But anything below 500 seems humanly impossible.
        # We could experiment though.
        if self.food_dropped > 5 and self.food_every_ms > 500:
            self.food_every_ms -= 100
            if self.food_dropped > 75 and self.food_every_ms > 250:
                self.food_every_ms -= 50
            pygame.time.set_timer(ADD_FOOD, self.food_every_ms)
    
    def text(self, txt, times = 0):
        font.render_to(
            self.screen,
            (0, font_size * times),
            txt,
            (0,0,0)
        )

    def draw_yuck(self, yuck):
        self.screen.blit(
            self.yuck_img, yuck
        )

    def draw_food(self, food):
        self.screen.blit(
            self.food_img, food
        )
    
    def draw_player(self):
        self.screen.blit(
            self.player_img, (self.player.x, self.player.y)
        )
        return pygame.Rect(
            self.player.x, self.player.y, player_size, player_size
        )

    def pre_processing_input(self):
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            if event.type == ADD_FOOD:
                self.add_food_or_yuck()
        return True

    def get_input_as_pos(self):
        # Handle input
        # Using the mouse is better than the keyboard
        result = pygame.mouse.get_pos()[0]
        # If the mouse if way off to the right, then
        # just set it to the most right point
        if result < 0:
            result = 0
        # If mouse is way off to the left, then just
        # set it to the most left point.
        if result > self.width - player_size:
            result = self.width - player_size
        return result

    def step(self):
        # Basic pre-processing of input
        if self.pre_processing_input() != True:
            return False

        # fill the screen with a color to wipe away anything from last frame
        self.screen.fill("#ccfeff")

        # Process player input and draw player rectangle
        self.player.x = self.get_input_as_pos()
        player_rect = self.draw_player()

        # Process any food
        i = -1
        for food in self.foods:
            i += 1
            # Make item fall down
            food.y += 300 * self.dt
            self.draw_food(food)

            # If it collides with the rectangle (player)
            # Then delete it.
            if player_rect.collidepoint(food.x, food.y):
                del self.foods[i]
                continue

            # If it isn't on-screen then just increase misses
            # And delete the item.
            if food.y > self.height:
                self.misses += 1
                del self.foods[i]
                continue

        # Process any yucks (bad food)
        for yuck in self.yucks:
            # Make item fall down
            yuck.y += 300 * self.dt
            self.draw_yuck(yuck)

            # If it collides with the rectangle (player)
            # Then game over. Otherwise, draw it.
            if player_rect.collidepoint(yuck.x, yuck.y):
                return False

        # Draw score and misses.
        self.text("Score: {0}".format(self.food_dropped - self.misses))
        self.text("Misses: {0}/8".format(self.misses), 1)

        # If we have too many misses, then just quit the game.
        if self.misses >= 8:
            return False

        # flip() the display to put your work on screen
        pygame.display.flip()

        self.dt = self.clock.tick(60) / 1000  # limits FPS to 60
        return self.running

mealfall = Mealfall()
while mealfall.step() == True: pass
pygame.quit()