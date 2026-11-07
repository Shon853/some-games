import random
import tkinter as tk

# ----------------- משחק סנייק -----------------
CELL_SIZE = 20
GRID_WIDTH = 25
GRID_HEIGHT = 20
SNAKE_SPEED = 90


class SnakeFrame(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent, bg="black")
    self.controller = controller

    # כפתור חזרה לתפריט
    top_bar = tk.Frame(self, bg="black")
    top_bar.pack(fill="x", padx=10, pady=5)
    btn_back = tk.Button(
        top_bar,
        text="Main menu",
        font=("Arial", 11),
        command=self.back_to_menu,
    )
    btn_back.pack(side="left")

    self.canvas = tk.Canvas(
        self,
        width=GRID_WIDTH * CELL_SIZE,
        height=GRID_HEIGHT * CELL_SIZE,
        bg="black",
        highlightthickness=0,
    )
    self.canvas.pack(pady=10)

    self.active = False
    self.after_id = None

  def start_game(self):
    self.active = True
    self.snake = [(5, 5), (4, 5), (3, 5)]
    self.direction = "Right"
    self.score = 0
    self.running = True
    self.food = self.spawn_food()

    # קשירת מקשים ייעודית למסך זה
    self.controller.bind("<Key>", self.handle_key)
    self.canvas.delete("all")
    self.game_loop()

  def back_to_menu(self):
    self.active = False
    if self.after_id:
      self.after_cancel(self.after_id)
    self.controller.show_menu()

  def spawn_food(self):
    while True:
      pos = (
          random.randint(0, GRID_WIDTH - 1),
          random.randint(0, GRID_HEIGHT - 1),
      )
      if pos not in self.snake:
        return pos

  def handle_key(self, event):
    if not self.active:
      return
    key = event.keysym
    if not self.running:
      if key in ("space", "r", "R"):
        self.start_game()
      return

    opposites = {
        "Up": "Down",
        "Down": "Up",
        "Left": "Right",
        "Right": "Left",
    }
    if key in opposites and key != opposites.get(self.direction):
      self.direction = key

  def game_loop(self):
    if not self.active or not self.running:
      return

    head_x, head_y = self.snake[0]
    moves = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}
    dx, dy = moves[self.direction]
    new_head = (head_x + dx, head_y + dy)

    if (
        new_head[0] < 0
        or new_head[0] >= GRID_WIDTH
        or new_head[1] < 0
        or new_head[1] >= GRID_HEIGHT
        or new_head in self.snake
    ):
      self.running = False
      cx, cy = GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2
      self.canvas.create_text(
          cx,
          cy - 20,
          text=f"GAME OVER! Score: {self.score}",
          fill="white",
          font=("Arial", 20, "bold"),
      )
      self.canvas.create_text(
          cx,
          cy + 25,
          text="press space or R to play again",
          fill="#00FF00",
          font=("Arial", 14),
      )
      return

    self.snake.insert(0, new_head)
    if new_head == self.food:
      self.score += 10
      self.food = self.spawn_food()
    else:
      self.snake.pop()

    self.canvas.delete("all")
    fx, fy = self.food
    self.canvas.create_oval(
        fx * CELL_SIZE,
        fy * CELL_SIZE,
        (fx + 1) * CELL_SIZE,
        (fy + 1) * CELL_SIZE,
        fill="red",
    )

    for i, (sx, sy) in enumerate(self.snake):
      color = "#00FF00" if i == 0 else "#228B22"
      self.canvas.create_rectangle(
          sx * CELL_SIZE,
          sy * CELL_SIZE,
          (sx + 1) * CELL_SIZE,
          (sy + 1) * CELL_SIZE,
          fill=color,
      )

    self.after_id = self.after(SNAKE_SPEED, self.game_loop)


# ----------------- משחק פונג (Pong) -----------------
PONG_WIDTH = 500
PONG_HEIGHT = 400


class PongFrame(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent, bg="#111111")
    self.controller = controller

    top_bar = tk.Frame(self, bg="#111111")
    top_bar.pack(fill="x", padx=10, pady=5)
    btn_back = tk.Button(
        top_bar,
        text="Main menu",
        font=("Arial", 11),
        command=self.back_to_menu,
    )
    btn_back.pack(side="left")

    self.canvas = tk.Canvas(
        self,
        width=PONG_WIDTH,
        height=PONG_HEIGHT,
        bg="black",
        highlightthickness=0,
    )
    self.canvas.pack(pady=10)

    self.active = False
    self.after_id = None
    self.pressed_keys = set()  # מעקב אחרי מקשים לחוצים בזמן אמת

  def start_game(self):
    self.active = True
    self.running = True
    self.score = 0
    self.pressed_keys.clear()

    # מאפייני המטקה
    self.paddle_w = 90
    self.paddle_h = 14
    self.paddle_x = (PONG_WIDTH - self.paddle_w) // 2
    self.paddle_y = PONG_HEIGHT - 35
    self.paddle_speed = 7.0  # מהירות תנועה חלקה לכל פריים

    # מאפייני הכדור
    self.ball_r = 8
    self.ball_x = PONG_WIDTH // 2
    self.ball_y = PONG_HEIGHT // 3
    self.ball_dx = 3.5
    self.ball_dy = 3.5

    # האזנה גם ללחיצה וגם לשחרור מקש
    self.controller.bind("<KeyPress>", self.handle_key_down)
    self.controller.bind("<KeyRelease>", self.handle_key_up)
    self.game_loop()

  def back_to_menu(self):
    self.active = False
    self.pressed_keys.clear()
    if self.after_id:
      self.after_cancel(self.after_id)
    self.controller.show_menu()

  def handle_key_down(self, event):
    if not self.active:
      return
    key = event.keysym
    if not self.running and key in ("space", "r", "R"):
      self.start_game()
      return
    self.pressed_keys.add(key)

  def handle_key_up(self, event):
    if event.keysym in self.pressed_keys:
      self.pressed_keys.remove(event.keysym)

  def game_loop(self):
    if not self.active or not self.running:
      return

    # תנועת מטקה חלקה בהתאם למקשים הלחוצים כרגע
    if (
        "Left" in self.pressed_keys
        or "a" in self.pressed_keys
        or "A" in self.pressed_keys
    ):
      self.paddle_x = max(0, self.paddle_x - self.paddle_speed)
    if (
        "Right" in self.pressed_keys
        or "d" in self.pressed_keys
        or "D" in self.pressed_keys
    ):
      self.paddle_x = min(
          PONG_WIDTH - self.paddle_w, self.paddle_x + self.paddle_speed
      )

    # עדכון מיקום הכדור
    self.ball_x += self.ball_dx
    self.ball_y += self.ball_dy

    # פגיעה בקירות צד
    if (
        self.ball_x - self.ball_r <= 0
        or self.ball_x + self.ball_r >= PONG_WIDTH
    ):
      self.ball_dx *= -1

    # פגיעה בתקרה
    if self.ball_y - self.ball_r <= 0:
      self.ball_dy *= -1

    # פגיעה במטקה
    if (
        self.paddle_y
        <= self.ball_y + self.ball_r
        <= self.paddle_y + self.paddle_h
    ):
      if self.paddle_x <= self.ball_x <= self.paddle_x + self.paddle_w:
        self.ball_dy = -abs(self.ball_dy)
        self.score += 1

        # חישוב זווית החזרה חכמה לפי נקודת הפגיעה במטקה
        hit_pos = (self.ball_x - (self.paddle_x + self.paddle_w / 2)) / (
            self.paddle_w / 2
        )
        self.ball_dx = hit_pos * 5.0

        # הגברת מהירות הדרגתית
        self.ball_dx *= 1.03
        self.ball_dy *= 1.03

    # נפילה לתחתית (Game Over)
    if self.ball_y > PONG_HEIGHT:
      self.running = False
      cx, cy = PONG_WIDTH // 2, PONG_HEIGHT // 2
      self.canvas.create_text(
          cx,
          cy - 20,
          text=f"GAME OVER! Score: {self.score}",
          fill="white",
          font=("Arial", 20, "bold"),
      )
      self.canvas.create_text(
          cx,
          cy + 25,
          text="press space or R to play again",
          fill="#00E5FF",
          font=("Arial", 14),
      )
      return

    # רינדור
    self.canvas.delete("all")
    self.canvas.create_text(
        40, 20, text=f"Score: {self.score}", fill="white", font=("Arial", 12)
    )
    self.canvas.create_oval(
        self.ball_x - self.ball_r,
        self.ball_y - self.ball_r,
        self.ball_x + self.ball_r,
        self.ball_y + self.ball_r,
        fill="white",
    )
    self.canvas.create_rectangle(
        self.paddle_x,
        self.paddle_y,
        self.paddle_x + self.paddle_w,
        self.paddle_y + self.paddle_h,
        fill="#00E5FF",
    )

    self.after_id = self.after(16, self.game_loop)  # ריצה בקצב ~60 FPS

# ----------------- מסך התפריט הראשי -----------------
class MainMenu(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent, bg="#20232A")
    self.controller = controller

    title = tk.Label(
        self,
        text="Python Arcade",
        font=("Arial", 22, "bold"),
        fg="#61DAFB",
        bg="#20232A",
    )
    title.pack(pady=40)

    btn_style = {
        "font": ("Arial", 14, "bold"),
        "width": 18,
        "pady": 8,
        "cursor": "hand2",
    }

    btn_snake = tk.Button(
        self,
        text="Snake",
        bg="#4CAF50",
        fg="white",
        command=lambda: controller.launch_game("Snake"),
        **btn_style,
    )
    btn_snake.pack(pady=12)

    btn_pong = tk.Button(
        self,
        text="pong",
        bg="#2196F3",
        fg="white",
        command=lambda: controller.launch_game("Pong"),
        **btn_style,
    )
    btn_pong.pack(pady=12)

    btn_exit = tk.Button(
        self,
        text="exit",
        bg="#F44336",
        fg="white",
        command=controller.destroy,
        **btn_style,
    )
    btn_exit.pack(pady=25)
    title = tk.Label(
        self,
        text="made by Shon Pekarski",
        font=("Arial", 11, "bold"),
        bg="#20232A",
        fg="white",
    )
    title.pack(pady=40)



# ----------------- מנהל האפליקציה הראשי -----------------
class App(tk.Tk):

  def __init__(self):
    super().__init__()
    self.title("Python Arcade")
    self.geometry("560x520")
    self.resizable(False, False)

    # מיכל ראשי לכל המסכים
    self.container = tk.Frame(self)
    self.container.pack(fill="both", expand=True)

    self.frames = {
        "Menu": MainMenu(self.container, self),
        "Snake": SnakeFrame(self.container, self),
        "Pong": PongFrame(self.container, self),
    }

    for frame in self.frames.values():
      frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    self.show_menu()

  def show_menu(self):
    self.unbind("<Key>")
    self.frames["Menu"].tkraise()

  def launch_game(self, game_name):
    game_frame = self.frames[game_name]
    game_frame.tkraise()
    game_frame.start_game()


if __name__ == "__main__":
  app = App()
  app.mainloop()