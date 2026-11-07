
import random
import tkinter as tk

# הגדרות כלליות 

CELL_SIZE = 20
GRID_WIDTH = 25
GRID_HEIGHT = 20
SNAKE_SPEED = 90

PONG_WIDTH = 500
PONG_HEIGHT = 400
PONG_SPEED = 16


#  משחק סנייק 

class SnakeFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller

        top_bar = tk.Frame(self, bg="black")
        top_bar.pack(fill="x", padx=10, pady=5)

        tk.Button(
            top_bar,
            text="Main menu",
            font=("Arial", 11),
            command=self.back_to_menu
        ).pack(side="left")

        self.canvas = tk.Canvas(
            self,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        self.active = False
        self.running = False
        self.after_id = None

    def cancel_loop(self):
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

    def start_game(self):
        self.cancel_loop()

        self.active = True
        self.running = True

        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0

        self.food = self.spawn_food()

        self.controller.bind("<KeyPress>", self.handle_key)
        self.controller.focus_set()

        self.canvas.delete("all")
        self.game_loop()

    def back_to_menu(self):
        self.active = False
        self.running = False
        self.cancel_loop()
        self.controller.show_menu()

    def spawn_food(self):
        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in self.snake
        ]

        return random.choice(available) if available else None

    def handle_key(self, event):
        if not self.active:
            return

        key = event.keysym

        if not self.running:
            if key.lower() in ("space", "r"):
                self.start_game()
            return

        opposites = {
            "Up": "Down",
            "Down": "Up",
            "Left": "Right",
            "Right": "Left"
        }

        if key in opposites:
            if key != opposites[self.direction]:
                self.next_direction = key

    def game_over(self, message="GAME OVER"):
        self.running = False
        self.after_id = None

        cx = GRID_WIDTH * CELL_SIZE // 2
        cy = GRID_HEIGHT * CELL_SIZE // 2

        self.canvas.create_text(
            cx,
            cy - 20,
            text=f"{message} | Score: {self.score}",
            fill="white",
            font=("Arial", 18, "bold")
        )

        self.canvas.create_text(
            cx,
            cy + 25,
            text="Press SPACE or R to play again",
            fill="#00FF00",
            font=("Arial", 12)
        )

    def game_loop(self):
        self.after_id = None

        if not self.active or not self.running:
            return

        self.direction = self.next_direction

        head_x, head_y = self.snake[0]

        moves = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }

        dx, dy = moves[self.direction]
        new_head = (head_x + dx, head_y + dy)

        # Проверка границ
        if (
            new_head[0] < 0 or
            new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or
            new_head[1] >= GRID_HEIGHT
        ):
            self.game_over()
            return

        eating = new_head == self.food

        # Хвост освобождает клетку, если еда не съедается
        body = self.snake if eating else self.snake[:-1]

        if new_head in body:
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if eating:
            self.score += 10
            self.food = self.spawn_food()

            if self.food is None:
                self.game_over("YOU WIN!")
                return
        else:
            self.snake.pop()

        self.render()

        self.after_id = self.after(
            SNAKE_SPEED,
            self.game_loop
        )

    def render(self):
        self.canvas.delete("all")

        if self.food is not None:
            fx, fy = self.food

            self.canvas.create_oval(
                fx * CELL_SIZE,
                fy * CELL_SIZE,
                (fx + 1) * CELL_SIZE,
                (fy + 1) * CELL_SIZE,
                fill="red",
                outline=""
            )

        for i, (sx, sy) in enumerate(self.snake):
            color = "#00FF00" if i == 0 else "#228B22"

            self.canvas.create_rectangle(
                sx * CELL_SIZE,
                sy * CELL_SIZE,
                (sx + 1) * CELL_SIZE,
                (sy + 1) * CELL_SIZE,
                fill=color,
                outline="black"
            )

        self.canvas.create_text(
            45,
            10,
            text=f"Score: {self.score}",
            fill="white",
            font=("Arial", 10),
            anchor="nw"
        )


#  משחק פונג 

class PongFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#111111")

        self.controller = controller

        top_bar = tk.Frame(self, bg="#111111")
        top_bar.pack(fill="x", padx=10, pady=5)

        tk.Button(
            top_bar,
            text="Main menu",
            font=("Arial", 11),
            command=self.back_to_menu
        ).pack(side="left")

        self.canvas = tk.Canvas(
            self,
            width=PONG_WIDTH,
            height=PONG_HEIGHT,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        self.active = False
        self.running = False
        self.after_id = None
        self.pressed_keys = set()

    def cancel_loop(self):
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

    def start_game(self):
        self.cancel_loop()

        self.active = True
        self.running = True
        self.score = 0
        self.pressed_keys.clear()

        # המטקה
        self.paddle_w = 90
        self.paddle_h = 14
        self.paddle_x = (PONG_WIDTH - self.paddle_w) / 2
        self.paddle_y = PONG_HEIGHT - 35
        self.paddle_speed = 7

        # הכדור
        self.ball_r = 8
        self.ball_x = PONG_WIDTH / 2
        self.ball_y = PONG_HEIGHT / 3

        self.ball_dx = random.choice([-3.5, 3.5])
        self.ball_dy = 3.5

        self.controller.bind(
            "<KeyPress>",
            self.handle_key_down
        )

        self.controller.bind(
            "<KeyRelease>",
            self.handle_key_up
        )

        self.controller.focus_set()

        self.game_loop()

    def back_to_menu(self):
        self.active = False
        self.running = False
        self.pressed_keys.clear()

        self.cancel_loop()
        self.controller.show_menu()

    def handle_key_down(self, event):
        if not self.active:
            return

        key = event.keysym

        if not self.running:
            if key.lower() in ("space", "r"):
                self.start_game()
            return

        self.pressed_keys.add(key.lower())

    def handle_key_up(self, event):
        self.pressed_keys.discard(event.keysym.lower())

    def game_over(self):
        self.running = False
        self.after_id = None

        cx = PONG_WIDTH // 2
        cy = PONG_HEIGHT // 2

        self.canvas.create_text(
            cx,
            cy - 20,
            text=f"GAME OVER! Score: {self.score}",
            fill="white",
            font=("Arial", 20, "bold")
        )

        self.canvas.create_text(
            cx,
            cy + 25,
            text="Press SPACE or R to play again",
            fill="#00E5FF",
            font=("Arial", 14)
        )

    def game_loop(self):
        self.after_id = None

        if not self.active or not self.running:
            return

        # תנועת המטקה
        if self.pressed_keys.intersection({"left", "a"}):
            self.paddle_x = max(
                0,
                self.paddle_x - self.paddle_speed
            )

        if self.pressed_keys.intersection({"right", "d"}):
            self.paddle_x = min(
                PONG_WIDTH - self.paddle_w,
                self.paddle_x + self.paddle_speed
            )

        # עדכון הכדור
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # קירות צד
        if self.ball_x - self.ball_r <= 0:
            self.ball_x = self.ball_r
            self.ball_dx = abs(self.ball_dx)

        elif self.ball_x + self.ball_r >= PONG_WIDTH:
            self.ball_x = PONG_WIDTH - self.ball_r
            self.ball_dx = -abs(self.ball_dx)

        # תקרה
        if self.ball_y - self.ball_r <= 0:
            self.ball_y = self.ball_r
            self.ball_dy = abs(self.ball_dy)

        # פגיעה במטקה
        if (
            self.ball_dy > 0 and
            self.ball_y + self.ball_r >= self.paddle_y and
            self.ball_y - self.ball_r <= self.paddle_y + self.paddle_h and
            self.ball_x + self.ball_r >= self.paddle_x and
            self.ball_x - self.ball_r <= self.paddle_x + self.paddle_w
        ):
            self.ball_y = self.paddle_y - self.ball_r
            self.ball_dy = -abs(self.ball_dy)

            hit_pos = (
                self.ball_x - (self.paddle_x + self.paddle_w / 2)
            ) / (self.paddle_w / 2)

            self.ball_dx = hit_pos * 5.0

            if abs(self.ball_dx) < 1.0:
                self.ball_dx = random.choice([-1.0, 1.0])

            # הגברת מהירות
            max_speed = 8.0
            self.ball_dx = max(-max_speed, min(max_speed, self.ball_dx * 1.03))
            self.ball_dy = max(-max_speed, min(max_speed, self.ball_dy * 1.03))

            self.score += 1

        # הכדור נפל
        if self.ball_y - self.ball_r > PONG_HEIGHT:
            self.game_over()
            return

        self.render()

        self.after_id = self.after(
            PONG_SPEED,
            self.game_loop
        )

    def render(self):
        self.canvas.delete("all")

        self.canvas.create_text(
            55,
            20,
            text=f"Score: {self.score}",
            fill="white",
            font=("Arial", 12)
        )

        self.canvas.create_oval(
            self.ball_x - self.ball_r,
            self.ball_y - self.ball_r,
            self.ball_x + self.ball_r,
            self.ball_y + self.ball_r,
            fill="white",
            outline=""
        )

        self.canvas.create_rectangle(
            self.paddle_x,
            self.paddle_y,
            self.paddle_x + self.paddle_w,
            self.paddle_y + self.paddle_h,
            fill="#00E5FF",
            outline=""
        )


#  מסך התפריט הראשי 

class MainMenu(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#20232A")

        self.controller = controller

        title = tk.Label(
            self,
            text="Python Arcade",
            font=("Arial", 22, "bold"),
            fg="#61DAFB",
            bg="#20232A"
        )
        title.pack(pady=40)

        btn_style = {
            "font": ("Arial", 14, "bold"),
            "width": 18,
            "pady": 8,
            "cursor": "hand2"
        }

        tk.Button(
            self,
            text="Snake",
            bg="#4CAF50",
            fg="white",
            command=lambda: controller.launch_game("Snake"),
            **btn_style
        ).pack(pady=12)

        tk.Button(
            self,
            text="Pong",
            bg="#2196F3",
            fg="white",
            command=lambda: controller.launch_game("Pong"),
            **btn_style
        ).pack(pady=12)

        tk.Button(
            self,
            text="Exit",
            bg="#F44336",
            fg="white",
            command=controller.destroy,
            **btn_style
        ).pack(pady=25)

        tk.Label(
            self,
            text="Made by Shon Pekarski",
            font=("Arial", 11, "bold"),
            bg="#20232A",
            fg="white"
        ).pack(pady=40)


#  מנהל האפליקציה הראשי 

class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Python Arcade")
        self.geometry("560x520")
        self.resizable(False, False)

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {
            "Menu": MainMenu(self.container, self),
            "Snake": SnakeFrame(self.container, self),
            "Pong": PongFrame(self.container, self)
        }

        for frame in self.frames.values():
            frame.place(
                relx=0,
                rely=0,
                relwidth=1,
                relheight=1
            )

        self.protocol("WM_DELETE_WINDOW", self.close_app)

        self.show_menu()

    def show_menu(self):
        # ביטול כל מקשי המשחק
        self.unbind("<Key>")
        self.unbind("<KeyPress>")
        self.unbind("<KeyRelease>")

        # ניקוי מצבי המשחק
        for name in ("Snake", "Pong"):
            frame = self.frames[name]
            frame.active = False
            frame.running = False
            frame.cancel_loop()

            if name == "Pong":
                frame.pressed_keys.clear()

        self.frames["Menu"].tkraise()

    def launch_game(self, game_name):
        game_frame = self.frames[game_name]

        game_frame.tkraise()
        game_frame.start_game()

    def close_app(self):
        for name in ("Snake", "Pong"):
            frame = self.frames[name]
            frame.active = False
            frame.running = False
            frame.cancel_loop()

        self.destroy()


# הפעלת האפליקציה 

if __name__ == "__main__":
    app = App()
    app.mainloop()
