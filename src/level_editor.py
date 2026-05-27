import json

import pygame   
import os


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
CIRCLE_RADIUS = 50
SNAP_MS = 50 

BEATMAP_PATH = "levels/lvl_1.json"

class Level_editor:
    def __init__(self, beatmap):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Level Editor")

        self.clock = pygame.time.Clock()
        self.running = True

        self.beatmap = beatmap

        # time management
        self.editor_time = 0  # ms
        self.playing = False
        self.play_start_ticks = 0  # pygame.time.get_ticks() when started
        self.play_start_time = 0   # editor_time when started
        self.drawing_slider = False
        self.slider_points = []
        self.slider_start_time = 0

        # load audio
        if os.path.exists(self.beatmap.audio):
            pygame.mixer.music.load(self.beatmap.audio)
        else:
            print("WARNING: audio file not found:", self.beatmap.audio)

    def start_playback(self):
        if not os.path.exists(self.beatmap.audio):
            return
        self.playing = True
        self.play_start_ticks = pygame.time.get_ticks()
        self.play_start_time = self.editor_time
        pygame.mixer.music.play(start=self.editor_time / 1000.0)

    def stop_playback(self):
        self.playing = False
        pygame.mixer.music.stop()

    def update_time(self):
        if self.playing:
            now = pygame.time.get_ticks()
            delta = now - self.play_start_ticks
            self.editor_time = self.play_start_time + delta

    def seek(self, delta_ms):
        # move editor_time by delta, clamp to >= 0
        self.editor_time = max(0, self.editor_time + delta_ms)
        if self.playing:
            # restart playback at new time
            self.start_playback()

    # ----- INPUT HANDLING -----

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                # Space: play/pause
                elif event.key == pygame.K_SPACE:
                    if self.playing:
                        self.stop_playback()
                    else:
                        self.start_playback()

                # Left/Right arrows: seek
                elif event.key == pygame.K_LEFT:
                    self.seek(-250)  # back 250ms
                elif event.key == pygame.K_RIGHT:
                    self.seek(250)   # forward 250ms


                # S: save
                elif event.key == pygame.K_s:
                    save_beatmap(self.beatmap, BEATMAP_PATH)
                    print("Saved beatmap to", BEATMAP_PATH)


            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and event.pos[1] < WINDOW_HEIGHT - 40:  # left click: place circle
                    pos = event.pos
                    snapped_time = self.snap_time(self.editor_time)
                    obj = HitObject("circle", snapped_time, pos)
                    self.beatmap.add_object(obj)
                    print(f"Placed circle at t={snapped_time}ms, pos={pos}")
                if event.button == 2:  # middle click: remove nearest object
                    print("Removing object near", event.pos)
                    pos = event.pos
                    nearest = None
                    nearest_dist = 9999
                    for obj in self.beatmap.objects:
                        dist = ((obj.pos[0] - pos[0]) ** 2 + (obj.pos[1] - pos[1]) ** 2) ** 0.5
                        if dist < nearest_dist and dist < CIRCLE_RADIUS:
                            nearest = obj
                            nearest_dist = dist
                    if nearest:
                        self.beatmap.objects.remove(nearest)
                        print(f"Removed object at t={nearest.time}ms, pos={nearest.pos}")

                if event.button == 3 and event.pos[1] < WINDOW_HEIGHT - 40:  
                    print("Starting slider at", event.pos)
                    self.drawing_slider = True
                    self.slider_start_time = self.snap_time(self.editor_time)
                    self.slider_start_ticks = pygame.time.get_ticks()
                    self.slider_points = [event.pos]


                if event.button == 4:  # scroll up: seek forward
                    self.seek(50)
                elif event.button == 5:  # scroll down: seek backward
                    self.seek(-50)

            elif event.type == pygame.MOUSEBUTTONUP:
                # Finish slider
                if event.button == 3 and self.drawing_slider:
                    self.drawing_slider = False
                    self.slider_points.append(event.pos)
                    print("Finished slider at", event.pos)
                    if len(self.slider_points) > 1:
                        self.slider_end_time = pygame.time.get_ticks()
                        self.slider_duration = self.slider_end_time - self.slider_start_ticks
                        obj = HitObject("slider", self.slider_start_time, self.slider_points[0], self.slider_points[-1], self.slider_duration)
                        self.beatmap.add_object(obj)

    def snap_time(self, t):
        if SNAP_MS <= 0:
            return int(t)
        return int(round(t / SNAP_MS) * SNAP_MS)

    # ----- RENDERING -----

    def draw(self):
        self.screen.fill((20, 20, 20))
        
        # draw all hitobjects
        for obj in self.beatmap.objects:
            if obj.time >= self.editor_time - 500 and obj.time <= self.editor_time + 500:
                
                if obj.type == "slider":
                    
                    color = (255, 100, 100)
                    pygame.draw.line(self.screen, color, obj.pos, obj.end_pos, 5)
                    pygame.draw.circle(self.screen, color, obj.pos, CIRCLE_RADIUS, 2)
                    self.screen.blit(pygame.font.SysFont("consolas", 12).render(f"start: {obj.time}ms", True, (255, 255, 255)), (obj.pos[0] + CIRCLE_RADIUS, obj.pos[1]))
                    pygame.draw.circle(self.screen, color, obj.end_pos, CIRCLE_RADIUS, 2)
                    self.screen.blit(pygame.font.SysFont("consolas", 12).render(f"end: {obj.time + obj.duration}ms", True, (255, 255, 255)), (obj.end_pos[0] + CIRCLE_RADIUS, obj.end_pos[1]))

                else:
                    color = (0, 150, 255)
                    pygame.draw.circle(self.screen, color, obj.pos, CIRCLE_RADIUS, 2)
                    self.screen.blit(pygame.font.SysFont("consolas", 12).render(f"{obj.time}ms", True, (255, 255, 255)), (obj.pos[0] + CIRCLE_RADIUS, obj.pos[1]))
                    

        # draw current time line at top
        font = pygame.font.SysFont("consolas", 18)
        text = font.render(f"time: {self.editor_time} ms", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        # draw play state
        state_text = "PLAYING" if self.playing else "PAUSED"
        text2 = font.render(state_text, True, (0, 255, 0) if self.playing else (255, 0, 0))
        self.screen.blit(text2, (10, 30))

        # simple timeline bar at bottom
        pygame.draw.rect(self.screen, (60, 60, 60), (0, WINDOW_HEIGHT - 40, WINDOW_WIDTH, 40))
        # we don't know song length here; just show a moving marker
        marker_x = (self.editor_time % 5000) / 5000 * WINDOW_WIDTH
        pygame.draw.line(self.screen, (255, 255, 0),
                         (marker_x, WINDOW_HEIGHT - 40),
                         (marker_x, WINDOW_HEIGHT))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update_time()
            self.draw()

        


class HitObject:
    def __init__(self, object_type, time_ms, pos, end_pos=None, duration=None):
        self.type = object_type
        self.time = time_ms
        self.pos = pos  # [x, y]
        self.end_pos = end_pos  # [x, y]
        self.duration = duration  # ms

    def to_dict(self):
        if self.type == "slider":
            return {
                "type": self.type,
                "time": self.time,
                "pos": self.pos,
                "end_pos": self.end_pos,
                "duration": self.duration
            }
        elif self.type == "circle":
            return {
                "type": self.type,
                "time": self.time,
                "pos": self.pos
            }

    @staticmethod
    def from_dict(d):
        if "end_pos" in d:
            return HitObject(d["type"], d["time"], d["pos"], d["end_pos"], d["duration"])
        return HitObject(d["type"], d["time"], d["pos"])




class Beatmap:
    def __init__(self, audio = None, offset=0):
        self.audio = audio
        self.offset = offset
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

        self.objects.sort(key=lambda o: o.time)

    def to_dict(self):
        return {
            "audio_file": self.audio,
            "offset": self.offset,
            "objects": [o.to_dict() for o in self.objects]
        }
    
    @staticmethod
    def from_dict(d):
        bm = Beatmap(d["audio_file"], d.get("offset", 0))
        for obj_data in d.get("objects", []):
            bm.objects.append(HitObject.from_dict(obj_data))
        bm.objects.sort(key=lambda o: o.time)
        return bm



def load_beatmap(path):
    if not os.path.exists(path):

        return Beatmap(audio="song.mp3", offset=0)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Beatmap.from_dict(data)


def save_beatmap(beatmap, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(beatmap.to_dict(), f, indent=2)