"""
لعبة سباق السيارات ثلاثية الأبعاد مع الذكاء الاصطناعي
GameCars 3D Racing Game with AI

المميزات:
- 100 مرحلة متزايد الصعوبة
- سيارة Algha Bug الذكية التي تتعلم من اللاعب
- عملات وعقبات (حفر، زيت، نيازك)
- مشروبات قوة وطيران مؤقت
- منحدرات لزيادة السرعة
- بيئة غنية بالأشجار والسماء

التحكم:
- WASD أو الأسهم: التحرك
- جمع العملات لت advancement للمستوى التالي
- تجنب الحفر والزيت والنيازك
- هزيمة Algha Bug كل 10 مستويات

التركيب والتشغيل:
1. تأكد من تثبيت Python 3.8+
2. قم بتثبيت Ursina: pip install ursina
3. شغّل اللعبة: python game_cars_3d.py

ملاحظة: تتطلب اللعبة نافذة رسومية (GUI) للعمل
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
import time

# إعداد اللعبة
app = Ursina(title="GameCars 3D - سباق السيارات", borderless=False, fullscreen=False, show_fps=True)
window.color = color.sky_blue

# متغيرات اللعبة
current_level = 1
coins = 0
speed_boost = 1.0
flight_mode = False
flight_timer = 0
algha_bug_defeated = False
algha_bug_power_multiplier = 1.0
player_speed_history = []
algha_bug_learned_patterns = []

# إنشاء الأرضية
ground = Entity(
    model='plane',
    texture='grass',
    collider='box',
    scale=(200, 1, 200),
    texture_scale=(50, 50),
    color=color.rgb(0, 150, 0)
)

# إنشاء السماء
sky = Sky(texture='sky_sunset')

# إنشاء اللاعب (السيارة)
player = Entity(
    model='cube',
    color=color.red,
    scale=(2, 1, 4),
    position=(0, 1, 0),
    collider='box'
)

# كاميرا تتبع اللاعب
camera.parent = player
camera.position = (0, 5, -15)
camera.rotation = (-20, 0, 0)

# معلومات المستوى
level_text = Text(text=f'Level: {current_level}/100', position=(-0.85, 0.45), scale=2, color=color.white)
coins_text = Text(text=f'Coins: {coins}', position=(-0.85, 0.40), scale=2, color=color.yellow)
speed_text = Text(text=f'Speed: {speed_boost:.1f}x', position=(-0.85, 0.35), scale=2, color=color.cyan)

# رسالة النصر
victory_text = Text(text='', position=(0, 0), scale=3, color=color.gold, origin=(0, 0))

# قائمة العقبات والعناصر
obstacles = []
coins_entities = []
powerups = []
meteors = []
trees = []

# إنشاء الأشجار
def create_trees():
    for i in range(100):
        x = random.uniform(-90, 90)
        z = random.uniform(-90, 90)
        if abs(x) > 10 or abs(z) > 10:  # بعيد عن مسار السباق
            tree = Entity(
                model='cone',
                color=color.dark_green,
                scale=(random.uniform(2, 5), random.uniform(10, 20), random.uniform(2, 5)),
                position=(x, 0, z),
                collider='box'
            )
            trees.append(tree)

create_trees()

# إنشاء العملات
def create_coins():
    for coin_entity in coins_entities:
        destroy(coin_entity)
    coins_entities.clear()
    
    for i in range(20):
        x = random.uniform(-80, 80)
        z = random.uniform(-80, 80)
        coin = Entity(
            model='sphere',
            color=color.gold,
            scale=(1, 1, 1),
            position=(x, 2, z),
            collider='box'
        )
        coins_entities.append(coin)

create_coins()

# إنشاء العقبات (حفر وزيت)
def create_obstacles():
    for obs in obstacles:
        destroy(obs)
    obstacles.clear()
    
    # حفر
    for i in range(10):
        x = random.uniform(-80, 80)
        z = random.uniform(-80, 80)
        pit = Entity(
            model='cube',
            color=color.black,
            scale=(3, 0.5, 3),
            position=(x, 0.1, z),
            collider='box',
            tag='pit'
        )
        obstacles.append(pit)
    
    # زيت
    for i in range(15):
        x = random.uniform(-80, 80)
        z = random.uniform(-80, 80)
        oil = Entity(
            model='cube',
            color=color.gray,
            scale=(2, 0.2, 2),
            position=(x, 0.1, z),
            collider='box',
            tag='oil'
        )
        obstacles.append(oil)

create_obstacles()

# إنشاء مشروبات القوة
def create_powerups():
    for pu in powerups:
        destroy(pu)
    powerups.clear()
    
    # مشروب السرعة
    for i in range(5):
        x = random.uniform(-80, 80)
        z = random.uniform(-80, 80)
        speed_potion = Entity(
            model='cube',
            color=color.cyan,
            scale=(1, 2, 1),
            position=(x, 1, z),
            collider='box',
            tag='speed'
        )
        powerups.append(speed_potion)
    
    # مشروب الطيران
    for i in range(3):
        x = random.uniform(-80, 80)
        z = random.uniform(-80, 80)
        flight_potion = Entity(
            model='cube',
            color=color.purple,
            scale=(1, 2, 1),
            position=(x, 1, z),
            collider='box',
            tag='flight'
        )
        powerups.append(flight_potion)

create_powerups()

# إنشاء المنحدرات
ramps = []
def create_ramps():
    for ramp in ramps:
        destroy(ramp)
    ramps.clear()
    
    for i in range(8):
        x = random.uniform(-60, 60)
        z = random.uniform(-60, 60)
        ramp = Entity(
            model='cube',
            color=color.brown,
            scale=(4, 1, 8),
            position=(x, 0.5, z),
            rotation=(15, 0, 0),
            collider='box',
            tag='ramp'
        )
        ramps.append(ramp)

create_ramps()

# سيارة Algha Bug الذكية
algha_bug = None
algha_bug_active = False

def create_algha_bug():
    global algha_bug, algha_bug_active
    if algha_bug:
        destroy(algha_bug)
    
    algha_bug = Entity(
        model='cube',
        color=color.gold,
        scale=(2.5, 1.2, 5),
        position=(50, 1, 50),
        collider='box'
    )
    algha_bug_active = True

# تحديث حركة Algha Bug بناءً على تعلمها من اللاعب
def update_algha_bug_ai():
    global algha_bug, algha_bug_active, player_speed_history, algha_bug_learned_patterns, current_level
    
    if not algha_bug_active or not algha_bug:
        return
    
    # تحليل أنماط اللاعب
    if len(player_speed_history) > 10:
        avg_speed = sum(player_speed_history[-10:]) / len(player_speed_history[-10:])
        algha_bug_learned_patterns.append(avg_speed)
    
    # تحريك Algha Bug نحو اللاعب بسرعة متزايدة
    if player:
        direction = player.position - algha_bug.position
        direction.y = 0
        direction = direction.normalized()
        
        # السرعة تعتمد على مستوى التعلم والقوة
        base_speed = 15 + (current_level // 10) * algha_bug_power_multiplier
        if algha_bug_learned_patterns:
            base_speed += sum(algha_bug_learned_patterns[-5:]) / max(len(algha_bug_learned_patterns[-5:]), 1)
        
        algha_bug.position += direction * base_speed * time.dt
        
        # التحقق من الاصطدام باللاعب
        distance = distance_3d(algha_bug.position, player.position)
        if distance < 4:
            # خسارة اللاعب
            current_level = max(1, current_level - 1)
            level_text.text = f'Level: {current_level}/100'
            victory_text.text = 'Algha Bug caught you! Level decreased!'
            victory_text.color = color.red
            invoke(clear_victory_text, delay=2)

def clear_victory_text():
    victory_text.text = ''

# التحقق من اصطدام اللاعب بالعناصر
def check_collisions():
    global coins, speed_boost, flight_mode, flight_timer, algha_bug_active, algha_bug_defeated, algha_bug_power_multiplier
    
    # التحقق من العملات
    for coin in coins_entities[:]:
        if distance_3d(player.position, coin.position) < 3:
            coins += 1
            coins_text.text = f'Coins: {coins}'
            destroy(coin)
            coins_entities.remove(coin)
    
    # التحقق من العقبات
    for obs in obstacles:
        if distance_3d(player.position, obs.position) < 2:
            if hasattr(obs, 'tag'):
                if obs.tag == 'pit':
                    speed_boost = max(0.3, speed_boost - 0.5)
                    speed_text.text = f'Speed: {speed_boost:.1f}x'
                elif obs.tag == 'oil':
                    speed_boost = max(0.2, speed_boost - 0.7)
                    speed_text.text = f'Speed: {speed_boost:.1f}x'
    
    # التحقق من مشروبات القوة
    for pu in powerups[:]:
        if distance_3d(player.position, pu.position) < 2:
            if hasattr(pu, 'tag'):
                if pu.tag == 'speed':
                    speed_boost = min(3.0, speed_boost + 0.5)
                    speed_text.text = f'Speed: {speed_boost:.1f}x'
                elif pu.tag == 'flight':
                    flight_mode = True
                    flight_timer = 5  # 5 ثواني طيران
            destroy(pu)
            powerups.remove(pu)
    
    # التحقق من المنحدرات
    for ramp in ramps:
        if distance_3d(player.position, ramp.position) < 3:
            speed_boost = min(3.0, speed_boost + 0.3)
            speed_text.text = f'Speed: {speed_boost:.1f}x'
    
    # التحقق من الفوز على Algha Bug
    if algha_bug_active and algha_bug:
        distance = distance_3d(player.position, algha_bug.position)
        if distance < 4:
            # فوز اللاعب
            algha_bug_active = False
            algha_bug_defeated = True
            coins += 50  # مكافأة الفوز
            coins_text.text = f'Coins: {coins}'
            
            # انميشن النصر
            victory_text.text = 'VICTORY! Algha Bug Defeated!'
            victory_text.color = color.gold
            
            # زيادة قوة Algha Bug في المراحل القادمة
            if current_level >= 10:
                algha_bug_power_multiplier = 2.0
            
            invoke(clear_victory_text, delay=3)
            invoke(create_algha_bug, delay=5)  # العودة بعد 5 ثواني

# إنشاء النيازك في الأوقات الصعبة
def spawn_meteor():
    if random.random() < 0.01:  # احتمال ضئيل كل إطار
        x = random.uniform(-80, 80)
        meteor = Entity(
            model='sphere',
            color=color.orange,
            scale=(2, 2, 2),
            position=(x, 50, random.uniform(-80, 80)),
            collider='box',
            tag='meteor'
        )
        meteors.append(meteor)

def update_meteors():
    for meteor in meteors[:]:
        meteor.y -= 20 * time.dt  # سقوط النيزك
        if meteor.y < 0:
            # التحقق من اصطدام النيزك باللاعب
            if distance_3d(player.position, meteor.position) < 3:
                speed_boost = max(0.1, speed_boost - 0.8)
                speed_text.text = f'Speed: {speed_boost:.1f}x'
            destroy(meteor)
            meteors.remove(meteor)

# التحكم باللاعب
player_velocity = Vec3(0, 0, 0)
player_speed = 20

def update():
    global player_velocity, speed_boost, flight_mode, flight_timer, player_speed_history
    
    # حفظ سرعة اللاعب للتعلم
    player_speed_history.append(player_speed * speed_boost)
    if len(player_speed_history) > 100:
        player_speed_history.pop(0)
    
    # حركة اللاعب
    forward = camera.forward
    forward.y = 0
    forward = forward.normalized()
    
    right = camera.right
    right.y = 0
    right = right.normalized()
    
    move_direction = Vec3(0, 0, 0)
    
    if held_keys['w'] or held_keys['up arrow']:
        move_direction += forward
    if held_keys['s'] or held_keys['down arrow']:
        move_direction -= forward
    if held_keys['a'] or held_keys['left arrow']:
        move_direction -= right
    if held_keys['d'] or held_keys['right arrow']:
        move_direction += right
    
    # تطبيق السرعة والمعززات
    if move_direction != Vec3(0, 0, 0):
        move_direction = move_direction.normalized()
    
    current_speed = player_speed * speed_boost
    player_velocity = move_direction * current_speed * time.dt
    
    # وضع الطيران
    if flight_mode:
        flight_timer -= time.dt
        player.y += 5 * time.dt  # ارتفاع أثناء الطيران
        if flight_timer <= 0:
            flight_mode = False
            player.y = 1  # العودة للأرض
    else:
        player.y = 1  # البقاء على الأرض
    
    player.position += player_velocity
    
    # حدود الخريطة
    player.x = clamp(player.x, -95, 95)
    player.z = clamp(player.z, -95, 95)
    
    # تحديث الكاميرا
    camera.world_position = player.position + (0, 5, -15)
    
    # التحقق من التصادمات
    check_collisions()
    
    # تحديث النيازك
    spawn_meteor()
    update_meteors()
    
    # تحديث Algha Bug AI
    update_algha_bug_ai()
    
    # إعادة إنشاء العناصر إذا نفدت
    if len(coins_entities) < 5:
        create_coins()
    if len(obstacles) < 10:
        create_obstacles()
    if len(powerups) < 3:
        create_powerups()

# الانتقال للمستوى التالي عند جمع عدد كافٍ من العملات
def check_level_up():
    global current_level
    if coins >= current_level * 10:
        current_level += 1
        level_text.text = f'Level: {current_level}/100'
        
        # إنشاء Algha Bug كل 10 مستويات
        if current_level % 10 == 0:
            create_algha_bug()
            victory_text.text = f'Algha Bug appears at Level {current_level}!'
            victory_text.color = color.orange
            invoke(clear_victory_text, delay=2)
        
        # زيادة الصعوبة
        create_obstacles()
        create_powerups()
        create_ramps()

# تشغيل فحص المستوى بشكل دوري
invoke(check_level_up, delay=1, repeat=True)

# تعليمات التحكم
instructions = Text(
    text='WASD/Arrows: Move | Space: Boost\nCollect coins & avoid obstacles!\nDefeat Algha Bug every 10 levels!',
    position=(0.35, -0.45),
    scale=1,
    color=color.white
)

print("Game started! Use WASD or Arrow keys to move.")
print("Collect coins, avoid pits and oil, and defeat Algha Bug every 10 levels!")

app.run()
