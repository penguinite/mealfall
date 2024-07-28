# Example file showing a basic pygame "game loop"
import pygame, random, os
from platformdirs import *

# pygame setup
pygame.init()
screen = pygame.display.set_mode((720, 900))
clock = pygame.time.Clock()
running = True

player_size = 80
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() - player_size)

foods = []
yucks = []
food_size = 20
food_every_ms = 3000
food_dropped = 0
misses = 0

font_size = 32
font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), font_size)

# Open up the best score file.
high_score = 0
try:
    os.makedirs(user_data_dir("Mealfall", "penguinite"), exist_ok=True)
    file = open(
        user_data_dir("Mealfall", "penguinite") + "/mealfall_high_score.txt",
        "r"
    )
    try:
        high_score = int(file.readline())
    except:
        high_score = 0

    file.close()
except:
    print("Couldn't open high score file. Just using 0 as default")
    print("Save file location: " + user_data_dir("Mealfall", "penguinite") + "/mealfall_high_score.txt")

def addFoodOrYuck(food_every_ms, food_dropped):
    # Roll a random number, if its 5 then drop a yuck
    # otherwise drop normal food.
    item = pygame.Vector2(random.randrange(0,screen.get_width()), 0)
    roll = random.randrange(0,3)
    if roll == 2:
        yucks.append(item)
    else:
        foods.append(item)

    # Increase the amount of food dropped.
    # This also kind of acts as the score,
    # since we can minus it with the misses to
    # get the amount of food we have eaten.
    food_dropped += 1

    # After 5 items, slowly decrease the timer.
    # But anything below 500 seems humanly impossible.
    # We could experiment though.
    if food_dropped > 5 and food_every_ms > 500:
        food_every_ms -= 100
        if food_dropped > 75 and food_every_ms > 250:
            food_every_ms -= 50
        pygame.time.set_timer(ADD_FOOD, food_every_ms)

    # Return these two, they will be updated by the caller.
    return (food_every_ms, food_dropped)

ADD_FOOD = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_FOOD, food_every_ms)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == ADD_FOOD:
            a,b = addFoodOrYuck(food_every_ms, food_dropped)
            food_dropped = b
            food_every_ms = a
    
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("#ccfeff")

    player_rect = pygame.draw.rect(
        screen, "red",
        pygame.Rect(player_pos.x, player_pos.y, player_size, player_size)
    )

    # Handle input
    # Using the mouse is better than the keyboard
    x = pygame.mouse.get_pos()[0]
    player_pos.x = x
    if x < 0:
        player_pos.x = 0
    if x > screen.get_width() - player_size:
        player_pos.x = screen.get_width() - player_size

    # Process any food
    i = -1
    for food in foods:
        i += 1
        # Make item fall down
        food.y += 300 * dt
        pygame.draw.circle(screen, "green", food, food_size)
    
        # If it collides with the rectangle (player)
        # Then delete it.
        if player_rect.collidepoint(food.x, food.y):
            del foods[i]
            continue

        # If it isn't on-screen then just increase misses
        # And delete the item.
        if food.y > screen.get_height():
            misses += 1
            del foods[i]
            continue

    
    # Process any yucks (bad food)
    i = -1
    for yuck in yucks:
        i += 1
        # Make item fall down
        yuck.y += 300 * dt
        pygame.draw.circle(screen, "red", yuck, food_size)
        # If it collides with the rectangle (player)
        # Then game over. Otherwise, draw it.
        if player_rect.collidepoint(yuck.x, yuck.y):
            running = False
            break

    # If we have way too many misses then just leave
    if misses >= 8:
        running = False
        break
    
    # Draw score    
    font.render_to(screen, (0, 0), "Score: {0}".format(food_dropped - misses), (0,0,0))
    
    # Draw misses
    font.render_to(screen, (0, font_size), "Misses: {0}/8".format(misses), (0,0,0))

    # Draw high-score
    font.render_to(screen, (0, font_size * 2), "High score: {0}".format(high_score), (0,0,0))

    # flip() the display to put your work on screen
    pygame.display.flip()

    dt = clock.tick(60) / 1000  # limits FPS to 60


# If we have reached this point.
# Then the user has died or left intentionally
# So we save the score, if its higher than the best score
if food_dropped - misses > high_score:
    high_score = food_dropped - misses
    try:
        os.makedirs(user_data_dir("Mealfall", "penguinite"), exist_ok=True)
        file = open(
            user_data_dir("Mealfall", "penguinite") + "/mealfall_high_score.txt",
            "w"
        )
        file.write(str(high_score))
        file.close()
    except:
        print("Couldn't open high score file. Not saving new high score.")
        print("Save file location: " + user_data_dir("Mealfall", "penguinite") + "/mealfall_high_score.txt")

pygame.quit()