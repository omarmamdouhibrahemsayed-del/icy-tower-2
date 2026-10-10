import pygame
import random
import math
import numpy as np

# 1. تهيئة الصوت والصورة
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Icy Tower - Deluxe Sound Edition")
clock = pygame.time.Clock()

# --- توليد أصوات Synth النوستالجية برمجياً ---
def generate_sound(frequency, duration, sound_type="jump"):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    
    if sound_type == "jump":
        # صوت قفز تصاعدي 8-bit
        freq_sweep = np.linspace(frequency, frequency * 2.2, n_samples)
        waveform = np.sin(2 * np.pi * freq_sweep * t)
    elif sound_type == "combo":
        # صوت تشقلب احتفالي متدرج
        freq_sweep = frequency * (1 + 0.5 * np.sin(2 * np.pi * 15 * t))
        waveform = 0.5 * np.sin(2 * np.pi * freq_sweep * t) + 0.5 * np.sign(np.sin(2 * np.pi * freq_sweep * t))
    elif sound_type == "land":
        # صوت هبوط خفيف
        waveform = np.sin(2 * np.pi * frequency * t) * np.exp(-15 * t)
    else:  # fall / game over
        freq_sweep = np.linspace(frequency, frequency * 0.3, n_samples)
        waveform = np.sin(2 * np.pi * freq_sweep * t)

    # تطبيق ضابط الصوت وتخفيف البداية والنهاية لمنع التشويش
    fade = np.linspace(1, 0, n_samples)
    sound_array = (waveform * fade * 32767).astype(np.int16)
    return pygame.mixer.Sound(buffer=sound_array)

# تجهيز المؤثرات الصوتية
SND_JUMP = generate_sound(300, 0.15, "jump")
SND_COMBO = generate_sound(450, 0.35, "combo")
SND_LAND = generate_sound(150, 0.08, "land")
SND_FALL = generate_sound(400, 0.6, "fall")

# الألوان
NIGHT_BLUE = (12, 18, 38)
PLATFORM_COLOR = (210, 110, 40)
PLATFORM_EDGE = (250, 180, 70)
HAROLD_SKIN = (255, 205, 160)
HAROLD_CLOTHES = (30, 110, 220)
HAROLD_CAP = (230, 30, 40)
WHITE = (255, 255, 255)
GREEN = (40, 240, 100)
YELLOW = (255, 220, 0)


# 2. فئة اللاعب (هارولد Harold بنفس المظهر الشهير)
class HaroldPlayer:
    def __init__(self):
        self.width = 32
        self.height = 46
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.rotation = 0
        self.is_flipping = False
        self.facing_right = True

    def update(self, keys):
        accel = 0.85
        max_speed = 9.5
        friction = 0.85

        if keys[pygame.K_LEFT]:
            self.vx -= accel
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.vx += accel
            self.facing_right = True
        else:
            self.vx *= friction

        self.vx = max(-max_speed, min(max_speed, self.vx))
        self.x += self.vx

        # الارتداد من الجدران
        if self.x < 15:
            self.x = 15
            self.vx *= -0.4
        elif self.x > WIDTH - self.width - 15:
            self.x = WIDTH - self.width - 15
            self.vx *= -0.4

        # الجاذبية
        self.vy += 0.65
        self.y += self.vy

        # دوران التشقلب في الهواء
        if self.is_flipping:
            rot_step = 30 if self.facing_right else -30
            self.rotation += rot_step
            if abs(self.rotation) >= 360:
                self.rotation = 0
                self.is_flipping = False
        else:
            self.rotation = 0

    def jump(self):
        if self.on_ground:
            speed_bonus = abs(self.vx) * 0.75
            self.vy = -(12.5 + speed_bonus)
            self.on_ground = False

            # تشغيل صوت القفز أو التشقلب
            if abs(self.vx) > 5.5:
                self.is_flipping = True
                SND_COMBO.play()
            else:
                SND_JUMP.play()

    def draw(self, surface, camera_y):
        draw_y = self.y - camera_y

        # رسم مجسم شخصية Harold بكل تفاصيله
        char_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # الجسم والملابس (Sweatshirt أزرق)
        pygame.draw.rect(char_surf, HAROLD_CLOTHES, (4, 16, 24, 20), border_radius=4)
        # البنطال الأغمق
        pygame.draw.rect(char_surf, (20, 60, 140), (6, 32, 20, 10), border_radius=2)
        # الحذاء الأبيض
        pygame.draw.rect(char_surf, WHITE, (4, 40, 10, 6), border_radius=2)
        pygame.draw.rect(char_surf, WHITE, (18, 40, 10, 6), border_radius=2)

        # الرأس والوجه
        pygame.draw.circle(char_surf, HAROLD_SKIN, (16, 12), 10)

        # العين والابتسامة حسب الاتجاه
        eye_x = 20 if self.facing_right else 12
        pygame.draw.circle(char_surf, (20, 20, 20), (eye_x, 11), 2)

        # الكاب الأحمر المميز مع القمة الجانبية
        cap_rect = (2, 2, 28, 8) if self.facing_right else (2, 2, 28, 8)
        pygame.draw.rect(char_surf, HAROLD_CAP, cap_rect, border_radius=3)
        peak_x = 22 if self.facing_right else -2
        pygame.draw.ellipse(char_surf, HAROLD_CAP, (peak_x, 6, 12, 5))

        # التدوير عند الحركة أو التشقلب
        rotated_surf = pygame.transform.rotate(char_surf, -self.rotation)
        new_rect = rotated_surf.get_rect(center=(self.x + self.width // 2, draw_y + self.height // 2))

        surface.blit(rotated_surf, new_rect.topleft)


# 3. فئة الدرج
class Platform:
    def __init__(self, y, level_num):
        self.width = max(80, 180 - (level_num // 8) * 10)
        self.height = 16
        self.x = random.randint(20, WIDTH - self.width - 20)
        self.y = y
        self.level_num = level_num

    def draw(self, surface, camera_y):
        draw_y = self.y - camera_y
        rect = pygame.Rect(self.x, draw_y, self.width, self.height)
        pygame.draw.rect(surface, PLATFORM_COLOR, rect, border_radius=4)
        pygame.draw.rect(surface, PLATFORM_EDGE, (self.x, draw_y, self.width, 4), border_radius=2)

        font = pygame.font.SysFont("Arial", 11, bold=True)
        txt = font.render(str(self.level_num), True, WHITE)
        surface.blit(txt, (self.x + 6, draw_y + 2))


# 4. محرك اللعبة الرئيسي
def main():
    player = HaroldPlayer()
    platforms = [Platform(HEIGHT - 40, 0)]
    platforms[0].x = WIDTH // 2 - 100
    platforms[0].width = 200

    for i in range(1, 15):
        platforms.append(Platform(HEIGHT - 40 - i * 70, i))

    camera_y = 0
    highest_level = 0
    combo_text = ""
    combo_timer = 0
    last_platform_level = 0

    font = pygame.font.SysFont("Impact", 28)
    combo_font = pygame.font.SysFont("Impact", 38)

    running = True
    while running:
        clock.tick(60)
        screen.fill(NIGHT_BLUE)

        # جدران الثلج الجانبية
        pygame.draw.rect(screen, (35, 55, 95), (0, 0, 15, HEIGHT))
        pygame.draw.rect(screen, (35, 55, 95), (WIDTH - 15, 0, 15, HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    player.jump()

        keys = pygame.key.get_pressed()
        player.update(keys)

        # متابعة الكاميرا
        target_camera_y = player.y - HEIGHT // 2
        if target_camera_y < camera_y:
            camera_y += (target_camera_y - camera_y) * 0.1

        camera_y -= 0.4 + (highest_level * 0.02)

        # التصادم مع المنصات
        was_on_ground = player.on_ground
        player.on_ground = False

        for p in platforms:
            if player.vy > 0 and (p.y <= player.y + player.height <= p.y + 15):
                if p.x - player.width + 5 <= player.x <= p.x + p.width - 5:
                    player.y = p.y - player.height
                    player.vy = 0
                    player.on_ground = True

                    if not was_on_ground:
                        SND_LAND.play()

                    # حساب القفزات والكلمات التشجيعية (Combos)
                    level_diff = p.level_num - last_platform_level
                    if level_diff >= 2:
                        words = {2: "GOOD!", 3: "SWEET!", 4: "GREAT!", 5: "SUPER DIZZY!"}
                        combo_text = words.get(level_diff, "UNSTOPPABLE!!")
                        combo_timer = 45

                    last_platform_level = p.level_num
                    highest_level = max(highest_level, p.level_num)
                    break

        # توليد منصات جديدة للأعلى
        highest_p_y = min(p.y for p in platforms)
        if highest_p_y > camera_y - 100:
            next_lvl = max(p.level_num for p in platforms) + 1
            platforms.append(Platform(highest_p_y - 70, next_lvl))

        platforms = [p for p in platforms if p.y - camera_y < HEIGHT + 50]

        # الخسارة
        if player.y - camera_y > HEIGHT:
            SND_FALL.play()
            running = False

        # الرسم
        for p in platforms:
            p.draw(screen, camera_y)

        player.draw(screen, camera_y)

        # الواجهة
        score_surf = font.render(f"Floor: {highest_level}", True, YELLOW)
        screen.blit(score_surf, (25, 20))

        if combo_timer > 0:
            combo_surf = combo_font.render(combo_text, True, GREEN)
            screen.blit(combo_surf, (WIDTH // 2 - combo_surf.get_width() // 2, 100))
            combo_timer -= 1

        pygame.display.flip()

    # شاشة Game Over
    pygame.time.wait(300)
    screen.fill(NIGHT_BLUE)
    go_text = font.render("GAME OVER", True, WHITE)
    final_score = font.render(f"Highest Floor: {highest_level}", True, YELLOW)
    screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 40))
    screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.flip()
    pygame.time.wait(2500)

    pygame.quit()

if __name__ == "__main__":
    main()