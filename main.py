import os
import sys

if getattr(sys, 'frozen', False):
    snap7_path = os.path.join(sys._MEIPASS, 'snap7')
    os.environ['PATH'] = snap7_path + os.pathsep + os.environ['PATH']

# This enables the import of snap7 with pyinstaller

import math
from os import path
from configparser import ConfigParser

from objects.filler import Filler
from sprites import *
from plcConnection import *
from objects.machine import *
from objects.bottle import *
from objects.productionLine import ProductionLine

import sys
import os


class Simulator:
    def __init__(self):
        # initialize simulator window, etc.
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        # pg.display.set_icon()
        self.clock = pg.time.Clock()
        self.font_name = pg.font.match_font(FONT_NAME)
        self.dir = ''
        self.config = ConfigParser()
        self.fps = 0
        self.max_fps = 1
        self.manual_mode_fps = 1
        self.unlimited_fps_on = False
        self.auto_fps_on = False
        self.plc_address = ''
        self.plc_rack = 0
        self.plc_slot = 1
        self.plc_port = 102  # default port: 102
        self.plc_read_thread = None
        self.plc_write_thread = None
        self.plc_status_thread = None
        self.inputs = []
        self.outputs = []
        self.io_lock = False
        self.running = False
        self.start_simulation = False
        self.self_processing_on = False
        self.manual_mode_on = False
        self.random_space_on = False
        self.min_space = 0
        self.max_space = 0
        self.next_space = 0
        self.broken_bottle_chance = BROKEN_BOTTLE_PROB
        self.fillers = []
        self.filler_index = 0
        self.filler_color = FILLER_COLOR
        self.filler_transparency = FILLER_TRANSPARENCY
        self.filler_update = False
        self.last_bottle = None
        self.texts = []
        self.setting_page = 0
        self.show_help = False
        self.is_start = False
        self.is_error = False

        self.sim_count = 0
        self.read_pps = 0
        self.write_pps = 0
        self.read_thread_count = 0
        self.write_thread_count = 0
        self.status_thread_count = 0
        self.read_operation_count = 0
        self.write_operation_count = 0
        self.status_operation_count = 0
        self.time_mem = 0
        self.time_set = 0
        self.timer_on = False

    def initial(self):
        # Simulation initialization
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        # Load images
        self.background = pg.image.load(self.resource_path("img/bg.png")).convert()
        self.machine_A = pg.image.load(self.resource_path("img/machine_A.png")).convert()
        self.machine_B = pg.image.load(self.resource_path("img/machine_B.png")).convert()
        self.machine_C = pg.image.load(self.resource_path("img/machine_C.png")).convert()
        self.machine_A_top = pg.image.load(self.resource_path("img/machine_A_top.png")).convert()
        self.machine_B_top = pg.image.load(self.resource_path("img/machine_B_top.png")).convert()
        self.machine_C_top = pg.image.load(self.resource_path("img/machine_C_top.png")).convert()
        self.machine_A_sensor = pg.image.load(self.resource_path("img/machine_A_sensor.png")).convert()
        self.machine_B_sensor = pg.image.load(self.resource_path("img/machine_B_sensor.png")).convert()
        self.machine_C_sensor = pg.image.load(self.resource_path("img/machine_C_sensor.png")).convert()
        self.laser = pg.image.load(self.resource_path("img/laser.png")).convert()
        self.bottle_images = []  # For loading bottle sprites with alpha channel
        for i in range(1, 5):
            self.bottle_images.append(
                pg.image.load(self.resource_path('img/bottle_sprite_part{}.png'.format(i))).convert_alpha())
        self.help = pg.image.load(self.resource_path('img/help.png'.format())).convert_alpha()
        self.checked = pg.image.load(self.resource_path('img/checked.png'.format())).convert_alpha()
        self.checked_inactive = pg.image.load(self.resource_path('img/checked_inactive.png'.format())).convert_alpha()
        self.checked_locked = pg.image.load(self.resource_path('img/checked_locked.png'.format())).convert_alpha()
        self.control_panel = pg.image.load(self.resource_path("img/control_panel.png")).convert()
        self.filler_buttons = []
        self.filler_buttons.append(pg.image.load(self.resource_path('img/filler_minus_ten.png'.format())).convert_alpha())
        self.filler_buttons.append(pg.image.load(self.resource_path('img/filler_minus_one.png'.format())).convert_alpha())
        self.filler_buttons.append(pg.image.load(self.resource_path('img/filler_plus_one.png'.format())).convert_alpha())
        self.filler_buttons.append(pg.image.load(self.resource_path('img/filler_plus_ten.png'.format())).convert_alpha())
        self.filler_buttons.append(pg.image.load(self.resource_path('img/filler_inf.png'.format())).convert_alpha())
        self.filler_buttons.append(pg.image.load(self.resource_path('img/filler_down.png'.format())).convert_alpha())
        self.filler_buttons.append(pg.image.load(self.resource_path('img/filler_up.png'.format())).convert_alpha())
        # Load sprite sheets
        self.lightGreenSpriteSheet = Spritesheet(self.resource_path("img/light_green_sprites.png"))
        self.lightOrangeSpriteSheet = Spritesheet(self.resource_path("img/light_orange_sprites.png"))
        self.lightRedSpriteSheet = Spritesheet(self.resource_path("img/light_red_sprites.png"))
        self.productionLineSpriteSheet = Spritesheet(self.resource_path("img/production_line_sprites.png"))
        # Preparing io area
        for i in range(37):
            self.inputs.append(False)
        self.inputs[0] = True
        for i in range(24):
            self.outputs.append(False)
        # Reading settings from .py file
            self.max_fps = FPS
            self.manual_mode_fps = MANUAL_MODE_FPS
            self.min_space = MIN_SPACE
            self.max_space = MAX_SPACE
            self.next_space = randrange(self.min_space, self.max_space)
        # Reading settings from .ini file
        try:
            self.config.read('simulator.ini')
            # [simulator]
            self.start_simulation = self.config.getboolean('simulator', 'start_simulation')
            self.broken_bottle_chance = self.config.getint('simulator', 'broken_bottle_probability')
            if self.broken_bottle_chance < 0:
                self.broken_bottle_chance = 0
            if self.broken_bottle_chance > 100:
                self.broken_bottle_chance = 100
            self.min_space = self.config.getint('simulator', 'min_bottles_space')
            if self.min_space < 10:
                self.min_space = 10
            self.max_space = self.config.getint('simulator', 'max_bottles_space')
            if self.max_space < self.min_space:
                self.max_space = self.min_space
            self.next_space = randrange(self.min_space, self.max_space)
            self.max_fps = self.config.getint('simulator', 'max_fps')
            if self.max_fps < 30:
                self.max_fps = 30
            if self.max_fps > 800:
                self.max_fps = 800
            self.manual_mode_fps = self.config.getint('simulator', 'manual_mode_fps')
            if self.manual_mode_fps < 30:
                self.manual_mode_fps = 30
            if self.manual_mode_fps > 800:
                self.manual_mode_fps = 800
            self.unlimited_fps_on = self.config.getboolean('simulator', 'unlimited_fps')
            self.auto_fps_on = self.config.getboolean('simulator', 'auto_fps')
            self.timer_on = self.config.getboolean('simulator', 'timer_on')
            self.time_set = self.config.getint('simulator', 'timer_time')
            if self.time_set <= 0:
                self.time_set = 0
                self.timer_on = False
            # [plc]
            self.plc_address = self.config.get('plc', 'address')
            self.plc_rack = self.config.getint('plc', 'rack')
            self.plc_slot = self.config.getint('plc', 'slot')
            self.plc_port = self.config.getint('plc', 'port')
            # [filler]
            # Preparing fillers list
            self.fillers.append(Filler(self.config.get('filler_1', 'name'),
                                       self.config.getint('filler_1', 'red'),
                                       self.config.getint('filler_1', 'green'),
                                       self.config.getint('filler_1', 'blue'),
                                       self.config.getfloat('filler_1', 'transparency'),
                                       self.config.getint('filler_1', 'amount'),
                                       self.config.getboolean('filler_1', 'infinite')))
            self.fillers.append(Filler(self.config.get('filler_2', 'name'),
                                       self.config.getint('filler_2', 'red'),
                                       self.config.getint('filler_2', 'green'),
                                       self.config.getint('filler_2', 'blue'),
                                       self.config.getfloat('filler_2', 'transparency'),
                                       self.config.getint('filler_2', 'amount'),
                                       self.config.getboolean('filler_2', 'infinite')))
            self.fillers.append(Filler(self.config.get('filler_3', 'name'),
                                       self.config.getint('filler_3', 'red'),
                                       self.config.getint('filler_3', 'green'),
                                       self.config.getint('filler_3', 'blue'),
                                       self.config.getfloat('filler_3', 'transparency'),
                                       self.config.getint('filler_3', 'amount'),
                                       self.config.getboolean('filler_3', 'infinite')))
        except Exception as e:
            print(e)
        # Resetting counters for measurements
        self.sim_count = 0
        self.read_pps = 0
        self.write_pps = 0
        self.status_thread_count = 0
        self.write_thread_count = 0
        self.read_thread_count = 0
        self.status_operation_count = 0
        self.write_operation_count = 0
        self.read_operation_count = 0
        self.time_mem = 0
        self.setting_page = 0
        self.filler_update = True
        # Initial texts render
        self.texts.append([])
        self.texts.append([])
        self.texts.append([])
        self.texts.append([])
        self.texts.append([])

        self.texts[0].append(self.render_text("Broken bottle chance: ", 20, WHITE))
        self.texts[0].append(self.render_text("current chance: " + str(self.broken_bottle_chance) + "%", 20, WHITE))
        self.texts[0].append(self.render_text("Start simulation:", 20, WHITE))
        self.texts[0].append(self.render_text("Self processing:", 20, WHITE))
        self.texts[0].append(self.render_text("Manual mode:", 20, WHITE))
        self.texts[0].append(self.render_text("Random space:", 20, WHITE))
        self.texts[1].append(self.render_text("PLC info:", 20, WHITE))
        self.texts[1].append(self.render_text("PLC connected: False", 15, WHITE))
        self.texts[1].append(self.render_text("PLC name: unknown", 15, WHITE))
        self.texts[1].append(self.render_text("PLC type: unknown", 15, WHITE))
        self.texts[1].append(self.render_text("CPU state: unknown", 15, WHITE))
        self.texts[1].append(self.render_text("Dow./Up. rate: 0/0 p/s", 15, WHITE))
        for filler in self.fillers:
            self.texts[2].append(self.render_text(filler.name, 20, WHITE))
        for filler in self.fillers:
            self.texts[2].append(self.render_text(str(filler.amount), 20, WHITE))
        self.texts[3].append(self.render_text("FPS limit: ", 20, WHITE))
        self.texts[3].append(self.render_text("max " + str(self.max_fps) + " FPS", 20, WHITE))
        self.texts[3].append(self.render_text("Unlimited FPS:", 20, WHITE))
        self.texts[3].append(self.render_text("Auto FPS:", 20, WHITE))

        self.texts[4].append(self.render_text("Simulator", 15, WHITE))
        self.texts[4].append(self.render_text("PLC", 15, WHITE))
        self.texts[4].append(self.render_text("Liquid schedule", 15, WHITE))
        self.texts[4].append(self.render_text("Time", 15, WHITE))
        self.texts[4].append(self.render_text("S.P.", 15, WHITE))
        # Preparing new simulation
        self.is_start = False
        self.is_error = False
        self.fps = FPS
        self.new()

    def new(self):
        # Simulation startup
        # Creating simulation object groups
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.machines = pg.sprite.Group()
        self.machines_top = pg.sprite.Group()
        self.machines_sensor = pg.sprite.Group()
        self.lasers = pg.sprite.Group()
        self.lights = pg.sprite.Group()
        self.bottles = pg.sprite.Group()
        self.production_lines = pg.sprite.Group()
        # Creating simulation objects
        machine_types = ["A", "B", "C"]
        for i in range(3):
            MachineTop(self, 250 + i * 250, 0, machine_types[i])
            Machine(self, 250 + i * 250, 135, machine_types[i])
            MachineSensor(self, 250 + i * 250, 335, machine_types[i])
        for i in range(5):
            ProductionLine(self, 0 + i * 200, 460)
        # creating control_panel lights
        self.control_panel_G = Light2(self, 175, 563, 'G')
        self.control_panel_R = Light2(self, 175, 578, 'R')
        self.control_panel_G.is_on = True
        # creating first bottle
        self.last_bottle = Bottle(self, -100, 320)
        # creating read (main) thread objects for exchanging data with PLC
        self.plc_read_thread = PLCRead(self)
        # Creating control variables 
        self.production_line_run = False  # production line run (input)
        self.machine_A_ROG = [False, False, False]  # machine sensor lights red/orange/green (inputs)
        self.machine_B_ROG = [False, False, False]
        self.machine_C_ROG = [False, False, False]
        self.machine_A_top_ROG = [False, False, False]  # machine top lights red/orange/green (inputs)
        self.machine_B_top_ROG = [False, False, False]
        self.machine_C_top_ROG = [False, False, False]
        self.machine_A_LR = [False, False]  # sensors left/right (outputs)
        self.machine_B_LR = [False, False]
        self.machine_C_LR = [False, False]
        # operation go_down/go_up/tool_on/tool_off/ack (inputs)
        self.machine_A_operation_in = [False, False, False, False, False, False]
        self.machine_B_operation_in = [False, False, False, False, False, False]
        self.machine_C_operation_in = [False, False, False, False, False, False]
        # operation start_pos/end_pos/tool_work/tool_ready/error (outputs)
        self.machine_A_operation_out = [False, False, False, False, False]
        self.machine_B_operation_out = [False, False, False, False, False]
        self.machine_C_operation_out = [False, False, False, False, False]
        # Creating self_processing_on variables
        self.sp_last_A_LR = [False, False]
        self.sp_last_B_LR = [False, False]
        self.sp_last_C_LR = [False, False]
        self.sp_A_to_B = ''
        self.sp_B_to_C = ''
        self.sp_during_operation = False
        self.sp_openA = True
        self.sp_openB = True
        self.sp_openC = True
        self.sp_A_ok = False
        self.sp_B_ok = False
        self.sp_C_ok = False
        self.sp_A_end_pos = False
        self.sp_B_end_pos = False
        self.sp_C_end_pos = False

        # Starting simulation
        self.self_processing_on = False
        self.manual_mode_on = False
        self.run()

    def run(self):
        # Starting status/read/write threads for exchanging data with PLC
        self.plc_read_thread.start()
        # Simulation loop
        self.running = True
        # Wait for PLC connection before starting simulation
        print("Waiting for PLC connection...")
        connection_wait_time = time.time()
        attempt_count = 0
        while not self.plc_read_thread.connected and self.running:
            # Check for events to allow user to exit during connection attempt
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
            # Draw waiting screen
            self.screen.fill(DARK_GRAY)
            waiting_text = self.render_text("Waiting for PLC connection...", 30, WHITE)
            self.screen.blit(waiting_text, (WIDTH//2 - waiting_text.get_width()//2, HEIGHT//2 - 70))
            address_text = self.render_text(f"Attempting to connect to: {self.plc_address}", 20, WHITE)
            self.screen.blit(address_text, (WIDTH//2 - address_text.get_width()//2, HEIGHT//2 - 30))
            
            # Show the connection attempt count
            attempt_count += 1
            attempts_text = self.render_text(f"Attempt {attempt_count}", 20, WHITE)
            self.screen.blit(attempts_text, (WIDTH//2 - attempts_text.get_width()//2, HEIGHT//2))
            
            # Display timeout message after 10 seconds
            if time.time() - connection_wait_time > 10:
                timeout_text = self.render_text("Connection taking longer than expected. Check PLC address and settings.", 15, WHITE)
                self.screen.blit(timeout_text, (WIDTH//2 - timeout_text.get_width()//2, HEIGHT//2 + 30))
                
                # Add more helpful text after 15 seconds
                if time.time() - connection_wait_time > 15:
                    help_text1 = self.render_text("1. Verify the PLC is powered on and accessible on the network", 15, WHITE)
                    help_text2 = self.render_text("2. Check that the IP address, rack, and slot in simulator.ini are correct", 15, WHITE)
                    help_text3 = self.render_text("3. Ensure no firewall is blocking the connection", 15, WHITE)
                    self.screen.blit(help_text1, (WIDTH//2 - help_text1.get_width()//2, HEIGHT//2 + 60))
                    self.screen.blit(help_text2, (WIDTH//2 - help_text2.get_width()//2, HEIGHT//2 + 80))
                    self.screen.blit(help_text3, (WIDTH//2 - help_text3.get_width()//2, HEIGHT//2 + 100))
            
            pg.display.flip()
            time.sleep(0.5)
            
        # If we exited the loop but aren't connected, exit
        if not self.plc_read_thread.connected:
            print("Failed to connect to PLC. Exiting.")
            self.running = False
            
        if self.timer_on:
            self.time_mem = time.time()
            
        while self.running:
            self.sim_count += 1
            
            # Check if we're still connected to PLC
            if not self.plc_read_thread.connected:
                print("PLC connection lost. Stopping simulation.")
                # Try one more time to reconnect
                self.plc_read_thread.connection_attempts = 0
                # Wait for a moment before stopping completely
                time.sleep(2)
                # If still not connected, stop the simulation
                if not self.plc_read_thread.connected:
                    self.running = False
                    break
                
            # fps management
            if self.manual_mode_on:
                self.fps = self.manual_mode_fps
            elif self.auto_fps_on and self.plc_read_thread.connected:
                if self.read_pps <= self.write_pps:
                    self.fps = math.ceil(self.read_pps * 0.9)
                else:
                    self.fps = math.ceil(self.write_pps * 0.9)
            elif self.unlimited_fps_on:
                self.fps = 0
            else:
                self.fps = self.max_fps
            self.clock.tick(self.fps)
            # input processing
            self.events()
            # objects state update
            if self.start_simulation:
                self.update()
            self.filler()
            # processing mode
            if self.manual_mode_on:
                self.manual_mode()
            elif self.self_processing_on:
                self.self_processing()
            else:
                self.plc_processing()
            # drawing frame
            self.draw()
            # timer execution
            if self.timer_on:
                if time.time() - self.time_mem >= self.time_set:
                    print("Simulation end by timer, after " + str(self.time_set) + " sec.")
                    self.running = False
        # at the end finish threads processes
        if not self.running:
            self.plc_read_thread.running = False
            self.plc_read_thread.join()

    def events(self):
        # Simulation loop events
        if not self.plc_read_thread.connected:
            # Only check for quit events if not connected to PLC
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
            return
            
        updated_broken_bottle_chance = False
        updated_self_processing = False
        updated_random_space = False
        updated_manual_mode = False
        updated_max_fps = False
        # list of pressed keys (for the purpose of shortcut combinations)
        keys = pg.key.get_pressed()
        # continuous checking of...
        # ...keys allowing action in timer_on
        if self.manual_mode_on:
            if keys[pg.K_LCTRL]:
                if keys[pg.K_LEFT]:
                    for bottle in self.bottles:
                        bottle.rect.x -= 10
                if keys[pg.K_RIGHT]:
                    for bottle in self.bottles:
                        bottle.rect.x += 10
            else:
                if keys[pg.K_LEFT]:
                    for bottle in self.bottles:
                        bottle.rect.x -= 1
                if keys[pg.K_RIGHT]:
                    for bottle in self.bottles:
                        bottle.rect.x += 1
        # ...mouse position for smoothing slider changes
        if pg.mouse.get_pressed()[0]:
            pos = pg.mouse.get_pos()
            x = pos[0]
            y = pos[1]
            # check if mouse is on proper position  of broken bottle chance setting
            if 10 <= x <= 230:
                if 60 <= y <= 80:
                    if x < 20:
                        x = 20
                    if x > 220:
                        x = 220
                    x -= 20
                    if self.setting_page == 0:
                        self.broken_bottle_chance = math.ceil(x / 2)
                        updated_broken_bottle_chance = True
                    elif self.setting_page == 3:
                        self.max_fps = math.ceil(30 + (x * 3.85))
                        updated_max_fps = True
        # single checking of pressing keys
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                self.running = False
            # check for pressing keyboard key
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_F1:
                    self.show_help = not self.show_help
                if event.key == pg.K_F2:
                    self.start_simulation = not self.start_simulation
                if event.key == pg.K_F3:
                    updated_self_processing = True
                if event.key == pg.K_F4:
                    updated_manual_mode = True
                if event.key == pg.K_F5:
                    updated_random_space = True
                if event.key == pg.K_F6:
                    self.unlimited_fps_on = not self.unlimited_fps_on
                if event.key == pg.K_F7:
                    self.auto_fps_on = not self.auto_fps_on
                if event.key == pg.K_TAB and keys[pg.K_LCTRL]:
                    self.setting_page += 1
                    if self.setting_page > 3:
                        self.setting_page = 0
                if event.key == pg.K_DOWN:
                    if keys[pg.K_LCTRL]:
                        self.broken_bottle_chance -= 10
                    else:
                        self.broken_bottle_chance -= 1
                    updated_broken_bottle_chance = True
                if event.key == pg.K_UP:
                    if keys[pg.K_LCTRL]:
                        self.broken_bottle_chance += 10
                    else:
                        self.broken_bottle_chance += 1
                    updated_broken_bottle_chance = True
                if event.key == pg.K_PAGEDOWN:
                    if keys[pg.K_LCTRL]:
                        self.max_fps -= 10
                    else:
                        self.max_fps -= 1
                    updated_max_fps = True
                if event.key == pg.K_PAGEUP:
                    if keys[pg.K_LCTRL]:
                        self.max_fps += 10
                    else:
                        self.max_fps += 1
                    updated_max_fps = True
                if self.manual_mode_on:
                    if event.key == pg.K_SPACE:
                        self.production_line_run = not self.production_line_run
                    if keys[pg.K_LCTRL]:
                        if event.key == pg.K_a:
                            self.machine_A_operation_in[4] = True
                        if event.key == pg.K_b:
                            self.machine_B_operation_in[4] = True
                        if event.key == pg.K_c:
                            self.machine_C_operation_in[4] = True
                    else:
                        if event.key == pg.K_a:
                            self.machine_A_operation_in[5] = True
                        if event.key == pg.K_b:
                            self.machine_B_operation_in[5] = True
                        if event.key == pg.K_c:
                            self.machine_C_operation_in[5] = True
            # check for releasing keyboard key
            if event.type == pg.KEYUP:
                if self.manual_mode_on:
                    if keys[pg.K_LCTRL]:
                        if event.key == pg.K_a:
                            self.machine_A_operation_in[4] = False
                        if event.key == pg.K_b:
                            self.machine_B_operation_in[4] = False
                        if event.key == pg.K_c:
                            self.machine_C_operation_in[4] = False
                    else:
                        if event.key == pg.K_a:
                            self.machine_A_operation_in[5] = False
                        if event.key == pg.K_b:
                            self.machine_B_operation_in[5] = False
                        if event.key == pg.K_c:
                            self.machine_C_operation_in[5] = False
            # check for pressing mouse button
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                x = pos[0]
                y = pos[1]
                # switching control_panel variables
                if 563 <= y <= 587:
                    if 5 <= x <= 54:
                        if not self.is_error:
                            self.is_start = True
                    if 60 <= x <= 109:
                        self.is_start = False
                    if 115 <= x <= 164:
                        for machine in self.machines:
                            machine.operation_error = False
                # switching setting menu pages
                if y <= 25:
                    if x < 73:
                        self.setting_page = 0
                    if 73 <= x <= 112:
                        self.setting_page = 1
                    if 112 <= x <= 223:
                        self.setting_page = 2
                    if 223 <= x <= 256:
                        self.setting_page = 3
                # switching self_processing_on and manual_mode_on settings
                if 160 <= x <= 185 and self.setting_page == 0:
                    if 130 <= y <= 155:
                        self.start_simulation = not self.start_simulation
                    if 170 <= y <= 195:
                        updated_self_processing = True
                    if 210 <= y <= 235:
                        updated_manual_mode = True
                    if 250 <= y <= 275:
                        self.random_space_on = not self.random_space_on
                elif 160 <= x <= 185 and self.setting_page == 3:
                    if 130 <= y <= 155:
                        self.unlimited_fps_on = not self.unlimited_fps_on
                    if 170 <= y <= 195:
                        self.auto_fps_on = not self.auto_fps_on
                # switching machines self processing mode
                if 50 <= y <= 75 and self.start_simulation and not (self.self_processing_on or self.manual_mode_on):
                    if 430 <= x <= 455:
                        for machine in self.machines:
                            if machine.type == "A":
                                machine.self_processing_mem = not machine.self_processing_mem
                    if 680 <= x <= 705:
                        for machine in self.machines:
                            if machine.type == "B":
                                machine.self_processing_mem = not machine.self_processing_mem
                    if 930 <= x <= 955:
                        for machine in self.machines:
                            if machine.type == "C":
                                machine.self_processing_mem = not machine.self_processing_mem
                # switching filler list positions
                if 225 <= x <= 250 and self.setting_page == 2:
                    if 60 <= y <= 85 or 110 <= y <= 135:
                        temp = self.fillers[1]
                        self.fillers[1] = self.fillers[0]
                        self.fillers[0] = temp
                        self.filler_update = True
                    if 140 <= y <= 165 or 190 <= y <= 215:
                        temp = self.fillers[1]
                        self.fillers[1] = self.fillers[2]
                        self.fillers[2] = temp
                        self.filler_update = True
                # switching filler list quantities
                row = (60, 140, 220)
                for i in range(3):
                    if row[i] <= y <= row[i]+25 and self.setting_page == 2:
                        if 10 <= x <= 35:
                            self.fillers[i].amount -= 10
                            if self.fillers[i].amount < 0:
                                self.fillers[i].amount = 0
                            self.filler_update = True
                        if 50 <= x <= 75:
                            self.fillers[i].amount -= 1
                            if self.fillers[i].amount < 0:
                                self.fillers[i].amount = 0
                            self.filler_update = True
                        if 90 <= x <= 115:
                            self.fillers[i].amount += 1
                            if self.fillers[i].amount > 999:
                                self.fillers[i].amount = 999
                            self.filler_update = True
                        if 130 <= x <= 155:
                            self.fillers[i].amount += 10
                            if self.fillers[i].amount > 999:
                                self.fillers[i].amount = 999
                            self.filler_update = True
                        if 170 <= x <= 195:
                            self.fillers[i].is_inf = not self.fillers[i].is_inf
                            self.filler_update = True
            # check for releasing mouse button
            # if event.type == pg.MOUSEBUTTONUP:  # no need of use
        # realization of prepared actions
        if updated_broken_bottle_chance:
            if self.broken_bottle_chance > 100:
                self.broken_bottle_chance = 100
            if self.broken_bottle_chance < 0:
                self.broken_bottle_chance = 0
            self.texts[0][1] = self.render_text("current chance: " + str(self.broken_bottle_chance) + "%", 20, WHITE)
        if updated_max_fps:
            if self.max_fps > 800:
                self.max_fps = 800
            if self.max_fps < 30:
                self.max_fps = 30
            self.texts[3][1] = self.render_text("max " + str(self.max_fps) + " FPS", 20, WHITE)
        if updated_self_processing:
            self.self_processing_on = not self.self_processing_on
        if updated_manual_mode:
            self.manual_mode_on = not self.manual_mode_on
            if self.manual_mode_on:
                self.production_line_run = False
        if updated_random_space:
            self.random_space_on = not self.random_space_on

    def update(self):
        # Check PLC connection first
        if not self.plc_read_thread.connected:
            # Stop the simulation if not connected to PLC
            if self.start_simulation:
                self.start_simulation = False
                print("Simulation stopped: PLC connection required")
            return
            
        # Simulation loop update
        self.all_sprites.update()
        # spawning next bottles
        if self.random_space_on:
            # spawning next bottles in random distances
            if self.last_bottle.rect.x >= self.next_space:
                next_position = self.last_bottle.rect.x - (88 + self.next_space)
                # making sure the bottle spawn off-screen
                if next_position > -88:
                    next_position = -88
                self.last_bottle = Bottle(self, next_position, 320)
                self.next_space = randrange(self.min_space, self.max_space)
        else:
            # spawning next bottles in equal distances
            if self.last_bottle.rect.x >= 150:
                self.last_bottle = Bottle(self, self.last_bottle.rect.x - 250, 320)
        # update control_panel
        self.is_error = False
        for machine in self.machines:
            if machine.operation_error:
                self.is_error = True
        if self.is_error:
            self.is_start = False
        if self.is_start:
            self.control_panel_G.is_on = True
        else:
            self.control_panel_G.is_on = False
        if self.is_error:
            self.control_panel_R.is_on = True
        else:
            self.control_panel_R.is_on = False

    def filler(self):
        # Check PLC connection first
        if not self.plc_read_thread.connected:
            return
            
        # Liquid queue processing
        if self.filler_update:
            # choosing active filler
            if self.fillers[0].amount > 0 or self.fillers[0].is_inf:
                self.filler_index = 0
            elif self.fillers[1].amount > 0 or self.fillers[1].is_inf:
                self.filler_index = 1
            elif self.fillers[2].amount > 0 or self.fillers[2].is_inf:
                self.filler_index = 2
            else:
                self.filler_index = 3
            # setting active filler parameters
            if self.filler_index < 3:
                self.filler_color = self.fillers[self.filler_index].color
                self.filler_transparency = self.fillers[self.filler_index].transparency
            else:
                self.filler_transparency = 0

            # re-render filler list elements
            for i in range(3):
                self.texts[2][i] = self.render_text(self.fillers[i].name, 20, WHITE)
                if self.fillers[i].is_inf:
                    self.texts[2][i + 3] = self.render_text("inf", 20, WHITE)
                else:
                    self.texts[2][i + 3] = self.render_text(str(self.fillers[i].amount), 20, WHITE)

            self.filler_update = False

    def manual_mode(self):
        # Check PLC connection first
        if not self.plc_read_thread.connected:
            # Stop the manual mode if not connected to PLC
            if self.manual_mode_on:
                self.manual_mode_on = False
                print("Manual mode disabled: PLC connection required")
            return
            
        # update machine sensor lights state...
        # ...for machine A
        if self.machine_A_LR[0] and self.machine_A_LR[1]:
            self.machine_A_ROG = [False, False, True]
        elif self.machine_A_LR[0] or self.machine_A_LR[1]:
            self.machine_A_ROG = [False, True, False]
        else:
            self.machine_A_ROG = [True, False, False]
        # ...for machine B
        if self.machine_B_LR[0] and self.machine_B_LR[1]:
            self.machine_B_ROG = [False, False, True]
        elif self.machine_B_LR[0] or self.machine_B_LR[1]:
            self.machine_B_ROG = [False, True, False]
        else:
            self.machine_B_ROG = [True, False, False]
        # ...for machine C
        if self.machine_C_LR[0] and self.machine_C_LR[1]:
            self.machine_C_ROG = [False, False, True]
        elif self.machine_C_LR[0] or self.machine_C_LR[1]:
            self.machine_C_ROG = [False, True, False]
        else:
            self.machine_C_ROG = [True, False, False]

    def self_processing(self):
        # Check PLC connection first
        if not self.plc_read_thread.connected:
            # Stop self-processing if not connected to PLC
            if self.self_processing_on:
                self.self_processing_on = False
                print("Self-processing disabled: PLC connection required")
            return
            
        # Simulation self processing loop update
        # starting production line after all operations complete
        if not self.machine_A_top_ROG[1] and not self.machine_B_top_ROG[1] and not self.machine_C_top_ROG[1]:
            self.sp_during_operation = False
        if not self.sp_during_operation:
            self.production_line_run = True

        # update machine sensor lights state...
        # ...for machine A
        if self.machine_A_LR[0] and self.machine_A_LR[1]:
            if self.machine_A_operation_in[5]:
                self.machine_A_operation_in[5] = False
            self.machine_A_ROG = [False, False, True]
            if self.sp_openA:
                self.production_line_run = False
                self.sp_during_operation = True
                self.sp_openA = False
                self.sp_A_ok = False
                self.machine_A_operation_in[5] = True
                self.machine_A_top_ROG[1] = True
                self.machine_A_top_ROG[2] = False
        elif self.machine_A_LR[0] or self.machine_A_LR[1]:
            self.machine_A_ROG = [False, True, False]
        else:
            self.machine_A_ROG = [True, False, False]
        # ...for machine B
        if self.machine_B_LR[0] and self.machine_B_LR[1]:
            if self.machine_B_operation_in[5]:
                self.machine_B_operation_in[5] = False
            self.machine_B_ROG = [False, False, True]
            if self.sp_openB:
                if self.sp_A_to_B != '':
                    if self.sp_A_to_B[0] == '1':
                        self.production_line_run = False
                        self.sp_during_operation = True
                        self.sp_openB = False
                        self.sp_B_ok = False
                        self.machine_B_operation_in[5] = True
                        self.machine_B_top_ROG[1] = True
                        self.machine_B_top_ROG[2] = False
        elif self.machine_B_LR[0] or self.machine_B_LR[1]:
            self.machine_B_ROG = [False, True, False]
        else:
            self.machine_B_ROG = [True, False, False]
        # ...for machine C
        if self.machine_C_LR[0] and self.machine_C_LR[1]:
            if self.machine_C_operation_in[5]:
                self.machine_C_operation_in[5] = False
            self.machine_C_ROG = [False, False, True]
            if self.sp_openC:
                if self.sp_B_to_C != '':
                    if self.sp_B_to_C[0] == '1':
                        self.production_line_run = False
                        self.sp_during_operation = True
                        self.sp_openC = False
                        self.sp_C_ok = False
                        self.machine_C_operation_in[5] = True
                        self.machine_C_top_ROG[1] = True
                        self.machine_C_top_ROG[2] = False
        elif self.machine_C_LR[0] or self.machine_C_LR[1]:
            self.machine_C_ROG = [False, True, False]
        else:
            self.machine_C_ROG = [True, False, False]
        # bottle left operation...
        # ...on machine A
        if self.sp_last_A_LR[1] and not self.machine_A_LR[1]:
            if not self.sp_openA:
                if self.sp_A_ok:
                    self.sp_A_to_B += '1'
                else:
                    self.sp_A_to_B += '0'
                self.sp_openA = True
        # ...on machine B
        if not self.machine_B_LR[1] and self.sp_last_B_LR[1]:
            self.sp_A_to_B = self.sp_A_to_B[1:]
            if not self.sp_openB:
                if self.sp_B_ok:
                    self.sp_B_to_C += '1'
                else:
                    self.sp_B_to_C += '0'
                self.sp_openB = True
            else:
                self.sp_B_to_C += '0'
        # ...on machine C
        if not self.machine_C_LR[1] and self.sp_last_C_LR[1]:
            self.sp_B_to_C = self.sp_B_to_C[1:]
            if not self.sp_openC:
                self.sp_openC = True

        # cycle A
        if not self.sp_openA:
            if self.machine_A_operation_out[3]: # If machine A is in operation 
                self.sp_A_ok = True
            if self.machine_A_operation_out[4]: # If machine A is not in operation
                self.sp_A_ok = False
            if self.machine_A_operation_out[1]: # If machine A is in position
                self.sp_A_end_pos = True 
            if self.machine_A_operation_out[0] and self.sp_A_end_pos: # If machine A is in position and the operation is complete
                self.machine_A_top_ROG[1] = False # Turn off the orange light
                if self.sp_A_ok: # If machine A is ok
                    self.machine_A_top_ROG[0] = False # Turn off the red light
                    self.machine_A_top_ROG[2] = True # Turn on the green light
                else:
                    self.machine_A_top_ROG[0] = True # Turn on the red light 
                    self.machine_A_top_ROG[2] = False # Turn off the green light
                self.sp_A_end_pos = False
        # cycle B
        if not self.sp_openB:
            if self.machine_B_operation_out[3]:
                self.sp_B_ok = True
            if self.machine_B_operation_out[4]:
                self.sp_B_ok = False
            if self.machine_B_operation_out[1]:
                self.sp_B_end_pos = True
            if self.machine_B_operation_out[0] and self.sp_B_end_pos:
                self.machine_B_top_ROG[1] = False
                if self.sp_B_ok:
                    self.machine_B_top_ROG[0] = False
                    self.machine_B_top_ROG[2] = True
                else:
                    self.machine_B_top_ROG[0] = True
                    self.machine_B_top_ROG[2] = False
                self.sp_B_end_pos = False
        # cycle C
        if not self.sp_openC:
            if self.machine_C_operation_out[3]:
                self.sp_C_ok = True
            if self.machine_C_operation_out[4]:
                self.sp_C_ok = False
            if self.machine_C_operation_out[1]:
                self.sp_C_end_pos = True
            if self.machine_C_operation_out[0] and self.sp_C_end_pos:
                self.machine_C_top_ROG[1] = False
                if self.sp_C_ok:
                    self.machine_C_top_ROG[0] = False
                    self.machine_C_top_ROG[2] = True
                else:
                    self.machine_C_top_ROG[0] = True
                    self.machine_C_top_ROG[2] = False
                self.sp_C_end_pos = False

        # machines LR sensor edge detection variables
        self.sp_last_A_LR[0] = self.machine_A_LR[0]
        self.sp_last_A_LR[1] = self.machine_A_LR[1]
        self.sp_last_B_LR[0] = self.machine_B_LR[0]
        self.sp_last_B_LR[1] = self.machine_B_LR[1]
        self.sp_last_C_LR[0] = self.machine_C_LR[0]
        self.sp_last_C_LR[1] = self.machine_C_LR[1]

    def plc_processing(self):
        # Check PLC connection first
        if not self.plc_read_thread.connected:
            # Stop the simulation if not connected to PLC
            if self.start_simulation:
                self.start_simulation = False
                print("Simulation stopped: PLC connection required")
            return
            
        # data access control
        if not self.io_lock:
            self.io_lock = True

            # update simulation inputs // PLC outputs
            self.production_line_run = self.inputs[0]
            self.machine_A_ROG = self.inputs[1:4]
            self.machine_B_ROG = self.inputs[4:7]
            self.machine_C_ROG = self.inputs[7:10]
            self.machine_A_top_ROG = self.inputs[10:13]
            self.machine_B_top_ROG = self.inputs[13:16]
            self.machine_C_top_ROG = self.inputs[16:19]
            self.machine_A_operation_in = self.inputs[19:25]
            self.machine_B_operation_in = self.inputs[25:31]
            self.machine_C_operation_in = self.inputs[31:37]

            # update simulation outputs // PLC inputs
            self.outputs = [self.machine_A_LR[0], self.machine_A_LR[1],
                            self.machine_B_LR[0], self.machine_B_LR[1],
                            self.machine_C_LR[0], self.machine_C_LR[1],
                            self.machine_A_operation_out[0], self.machine_A_operation_out[1],
                            self.machine_A_operation_out[2], self.machine_A_operation_out[3],
                            self.machine_A_operation_out[4],
                            self.machine_B_operation_out[0], self.machine_B_operation_out[1],
                            self.machine_B_operation_out[2], self.machine_B_operation_out[3],
                            self.machine_B_operation_out[4],
                            self.machine_C_operation_out[0], self.machine_C_operation_out[1],
                            self.machine_C_operation_out[2], self.machine_C_operation_out[3],
                            self.machine_C_operation_out[4], False, False, False]

            self.io_lock = False

    def draw(self):
        # Simulation drawing loop
        # drawing background
        self.screen.blit(self.background, (0, 0))
        
        # Check if PLC is connected and show appropriate message if not
        if not self.plc_read_thread.connected:
            self.screen.fill(DARK_GRAY)
            disconnected_text = self.render_text("PLC Connection Required", 30, WHITE)
            self.screen.blit(disconnected_text, (WIDTH//2 - disconnected_text.get_width()//2, HEIGHT//2 - 50))
            instructions_text = self.render_text("This simulator only works when connected to a PLC.", 20, WHITE)
            self.screen.blit(instructions_text, (WIDTH//2 - instructions_text.get_width()//2, HEIGHT//2))
            address_text = self.render_text(f"Configured PLC address: {self.plc_address}", 20, WHITE)
            self.screen.blit(address_text, (WIDTH//2 - address_text.get_width()//2, HEIGHT//2 + 30))
            settings_text = self.render_text("Check settings.ini to configure PLC connection parameters.", 18, WHITE)
            self.screen.blit(settings_text, (WIDTH//2 - settings_text.get_width()//2, HEIGHT//2 + 60))
            pg.display.flip()
            return
            
        # self.all_sprites.draw(self.screen)  # not in use as the sprites update queue is specified
        # draw sprites under bottle liquid
        self.machines_sensor.draw(self.screen)
        self.production_lines.draw(self.screen)
        # draw control panel
        self.screen.blit(self.control_panel, (0, 550))
        # no need to draw lasers as they are included in machine_sensor image
        # self.lasers.draw(self.screen)
        # draw bottle liquid
        for bottle in self.bottles:
            if not bottle.broken and bottle.filled > 0:
                s = pg.Surface((86, bottle.filled))
                s.set_alpha(255 * bottle.filler_transparency)
                s.fill(bottle.filler_color)
                self.screen.blit(s, (bottle.rect.x + 1, bottle.rect.y + 55 + 130 - bottle.filled))
        # draw sprites above bottle liquid
        self.bottles.draw(self.screen)
        self.machines.draw(self.screen)
        self.machines_top.draw(self.screen)
        for i in range(3):
            pg.draw.rect(self.screen, WHITE, (430 + i * 250, 50, 25, 25))
            self.screen.blit(self.texts[4][4], (430 + i * 250, 30))  # 'S.P.'
        if self.self_processing_on or self.manual_mode_on:
            for i in range(3):
                self.screen.blit(self.checked_locked, (430 + i * 250, 50))
        else:
            for machine in self.machines:
                if machine.type == "A" and machine.self_processing_on:
                    self.screen.blit(self.checked, (430, 50))
                if machine.type == "B" and machine.self_processing_on:
                    self.screen.blit(self.checked, (680, 50))
                if machine.type == "C" and machine.self_processing_on:
                    self.screen.blit(self.checked, (930, 50))

        # draw simulator settings depend on selected page
        # pg.draw.rect(self.screen, DARK_GRAY, (0, 25, 1000, 1))

        # simulator setting
        if self.setting_page == 0:
            pg.draw.rect(self.screen, DARK_GRAY, (0, 0, 73, 25))
            # broken bottle chance
            self.screen.blit(self.texts[0][0], (10, 30))  # 'Broken bottle chance:'
            pg.draw.rect(self.screen, WHITE, (20, 70, 200, 1))
            pg.draw.circle(self.screen, WHITE, (20 + (self.broken_bottle_chance * 2), 70), 10)
            self.screen.blit(self.texts[0][1], (20, 90))  # 'current chance: <value>%'
            # start simulation
            self.screen.blit(self.texts[0][2], (10, 130))  # 'Start simulation:'
            pg.draw.rect(self.screen, WHITE, (160, 130, 25, 25))
            if self.start_simulation:
                self.screen.blit(self.checked, (160, 130))
            # self processing
            self.screen.blit(self.texts[0][3], (10, 170))  # 'Self processing:'
            pg.draw.rect(self.screen, WHITE, (160, 170, 25, 25))
            if self.self_processing_on:
                if self.manual_mode_on or not self.start_simulation:
                    self.screen.blit(self.checked_inactive, (160, 170))
                else:
                    self.screen.blit(self.checked, (160, 170))
            # manual mode
            self.screen.blit(self.texts[0][4], (10, 210))  # 'Manual mode:'
            pg.draw.rect(self.screen, WHITE, (160, 210, 25, 25))
            if self.manual_mode_on:
                if self.start_simulation:
                    self.screen.blit(self.checked, (160, 210))
                else:
                    self.screen.blit(self.checked_inactive, (160, 210))
            # randomize distances
            self.screen.blit(self.texts[0][5], (10, 250))  # 'Random space:'
            pg.draw.rect(self.screen, WHITE, (160, 250, 25, 25))
            if self.random_space_on:
                self.screen.blit(self.checked, (160, 250))
        # PLC setting
        elif self.setting_page == 1:
            pg.draw.rect(self.screen, DARK_GRAY, (73, 0, 39, 25))
            self.screen.blit(self.texts[1][0], (10, 30))  # 'PLC info:'
            self.screen.blit(self.texts[1][1], (20, 60))  # 'PLC connected:...'
            self.screen.blit(self.texts[1][2], (20, 80))  # 'PLC name:...'
            self.screen.blit(self.texts[1][3], (20, 100))  # 'PLC type:...'
            self.screen.blit(self.texts[1][4], (20, 120))  # 'CPU state:...'
            self.screen.blit(self.texts[1][5], (20, 140))  # 'Dow/Up rate:...'
        # liquid setting
        elif self.setting_page == 2:
            pg.draw.rect(self.screen, DARK_GRAY, (112, 0, 111, 25))
            for i in range(3):
                self.screen.blit(self.texts[2][0+i], (10, 30+(i*80)))
                self.screen.blit(self.texts[2][3+i], (170, 30+(i*80)))
                for j in range(5):
                    self.screen.blit(self.filler_buttons[j], (10+(j*40), 60+(i*80)))
                # move down button
                if i != 2:
                    self.screen.blit(self.filler_buttons[j+1], (225, 60 + (i * 80)))
                # move up button
                if i != 0:
                    self.screen.blit(self.filler_buttons[j+2], (225, 30 + (i * 80)))
            # drawing lines between list elements
            pg.draw.rect(self.screen, DARK_GRAY, (10, 100, 240, 1))
            pg.draw.rect(self.screen, DARK_GRAY, (10, 180, 240, 1))
        # time setting
        else:
            pg.draw.rect(self.screen, DARK_GRAY, (223, 0, 43, 25))
            # fps
            self.screen.blit(self.texts[3][0], (10, 30))  # 'FPS limit:'
            pg.draw.rect(self.screen, WHITE, (20, 70, 200, 1))
            pg.draw.circle(self.screen, WHITE, (20 + (self.max_fps / 4), 70), 10)
            self.screen.blit(self.texts[3][1], (20, 90))  # 'max <value> FPS'
            # unlimited FPS
            self.screen.blit(self.texts[3][2], (10, 130))  # 'Unlimited FPS:'
            pg.draw.rect(self.screen, WHITE, (160, 130, 25, 25))
            if self.unlimited_fps_on:
                if (self.auto_fps_on and self.plc_read_thread.connected) or self.manual_mode_on:
                    self.screen.blit(self.checked_inactive, (160, 130))
                else:
                    self.screen.blit(self.checked, (160, 130))
            # auto FPS
            self.screen.blit(self.texts[3][3], (10, 170))  # 'Auto FPS:'
            pg.draw.rect(self.screen, WHITE, (160, 170, 25, 25))
            if self.auto_fps_on:
                if self.plc_read_thread.connected and not self.manual_mode_on:
                    self.screen.blit(self.checked, (160, 170))
                else:
                    self.screen.blit(self.checked_inactive, (160, 170))
        # draw setting menu option texts
        self.screen.blit(self.texts[4][0], (5, 5))
        self.screen.blit(self.texts[4][1], (78, 5))
        self.screen.blit(self.texts[4][2], (117, 5))
        self.screen.blit(self.texts[4][3], (228, 5))
        # show help
        if self.show_help:
            self.screen.blit(self.help, (0, 0))
        # flip the display after drawing everything
        pg.display.flip()

    def render_text(self, text, size, color):
        # Additional helping function for rendering text
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        return text_surface

    def resource_path(self, relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


# Main
if __name__ == '__main__':
    print("="*80)
    print("BOTTLE FILLING MACHINE SIMULATOR")
    print("="*80)
    print("This simulator requires a PLC connection to operate.")
    print("Configuration will be loaded from simulator.ini")
    
    # Read PLC settings from ini file to show the user
    import configparser
    config = configparser.ConfigParser()
    try:
        config.read('simulator.ini')
        plc_address = config.get('plc', 'address')
        plc_rack = config.getint('plc', 'rack')
        plc_slot = config.getint('plc', 'slot')
        plc_port = config.getint('plc', 'port')
        print("\nPLC Connection Settings:")
        print(f"  Address: {plc_address}")
        print(f"  Rack: {plc_rack}")
        print(f"  Slot: {plc_slot}")
        print(f"  Port: {plc_port}")
        print("\nMake sure your PLC is powered on and accessible on the network.")
    except Exception as e:
        print("Error reading simulator.ini. Please ensure the file exists and has the correct format.")
        print(f"Error details: {str(e)}")
    
    print("="*80)
    
    g = Simulator()
    g.initial()

    print('sim_count: ' + str(g.sim_count))
    print('status_thread_count: ' + str(g.status_thread_count))
    print('status_operation_count: ' + str(g.status_operation_count))
    print('write_thread_count: ' + str(g.write_thread_count))
    print('write_operation_count: ' + str(g.write_operation_count))
    print('read_thread_count: ' + str(g.read_thread_count))
    print('read_operation_count: ' + str(g.read_operation_count))
    
    print("\nSimulation ended. PLC connection is required to run the simulator.")
    pg.quit()
