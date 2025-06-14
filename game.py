import pygame
import sys
import random
import time
import os
# pygame 초기 설정
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("으차차")
clock = pygame.time.Clock()

# 각종 변수와 리소스 불러오기
state = 'day'
first_run = 300
time_ms = 1
game_speed = 1.0
location = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res') + os.sep
font = pygame.font.Font(location + "SCDream5.otf", 36)

background_day_image = pygame.image.load(location + "background.jpg")
background_day_image = pygame.transform.scale(background_day_image, (800, 600))

background_night_image = pygame.image.load(location + "night.png")
background_night_image = pygame.transform.scale(background_night_image, (800, 600))


player_image = pygame.image.load(location + "character.png")
player_image = pygame.transform.scale(player_image, (40, 60))

boss_image = pygame.image.load(location + "boss.png")
boss_image = pygame.transform.scale(boss_image, (200, 100))

target_up_image = pygame.image.load(location + "target_b-t.png")
target_bottom_image = pygame.image.load(location + "target_t-b.png")

life_boost_image = pygame.image.load(location + "monster.png")
life_boost_image = pygame.transform.scale(life_boost_image, (50, 60))

grade_images = {}
grades = ['A', 'B', 'C', 'D', 'F']
for grade in grades:
    img_path = f"{location}/grade/{grade}.png"
    grade_images[grade] = pygame.image.load(img_path)
    grade_images[grade] = pygame.transform.scale(grade_images[grade], (80, 80))

background_audio = pygame.mixer.Sound(location + '\\audio\\' + 'background.mp3')
background_audio.play(-1)
laser_audio = pygame.mixer.Sound(location + '\\audio\\' + 'laser.mp3')
background_audio.set_volume(0.5)
hit_audio = pygame.mixer.Sound(location + '\\audio\\' + 'hit.mp3')
hit_boss_audio = pygame.mixer.Sound(location + '\\audio\\' + 'boss_hit.mp3')

targets = []
num_targets = 5
life = 5
bonus = 1
start_time = time.time() 

life_boost = None
life_boost_timer = 0
life_boost_interval = random.randint(5, 10)

player = pygame.Rect(20, 300, 30, 30)
player_speed = 4
gravity = 0.7
player_velocity_y = 0
ground_y = 570

grade_target = pygame.Rect(650, 250, 200, 100) 
score = 0 

GRADE_THRESHOLDS = dict(A=1500, B=1000, C=800, D=300, F=1)

def get_current_grade(score):
    if score >= 1500:
        return 'A'
    elif score >= 1000:
        return 'B'
    elif score >= 800:
        return 'C'
    elif score >= 300:
        return 'D'
    else:
        return 'F'

bullets = []
bullet_speed = 7

# 초기 장애물 설정
targets = [
    pygame.Rect(250, 0, 30, 150),
    pygame.Rect(250, 350, 30, 300),
    pygame.Rect(450, 0, 30, 100),
    pygame.Rect(450, 250, 30, 500),
    pygame.Rect(650, 0, 30, 300),
    pygame.Rect(650, 450, 30, 300)
]

# 장애물 생성 함수
def create_target(last_x):
    target_pattern = random.choice([
        [pygame.Rect(300+last_x, 0, 30, 200), pygame.Rect(300+last_x, 350, 30, 300)],  
        [pygame.Rect(450+last_x, 0, 30, 100), pygame.Rect(450+last_x, 250, 30, 500)],  
        [pygame.Rect(600+last_x, 0, 30, 300), pygame.Rect(600+last_x, 450, 30, 300)]
    ])
    return target_pattern

running = True
while running:
    current_time = time.time() - start_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player_velocity_y = -10 

    # 플레이어 점프
    player_velocity_y += gravity
    player.y += player_velocity_y

    # 총알 관련
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        if not bullets or bullets[-1].x > player.x + 100:
            bullet = pygame.Rect(player.centerx - 5, player.centery, 10, 5)
            bullets.append(bullet)
            laser_audio.play()

    for bullet in bullets[:]:
        bullet.x += bullet_speed * game_speed
        if bullet.right > 800:
            bullets.remove(bullet)

    # 바닥 충돌 처리
    if player.bottom >= ground_y:
        player.bottom = ground_y
        player_velocity_y = 0

    # 장애물 관련
    for target in targets[:]:
        if player.colliderect(target):
            targets.remove(target)
            hit_audio.play()
            life -= 1
            if life <= 0:
                running = False
            break

    for target in targets[:]:
        target.x -= 2 * game_speed
        if target.left < 0:
            targets.remove(target)
            last_x = targets[-1].x
            new_targets = create_target(last_x)
            targets.extend(new_targets)

    # 에너지드링크 관련
    if life_boost is None and current_time - life_boost_timer >= life_boost_interval:
        boost_x = random.randint(100, 700)
        boost_y = random.randint(50, 200)  
        life_boost = pygame.Rect(boost_x, boost_y, 20, 20)
        life_boost_timer = current_time
        life_boost_interval = random.randint(5, 10)

    if life_boost and player.colliderect(life_boost):
        if life < 5:
            life += 1
        bonus *= 1.1
        life_boost = None

    if life_boost:
        life_boost.x -=  2* game_speed
        if life_boost.left < 0:
            life_boost = None

    # 책 점수 처리
    for bullet in bullets[:]:
        if grade_target.colliderect(bullet):
            hit_boss_audio.play()
            bullets.remove(bullet)
            score += 10*bonus # 점수 부스트
            target_location = random.randint(100, 450)
            grade_target.y = target_location

            # A 학점 달성시 게임 종료
            if score >= GRADE_THRESHOLDS['A']:
                running = False

    # 배경 바꾸기
    if time_ms % 1800 == 0:
        if state == 'night':
            state = 'day'
        else:
            state = 'night'

    if state == 'day':
        screen.blit(background_day_image, (0, 0))
    else:
        screen.blit(background_night_image, (0, 0))
    
    pygame.draw.rect(screen, (139, 69, 19), (0, ground_y, 800, 30)) 

    # 장애물 그리기
    for target in targets:
        if target.y == 0:
            scaled_image = pygame.transform.scale(target_bottom_image, target.size)
            screen.blit(scaled_image, target.topleft)
        else:
            scaled_image = pygame.transform.scale(target_up_image, target.size)
            screen.blit(scaled_image, target.topleft)

    screen.blit(player_image, player)

    for bullet in bullets: 
        pygame.draw.rect(screen, (255, 255, 0), bullet)

    screen.blit(boss_image, grade_target)

    if life_boost:
        screen.blit(life_boost_image, life_boost.topleft)

    screen.blit(grade_images[str(get_current_grade(score))], (700, 20)) 
    
    pygame.draw.rect(screen, (255,255,255), (50, 40, 600, 20))
    pygame.draw.rect(screen, (255,69,0), (50, 40, life * 120, 20))
    pygame.draw.rect(screen, (0, 0, 0), (50, 40, 600, 20), 5)

    GRADE_ORDER = ['F', 'D', 'C', 'B', 'A']
    PROGRESS_THRESHOLDS = { 'F': 0, 'D': 300, 'C': 800, 'B': 1000, 'A': 1500 }

    current_grade = get_current_grade(score)
    lower_bound = PROGRESS_THRESHOLDS[current_grade]

    # 게임 속도 난이도 조절
    time_ms += 1
    if time_ms % 300 == 0:
        game_speed += 0.05

    # 진행률 계산
    if current_grade == 'A':
        upper_bound = PROGRESS_THRESHOLDS['A']
        progress_ratio = 1.0
    else:
        next_grade = GRADE_ORDER[GRADE_ORDER.index(current_grade) + 1]
        upper_bound = PROGRESS_THRESHOLDS[next_grade]
        if (upper_bound - lower_bound) > 0:
            progress_ratio = (score - lower_bound) / (upper_bound - lower_bound)
        else:
            progress_ratio = 1.0

    if first_run:
        text= font.render("스페이스바 : 점프", True, (255, 255, 255))
        text2 = font.render("방향키 오른쪽 : 연필 발사", True, (255, 255, 255))
        text3 = font.render("목표 : A학점 달성, 책 맞출시 학점 증가", True, (255, 255, 255))
        text_rect = text.get_rect(center=(400, 280))
        text2_rect = text2.get_rect(center=(400, 320))
        text3_rect = text3.get_rect(center=(400, 360))
        screen.blit(text, text_rect)
        screen.blit(text2, text2_rect)
        screen.blit(text3, text3_rect)
        first_run -= 1

    pygame.draw.rect(screen, (255, 255, 255), (50, 70, 600, 30))
    pygame.draw.rect(screen, (0, 128, 255), (50, 70, 600 * min(progress_ratio, 1.0), 30))
    pygame.draw.rect(screen, (0, 0, 0), (50, 70, 600, 30), 4)

    pygame.display.flip()
    clock.tick(60)

# 게임 종료
if state == 'day':
    screen.blit(background_day_image, (0, 0)) 
elif state == 'night':
    screen.blit(background_night_image, (0, 0))
else:
    screen.fill((0, 0, 0))

if life <= 0:
    text = font.render("Game Over!", True, (255, 0, 0))
    final_grade = font.render(f"최종 학점: {get_current_grade(score)}", True, (255, 255, 255))
    final_score = font.render(f"최종 점수: {int(score)}", True, (255, 255, 255))
    text_rect = text.get_rect(center=(400, 280))
    grade_rect = final_grade.get_rect(center=(400, 320))
    score_rect = final_score.get_rect(center=(400, 360))
    screen.blit(text, text_rect)
    screen.blit(final_grade, grade_rect)
    screen.blit(final_score, score_rect)

if score >= GRADE_THRESHOLDS['A']:
    text = font.render("A학점으로 졸업 성공!!", True, (0, 255, 0))
    text2 = font.render(f"클리어 시간: {int(time.time() - start_time)}초", True, (255, 255, 255))
    text3 = font.render(f"최종 점수: {int(score)}", True, (255, 255, 255))
    text_rect = text.get_rect(center=(400, 280))
    text2_rect = text2.get_rect(center=(400, 320))
    text3_rect = text3.get_rect(center=(400, 360))
    screen.blit(text, text_rect)
    screen.blit(text2, text2_rect)
    screen.blit(text3, text3_rect)

pygame.display.flip()
pygame.time.delay(6000)
pygame.quit()
sys.exit()