import unittest
import pygame
import numpy as np

# استيراد الكلاسات والدوال من ملف اللعبة الرئيسي (افترض أن اسم ملف اللعبة game.py)
# يمكنك تغيير كلمة game باسم ملف اللعبة الخاص بك
try:
    from game import HaroldPlayer, Platform, generate_sound, WIDTH, HEIGHT
except ImportError:
    # في حال كان الكود في نفس الملف أو اسم الملف مختلف
    pass

class TestIcyTowerGame(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # تهيئة بيئة Pygame الصوتية والمرئية للاختبارات
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.mixer.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_player_initialization(self):
        """اختبار القيم الافتراضية للاعب هارولد عند بدء اللعبة"""
        player = HaroldPlayer()
        self.assertEqual(player.width, 32)
        self.assertEqual(player.height, 46)
        self.assertFalse(player.on_ground)
        self.assertTrue(player.facing_right)

    def test_player_movement_limits(self):
        """اختبار عدم تجاوز اللاعب لحدود الشاشة والارتداد"""
        player = HaroldPlayer()
        player.x = 5  # محاولة تجاوز الجدار الأيسر
        # محاكاة تحديث الحركة
        keys = {}
        player.update(keys)
        # يجب أن يرتد للداخل ولا يقل عن 15
        self.assertGreaterEqual(player.x, 15)

    def test_platform_generation(self):
        """اختبار خصائص المنصات وأرقام الطوابق"""
        level = 3
        platform = Platform(200, level)
        self.assertEqual(platform.level_num, level)
        self.assertEqual(platform.height, 16)
        # التأكد من أن عرض المنصات ضمن الحدود المنطقية
        self.assertGreaterEqual(platform.width, 80)

    def test_sound_generator(self):
        """اختبار مولد الأصوات البرمجي Synth وعودته ككائن Pygame Sound"""
        sound = generate_sound(440, 0.1, "jump")
        self.assertIsInstance(sound, pygame.mixer.Sound)

if __name__ == "__main__":
    unittest.main()