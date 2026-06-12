import pygame
import cv2
import numpy as np
import sys
import os
from keras.models import load_model

# 获取资源文件路径（适配 PyInstaller 打包）
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

def predict_gesture(image):
    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

    image = (image / 127.5) - 1

    prediction = model.predict(image, verbose=0)
    index = np.argmax(prediction)
    class_name = class_names[index]
    # 实际应用中这里应该使用人工智能算法进行判断
    player_gesture = class_name[2:-1]
    return player_gesture

def get_ai_gesture(player_gesture):
    # 简单的AI逻辑：根据玩家的手势返回随机AI的手势
    # 实际应用中这里应该使用更复杂的算法
    if player_gesture == "paper":
        ai_gesture = "scissors"
    elif player_gesture == "rock":
        ai_gesture = "paper"
    elif player_gesture == "scissors":
        ai_gesture = "rock"
    else:
        ai_gesture = ""
    return ai_gesture
# 判定胜负
def determine_winner(player, ai):
    if player == ai: return "平局"
    if (player == "rock" and ai == "scissors") or (player == "scissors" and ai == "paper") or (player == "paper" and ai == "rock"):
        return "你赢了!"
    return "AI赢了!"

'''初始化pygame'''
pygame.init()

'''创建游戏窗口'''
W, H = 1000, 600 #游戏窗口大小
bg_color = (40, 40, 60) #背景颜色
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("AI手势猜拳") #标题
'''加载资源（汉字字体）'''
#汉字字体
pygame.font.init()
font = pygame.font.Font(resource_path('data/fonts/msyh.TTF'), 24)
'''加载音效'''
pygame.mixer.init()
sound_open = pygame.mixer.Sound(resource_path('data/sounds/open_sound.wav'))
'''加载图片'''
ai_paper = pygame.image.load(resource_path("data/images/ai_paper.png"))
ai_rock = pygame.image.load(resource_path("data/images/ai_rock.png"))
ai_scissors = pygame.image.load(resource_path("data/images/ai_scissors.png"))
ai_original = pygame.image.load(resource_path("data/images/ai_original.png"))
#打开摄像头
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FPS, 30)

'''初始化游戏状态'''
game_state = "waiting"  # waiting, playing, result
player_gesture = ""
ai_gesture = ""
round_count = 0
player_score = 0
ai_score = 0
countdown = 3
temp = None
sound = None
last_time = pygame.time.get_ticks() #用于更新倒计时的上一次记录的时间
clock = pygame.time.Clock() #开启游戏时钟

model = load_model(resource_path("data/models/keras_model_good.h5"), compile=False)

with open(resource_path("data/labels/labels.txt"), "r", encoding="utf-8") as f:
    class_names = f.readlines()

# 预先缩放AI手势图片（避免每帧重复缩放）
ai_paper = pygame.transform.smoothscale(ai_paper, (150, 150))
ai_scissors = pygame.transform.smoothscale(ai_scissors, (150, 150))
ai_rock = pygame.transform.smoothscale(ai_rock, (150, 150))
ai_original = pygame.transform.smoothscale(ai_original, (150, 150))

'''主循环'''
while True:
    '''事件处理'''

    for event in pygame.event.get(): #获取用户的操作
        if event.type == pygame.KEYDOWN: #如果用户在键盘上按键
            if event.key == pygame.K_SPACE: #如果按下空格键
                sound_open.play()
                if game_state in ("waiting", "result"): #如果游戏还没开始，开始新回合
                    game_state = "playing"
                    round_count += 1 #回合数加1
                    countdown = 3 #重置三秒倒计时
                    last_time = pygame.time.get_ticks() #更新上一次记录的时间


        if event.type == pygame.MOUSEBUTTONDOWN: #如果用户在键盘上按键
            if event.button == 1: #如果按下左键
                sound_open.play()
                if game_state in ("waiting", "result"): #如果游戏还没开始，开始新回合
                    game_state = "playing"
                    round_count += 1 #回合数加1
                    countdown = 3 #重置三秒倒计时
                    last_time = pygame.time.get_ticks() #更新上一次记录的时间


        if event.type == pygame.QUIT: #如果关闭窗口，退出游戏
            cap.release()
            pygame.quit()
            sys.exit()

    '''游戏逻辑和状态更新'''
    # 获取摄像头画面
    ret, frame = cap.read()

    height, width = frame.shape[:2]

    start_x = (width - 224) // 2
    start_y = (height - 224) // 2

    image = frame[start_y:start_y + 224, start_x:start_x + 224]

    cv2.rectangle(frame, (start_x, start_y), (start_x + 224, start_y + 224), (0, 255, 0), 3)

    # 在游戏开始的状态中，每1000毫秒更新一次倒计时，如果倒计时结束，则进行胜负判断
    current_time = pygame.time.get_ticks()
    if game_state == "playing" and current_time - last_time > 1000:
        countdown -= 1  # 倒计时减1
        if countdown <= 0:  # 如果倒计时结束
            game_state = "result"
            player_gesture = predict_gesture(image)
            ai_gesture = get_ai_gesture(player_gesture)
            result = determine_winner(player_gesture, ai_gesture)
            if "你赢了" in result:
                player_score += 1
                sound = pygame.mixer.Sound(resource_path('data/sounds/victory.wav'))
            elif "AI赢了" in result:
                ai_score += 1
                sound = pygame.mixer.Sound(resource_path('data/sounds/defeat.wav'))
            else:
                sound = pygame.mixer.Sound(resource_path('data/sounds/open_sound.wav'))

            temp = image.copy()
            temp = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB)
            temp = cv2.resize(temp, (150, 150))
            temp = np.rot90(temp)
            temp = pygame.surfarray.make_surface(temp)
            sound.play()
        last_time = current_time  # 更新上一次记录的时间

    '''界面绘制'''
    # 背景
    screen.fill(bg_color)
    # 标题和分数
    title = font.render("AI手势猜拳游戏", True, (255, 200, 100))
    screen.blit(title, (W // 2 - title.get_width() // 2, 20))
    score_text = font.render(f"回合: {round_count}  你: {player_score}  AI: {ai_score}", True, (200, 200, 255))
    screen.blit(score_text, (W // 2 - score_text.get_width() // 2, 70))

    #摄像头画面，这里需要对opencv视频帧进行处理，使得兼容pygame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    frame = cv2.resize(frame, (400, 300))

    frame = np.rot90(frame) #因为opencv和pygame坐标系差异，逆时针旋转90度
    #将视频帧转换为pygame的Surface类型并绘制出来
    frame = pygame.surfarray.make_surface(frame)
    pygame.draw.rect(screen, (20, 20, 30), (W // 2 - 410, 120, 820, 320))
    screen.blit(frame, (W // 2 - 400, 130))

    ai_text = font.render(" ——AI的出拳", True, (100, 200, 255))
    screen.blit(ai_text, (int(W // 1.5 + ai_text.get_width() - 210 // 2), 185))

    player_text = font.render(" ——你的出拳", True, (100, 200, 255))
    screen.blit(player_text, (int(W // 1.5 + player_text.get_width() - 210 // 2), 340))

    if ai_gesture == "paper":
        screen.blit(ai_paper, (W // 2 +55 , 130))
        screen.blit(temp, (W // 2 + 55, 290))
    elif ai_gesture == "rock":
        screen.blit(ai_rock, (W // 2 +55, 130))
        screen.blit(temp, (W // 2 + 55, 290))
    elif ai_gesture == "scissors":
        screen.blit(ai_scissors, (W // 2 +55, 130))
        screen.blit(temp, (W // 2 + 55, 290))
    else :
        screen.blit(ai_original, (W // 2 +55, 130))
        screen.blit(ai_original, (W // 2 + 55, 290))

    # 游戏状态显示
    if game_state == "waiting": #等待开始新回合
        prompt = font.render("按空格键或者点击左键开始新回合", True, (100, 200, 255))
        screen.blit(prompt, (W // 2 - prompt.get_width() // 2, 470))
    elif game_state == "playing": #等待玩家出拳
        count_text = font.render(f"倒计时：{countdown}", True, (255, 100, 100))
        screen.blit(count_text, (W // 2 - count_text.get_width() // 2, 470))
        screen.blit(ai_original, (W // 2 + 55, 130))
        screen.blit(ai_original, (W // 2 + 55, 290))
    elif game_state == "result": #倒计时结束，显示结果


        #设置结果显示颜色
        if "你赢了" in result:
            win_text_color = (100, 255, 100)  # 如果玩家赢了，结果显示为绿色

        elif "AI赢了" in result:
            win_text_color = (255, 100, 100)  # 如果AI赢了，结果显示为红色

        else:
            win_text_color = (200, 200, 200)  # 如果平局，结果显示为灰色

                #绘制出拳结果
        result_text = font.render(f"你出: {player_gesture}  AI出: {ai_gesture}", True, (255, 255, 100))
        screen.blit(result_text, (W // 2 - result_text.get_width() // 2, 470))
        win_text = font.render(result, True, win_text_color )
        screen.blit(win_text, (W // 2 - win_text.get_width() // 2, 510))
        restart = font.render("按空格键或者点击左键继续", True, (100, 200, 255))
        screen.blit(restart, (W // 2 - restart.get_width() // 2, 550))

    '''刷新显示'''
    # 刷新屏幕，把在后端缓冲区完成绘制的新内容更新到屏幕上显示，同时把原来前端缓冲区的内容放到后端缓冲区，为下一轮绘图做准备
    pygame.display.flip()
    #按照30帧每秒的速度更新游戏状态，防止游戏运行过快或过慢
    clock.tick(30)