import pygame as pg
import random
#import paho.mqtt.client as mqtt
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
        pg.init()
        self.screen = pg.display.set_mode((self.size_x, self.size_y))
        pg.display.set_caption('Fit&Fun')
        # Font, Colors
        self.font_name = pg.font.match_font('arial')
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

    def menu(self):
        image=pg.image.load(self.dir_img+'/menu.png')
        image=pg.transform.scale(image, (640,480))
        while True:
            self.screen.blit(image,(0,0))
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.display.quit()
                    exit() 
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.pos[0] in range(300,320) and event.pos[1] in range(200,220) :
                        self.game()

    def _draw_text(self, text, size, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.BLACK)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def game(self):
        image=pg.image.load(self.dir_img+'/level1.png')
        image=pg.transform.scale(image, (640,480))
        bgx=0

        player=pg.image.load(self.dir_img+'/boy.png')
        player=pg.transform.rotozoom(player,0,0.2)

        player_y = 325
        gravity=1
        jumpcount=0
        #jump=0

        crate=pg.image.load(self.dir_img+'/mushroom.png')
        crate=pg.transform.rotozoom(crate,0,0.8)
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

            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.display.quit()
                    print("QUIT")
                    #lock.release()
                    exit() 
                if event.type == pg.KEYDOWN:
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





class KeyboardController():
    
    def __init__(self, on_message):
        self.on_message = on_message
    
    def run(self):
        self.t1 = threading.Thread(target=self.kb_input_process, daemon=True)
        self.t1.start()
    
    class FakeMQTTMessage():
        def __init__(self, payload):
            self.payload = payload.encode("utf-8")
        
        def __str__(self):
            return self.payload
    
    def kb_input_process(self):
        state = 0    # state == 1 if a key is pressed
        n_press = 0
        last_ticks = pg.time.get_ticks()
        timer = 0
        virtual_speed = 0
        while True:
            if pg.key.get_focused():
                keys = pg.key.get_pressed()
                if state == 0 and keys[pg.K_UP]:
                    state = 1
                    n_press += 1
                elif state == 1 and not keys[pg.K_UP]:
                    state = 0
            
            current_ticks = pg.time.get_ticks()
            dt = current_ticks - last_ticks
            timer += dt
            last_ticks = current_ticks
            
            if timer > 100:
                # Every 100 millisec...
                virtual_speed = max(0, virtual_speed - 10)
                virtual_speed += n_press * 50
                message = self.FakeMQTTMessage(str(virtual_speed))
                #print(message)
                self.on_message(None, None, message)
                n_press = 0
                timer = 0
            
    def stop(self):
        self.lock.release()
        self.t1.join()



console=Console()
#mqtt_subscriber=MqttSubscriber(console.get_speed)
#mqtt_subscriber.run()
virtualController = KeyboardController(console.get_speed)
virtualController.run()
console.menu()
