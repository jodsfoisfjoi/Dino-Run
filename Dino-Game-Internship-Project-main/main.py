import pygame
import random

def display_score(start_time):
    time = int(pygame.time.get_ticks() / 300) - start_time
    score_surf = game_font.render(f"Score: {time}", False, "Black")
    score_rect = score_surf.get_rect(center=(400, 50))
    screen.blit(score_surf, score_rect)
    return time

def display_lives(lives):
    lives_surf = game_font.render(f"Lives: {lives}", False, "Black")
    lives_rect = lives_surf.get_rect(topleft=(10, 10))
    screen.blit(lives_surf, lives_rect)

def obstacle_movement(obstacle_list, speed_multiplier):
    if obstacle_list:
        for obstacle_rect in obstacle_list:
            obstacle_rect.x -= 5 * speed_multiplier

            if obstacle_rect.bottom == 300:
                if obstacle_rect.width == enemy_surf.get_width():
                    screen.blit(enemy_surf, obstacle_rect)
                elif obstacle_rect.width == enemy_2_surf.get_width():
                    screen.blit(enemy_2_surf, obstacle_rect)
            else:
                if obstacle_rect.width == basketball_surf.get_width():
                    screen.blit(basketball_surf, obstacle_rect)
                else:
                    screen.blit(enemy_3_surf, obstacle_rect)

        obstacle_list = [obstacle for obstacle in obstacle_list if obstacle.x > -100 or obstacle.width == basketball_surf.get_width()]
        return obstacle_list
    else:
        return []

def collisions(player, obstacles):
    if obstacles:
        for obstacle_rect in obstacles:
            if player.colliderect(obstacle_rect):
                if obstacle_rect.width == basketball_surf.get_width():
                    return "basketball", obstacle_rect
                else:
                    return "enemy", obstacle_rect
    return "none", None

def update_leaderboard(score, filename="leaderboard.txt"):
    try:
        with open(filename, 'r') as file:
            scores = [int(line.strip()) for line in file.readlines()]
    except FileNotFoundError:
        scores = []

    scores.append(score)
    scores = sorted(set(scores), reverse=True)[:5]  # Ensure scores are distinct

    with open(filename, 'w') as file:
        for score in scores:
            file.write(f"{score}\n")

    return scores

def display_leaderboard(scores):
    screen.fill("black")
    game_over_surf = game_font.render("Game Over! Press SPACE to Restart", False, "White")
    game_over_rect = game_over_surf.get_rect(center=(400, 100))
    screen.blit(game_over_surf, game_over_rect)

    leaderboard_title_surf = game_font.render("Top 5 Scores", False, "White")
    leaderboard_title_rect = leaderboard_title_surf.get_rect(center=(400, 150))
    screen.blit(leaderboard_title_surf, leaderboard_title_rect)

    for index, score in enumerate(scores):
        score_surf = game_font.render(f"{index + 1}. {score}", False, "White")
        score_rect = score_surf.get_rect(center=(400, 200 + index * 40))
        screen.blit(score_surf, score_rect)

pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
pygame.display.set_caption("caixukun run")
running = True
start_time = 0
is_playing = False
score = 0
game_font = pygame.font.Font("font/Pixeltype.ttf", 50)
score_surf = game_font.render("SCORE", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

sky_surf = pygame.image.load("graphics/egg/cyk.png").convert()
sky_surf = pygame.transform.rotozoom(sky_surf, 0, 0.65)
ground_surf = pygame.image.load("graphics/egg/99.png").convert()
ground_surf = pygame.transform.rotozoom(ground_surf, 0, 3.5)

obstacle_rect_list = []

player_surf = pygame.image.load("graphics/egg/我的飞机.png").convert_alpha()
player_squat_surf = pygame.image.load("graphics/egg/paddle2_1.png").convert_alpha()
player_squat_surf = pygame.transform.rotozoom(player_squat_surf, 0, 0.7)
player_squat_rect = player_squat_surf.get_rect(midbottom=(80, 305))
player_jump_surf = pygame.image.load("graphics/egg/pipe.png").convert_alpha()
player_jump_surf = pygame.transform.rotozoom(player_jump_surf, 0, 0.35)
player_rect = player_surf.get_rect(midbottom=(80, 300))
enemy_surf = pygame.image.load("graphics/egg/chicken.png").convert_alpha()
enemy_surf = pygame.transform.rotozoom(enemy_surf, 0, 0.12)
enemy_2_surf = pygame.image.load("graphics/egg/chicken_2.png").convert_alpha()
enemy_2_surf = pygame.transform.rotozoom(enemy_2_surf, 0, 0.15)
enemy_3_surf = pygame.image.load("graphics/egg/ikun.png").convert_alpha()
enemy_3_surf = pygame.transform.rotozoom(enemy_3_surf, 0, 0.07)
basketball_surf = pygame.image.load("graphics/egg/ball.png").convert_alpha()
gravity = 0

# Load animation frames for player with basketball
player_basketball_frames = [
    pygame.image.load("graphics/egg/cxk_left.png").convert_alpha(),
    pygame.image.load("graphics/egg/cxk_midleft.png").convert_alpha(),
    pygame.image.load("graphics/egg/cxk_mid.png").convert_alpha(),
    pygame.image.load("graphics/egg/cxk_midright.png").convert_alpha(),
    pygame.image.load("graphics/egg/cxk_right.png").convert_alpha(),
]
animation_index = 0
animation_timer = pygame.USEREVENT + 3
pygame.time.set_timer(animation_timer, 100)  # Adjust the timing for the animation speed

timer = pygame.USEREVENT + 1
pygame.time.set_timer(timer, 1500)

# Speed multiplier related variables
INITIAL_OBSTACLE_SPEED = 1.0
speed_multiplier = INITIAL_OBSTACLE_SPEED
SPEED_INCREASE_INTERVAL = 5000  # Interval for increasing speed (milliseconds)
SPEED_MULTIPLIER_INCREMENT = 0.1  # Increment to the speed multiplier

pygame.time.set_timer(pygame.USEREVENT + 2, SPEED_INCREASE_INTERVAL)

# Game state variables
is_playing = False
leaderboard_scores = []
jumps = 0  # Track the number of jumps
is_squatting = False
player_has_basketball = False  # Track if the player has the basketball
lives = 2  # Player starts with 2 lives
basketball_count = 0  # Track collected basketballs
basketball_positions = []  # Store positions of collected basketballs
god_mode = False  # Player invincibility flag
god_mode_start_time = 0  # Track the start time of invincibility
GOD_MODE_DURATION = 1000  # Duration of invincibility in milliseconds

def reset_game():
    global start_time, speed_multiplier, player_rect, gravity, is_squatting, player_has_basketball, animation_index, obstacle_rect_list, score, lives, basketball_count, basketball_positions, god_mode, god_mode_start_time
    start_time = int(pygame.time.get_ticks() / 300)
    speed_multiplier = INITIAL_OBSTACLE_SPEED
    player_rect.midbottom = (80, 300)  # Reset player position
    gravity = 0
    is_squatting = False  # Reset squatting state
    player_has_basketball = False  # Reset player state
    animation_index = 0  # Reset animation index
    obstacle_rect_list.clear()  # Clear obstacles
    score = 0  # Reset score
    lives = 2  # Reset lives
    basketball_count = 0  # Reset basketball count
    basketball_positions.clear()  # Clear basketball positions
    god_mode = False  # Reset invincibility state
    god_mode_start_time = 0  # Reset invincibility timer

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if is_playing:
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                if player_rect.bottom >= 300:
                    gravity = -20
                    jumps = 1
                elif jumps < 2:
                    gravity = -20
                    jumps += 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN and player_rect.bottom >= 300:
                    is_squatting = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    is_squatting = False
            if event.type == timer:
                obstacle_type = random.choices(
                    ["enemy", "enemy_2", "basketball", "enemy_3"],
                    [1, 1, 0.5, 1],
                )[0]
                if obstacle_type == "enemy":
                    obstacle_rect_list.append(enemy_surf.get_rect(bottomright=(random.randint(900, 1100), 300)))
                elif obstacle_type == "enemy_2":
                    obstacle_rect_list.append(enemy_2_surf.get_rect(bottomright=(random.randint(900, 1100), 300)))
                elif obstacle_type == "basketball":
                    obstacle_rect_list.append(basketball_surf.get_rect(bottomright=(random.randint(900, 1100), 210)))
                else:
                    obstacle_rect_list.append(enemy_3_surf.get_rect(bottomright=(random.randint(900, 1100), 210)))
            if event.type == pygame.USEREVENT + 2:
                speed_multiplier += SPEED_MULTIPLIER_INCREMENT
            if event.type == animation_timer and player_has_basketball:
                animation_index = (animation_index + 1) % len(player_basketball_frames)
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_playing = True
                reset_game()

    if is_playing:
        screen.blit(sky_surf, (0, 0))
        screen.blit(ground_surf, (0, 300))

        score = display_score(start_time)
        display_lives(lives)
        gravity += 1
        player_rect.y += gravity
        if player_rect.bottom >= 300:
            player_rect.bottom = 300
            jumps = 0

        # Change player sprite based on state
        if player_has_basketball:
            if player_rect.bottom < 300:
                player_image = player_jump_surf
            elif is_squatting:
                player_image = player_squat_surf
            else:
                player_image = player_basketball_frames[animation_index]
        else:
            if player_rect.bottom < 300:
                player_image = player_jump_surf
            elif is_squatting:
                player_image = player_squat_surf
            else:
                player_image = player_surf

        player_rect = player_image.get_rect(midbottom=player_rect.midbottom)
        screen.blit(player_image, player_rect)

        obstacle_rect_list = obstacle_movement(obstacle_rect_list, speed_multiplier)
        
        # Check if god mode has expired
        if god_mode and pygame.time.get_ticks() - god_mode_start_time > GOD_MODE_DURATION:
            god_mode = False
        
        collision_type, collided_basketball = collisions(player_rect, obstacle_rect_list)
        if collision_type == "enemy" and not god_mode:
            if lives > 1:
                lives -= 1
                god_mode = True
                god_mode_start_time = pygame.time.get_ticks()
            else:
                is_playing = False
                leaderboard_scores = update_leaderboard(score)
        elif collision_type == "basketball":
            player_has_basketball = True
            basketball_count += 1
            # Move the collided basketball to the top right corner
            collided_basketball.topright = (760 - (basketball_count - 1) * 40, 10)
            basketball_positions.append(collided_basketball)
            obstacle_rect_list = [ob for ob in obstacle_rect_list if ob != collided_basketball]
            if basketball_count >= 5:
                basketball_count = 0
                lives += 1
                player_has_basketball = False
                basketball_positions.clear()

        # Display collected basketballs at the top right corner
        for basketball_rect in basketball_positions:
            screen.blit(basketball_surf, basketball_rect)

    else:
        screen.fill("black")
        game_over_surf = game_font.render("Press SPACE to Start", False, "White")
        game_over_rect = game_over_surf.get_rect(center=(400, 200))
        screen.blit(game_over_surf, game_over_rect)
        if leaderboard_scores:
            display_leaderboard(leaderboard_scores)

    pygame.display.update()
    clock.tick(60)

pygame.quit()





