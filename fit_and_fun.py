import pygame
import random
import paho.mqtt.client as mqtt
import threading


class Console():

    def __init__(self):
        # Configuration
        self.size_x=640
        self.size_y=480
        self.dir_img='images'
        # Threshold
        self.ROT_SPEED_MIN=10
        # rot speed max = 700, screen speed max = 3 => 3/600
        self.SPEED_RATIO=0.005
        # Control variable
        self.jump=0
        self._on_message = None
        self.speed=0
        self.rot_speed=0
        self.score=0
        # Screen init
        pygame.init()
        self.screen = pygame.display.set_mode((self.size_x, self.size_y))
        pygame.display.set_caption('Fit&Fun')
        # Font, Colors
        self.font_name = pygame.font.match_font('arial')
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

    def menu(self):
        image=pygame.image.load(self.dir_img+'/menu.png')
        image=pygame.transform.scale(image, (640,480))
        while True:
            self.screen.blit(image,(0,0))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    exit() 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.pos[0] in range(300,320) and event.pos[1] in range(200,220) :
                        self.game()

    def _draw_text(self, text, size, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.BLACK)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def game(self):
        image=pygame.image.load(self.dir_img+'/level1.png')
        image=pygame.transform.scale(image, (640,480))
        bgx=0

        player=pygame.image.load(self.dir_img+'/boy.png')
        player=pygame.transform.rotozoom(player,0,0.2)

        player_y = 325
        gravity=1
        jumpcount=0
        #jump=0

        crate=pygame.image.load(self.dir_img+'/crate.png')
        crate=pygame.transform.rotozoom(crate,0,0.8)
        crate_x=700
        crate_speed=2

        while True:
            self.screen.blit(image,(bgx-640,0))
            self.screen.blit(image,(bgx,0))
            self.screen.blit(image,(bgx+640,0))

            bgx = bgx - self.speed
            if bgx <= -640:
                bgx=0

            p_rect=self.screen.blit(player,(50, player_y))

            player_y=325-40*self.jump
            
            c_rect=self.screen.blit(crate,(crate_x,250))

            crate_x -= crate_speed

            if crate_x < -50:
                crate_x=random.randint(700,800)
                crate_speed=random.randint(2,3)

            if p_rect.colliderect(c_rect):
                self.score+=10
                crate_x=-51
             
            
            msg='Speed: '+str(round(self.rot_speed))+ ' - Score: '+ str(self.score)
            self._draw_text(msg, 30, 220, 1)

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    print("QUIT")
                    #lock.release()
                    exit() 
                if event.type == pygame.KEYDOWN:
                    self.jump=1

    def get_speed(self, client, userdata, message):
        try:
            rot_speed=float(str(message.payload.decode("utf-8"))) 
            if rot_speed < self.ROT_SPEED_MIN:
                self.rot_speed=0
                self.speed=0
            else:
                self.rot_speed=rot_speed
                self.speed=round(self.SPEED_RATIO*self.rot_speed)
        except Exception:
            self.speed=0
            self.rot_speed=0

        self.score=self.score+self.speed
        if self.speed > 2:
            self.jump=1
        else:
            self.jump=0

        print("speed: " , self.rot_speed, self.speed)
        print("score: " , self.score)

class MqttSubscriber():

    def __init__(self, on_message):
        self.on_message=on_message
        self.value=10
        self.mqttBroker ='localhost'
        client = mqtt.Client("Console")
        client.connect(self.mqttBroker) 
        self.lock = threading.Lock()
        self.lock.acquire()


    def subscribe_connect(self): 
        print("START SUBSCRIBER")
        client = mqtt.Client("Console")
        client.connect(self.mqttBroker) 

        client.loop_start()
        client.subscribe("fit_and_fun/speed")
        client.on_message=self.on_message 
        
        self.lock.acquire()
        client.loop_stop()
        print("END SUBSCRIBER")
   

    def run(self):
        self.t1=threading.Thread(target=self.subscribe_connect)
        self.t1.start()


    def stop(self):
        self.lock.release()
        self.t1.join()


console=Console()
mqtt_subscriber=MqttSubscriber(console.get_speed)
mqtt_subscriber.run()
console.menu()
