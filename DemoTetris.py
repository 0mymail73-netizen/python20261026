import random
import tkinter as tk


CELL_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CANVAS_WIDTH = CELL_SIZE * BOARD_WIDTH
CANVAS_HEIGHT = CELL_SIZE * BOARD_HEIGHT

SHAPES = [
    ("I", ("....", "####", "....", "...."), "#37c8e8"),
    ("O", (".##.", ".##.", "....", "...."), "#f4d35e"),
    ("T", (".#..", "###.", "....", "...."), "#a879e8"),
    ("S", (".##.", "##..", "....", "...."), "#52c78b"),
    ("Z", ("##..", ".##.", "....", "...."), "#f06464"),
    ("J", ("#...", "###.", "....", "...."), "#5685e8"),
    ("L", ("..#.", "###.", "....", "...."), "#f29b4b"),
]
MASCOTS = ("germ", "drop")


def rotate_clockwise(matrix):
    return tuple("".join(row[column] for row in matrix[::-1]) for column in range(len(matrix[0])))


class TetrisGame:
    def __init__(self, root):
        self.root = root
        self.root.title("테트리스")
        self.root.resizable(False, False)
        self.root.configure(bg="#18202b")

        main = tk.Frame(root, bg="#18202b", padx=18, pady=18)
        main.pack()

        self.board_canvas = tk.Canvas(
            main,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="#10161e",
            highlightthickness=1,
            highlightbackground="#394655",
        )
        self.board_canvas.pack(side=tk.LEFT)

        sidebar = tk.Frame(main, bg="#18202b", width=150, padx=18)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="테트리스",
            font=("Segoe UI", 20, "bold"),
            fg="#f2f5f8",
            bg="#18202b",
        ).pack(anchor="w", pady=(2, 18))

        self.score_var = tk.StringVar()
        self.lines_var = tk.StringVar()
        self.level_var = tk.StringVar()
        for label, variable in (("점수", self.score_var), ("줄", self.lines_var), ("단계", self.level_var)):
            tk.Label(sidebar, text=label, font=("Segoe UI", 9, "bold"), fg="#91a0af", bg="#18202b").pack(anchor="w")
            tk.Label(sidebar, textvariable=variable, font=("Segoe UI", 16, "bold"), fg="#f2f5f8", bg="#18202b").pack(anchor="w", pady=(0, 12))

        tk.Label(sidebar, text="다음 블록", font=("Segoe UI", 9, "bold"), fg="#91a0af", bg="#18202b").pack(anchor="w", pady=(2, 8))
        self.next_canvas = tk.Canvas(sidebar, width=120, height=100, bg="#10161e", highlightthickness=1, highlightbackground="#394655")
        self.next_canvas.pack(anchor="w", pady=(0, 18))

        controls = "←  왼쪽 이동\n→  오른쪽 이동\n↓  빠르게 내리기\n↑  회전\nSpace  즉시 내리기\nP  일시정지   R  다시 시작"
        tk.Label(sidebar, text=controls, justify=tk.LEFT, font=("Segoe UI", 9), fg="#c0cad4", bg="#18202b").pack(anchor="w", pady=4)

        self.root.bind("<Key>", self.handle_key)
        self.root.focus_set()
        self.timer_id = None
        self.restart()

    def restart(self):
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.paused = False
        self.game_over = False
        self.next_piece = random.choice(SHAPES)
        self.next_mascot = random.choice(MASCOTS)
        self.spawn_piece()
        self.draw()
        self.schedule_tick()

    def spawn_piece(self):
        name, matrix, color = self.next_piece
        self.current = {
            "name": name,
            "matrix": matrix,
            "color": color,
            "mascot": self.next_mascot,
            "x": 3,
            "y": 0,
        }
        self.next_piece = random.choice(SHAPES)
        self.next_mascot = random.choice(MASCOTS)
        if not self.is_valid(self.current["matrix"], self.current["x"], self.current["y"]):
            self.game_over = True

    def is_valid(self, matrix, x, y):
        for row_index, row in enumerate(matrix):
            for column_index, cell in enumerate(row):
                if cell != "#":
                    continue
                board_x = x + column_index
                board_y = y + row_index
                if board_x < 0 or board_x >= BOARD_WIDTH or board_y >= BOARD_HEIGHT:
                    return False
                if board_y >= 0 and self.board[board_y][board_x] is not None:
                    return False
        return True

    def move(self, dx, dy):
        new_x = self.current["x"] + dx
        new_y = self.current["y"] + dy
        if self.is_valid(self.current["matrix"], new_x, new_y):
            self.current["x"] = new_x
            self.current["y"] = new_y
            return True
        return False

    def rotate(self):
        rotated = rotate_clockwise(self.current["matrix"])
        for offset in (0, -1, 1, -2, 2):
            if self.is_valid(rotated, self.current["x"] + offset, self.current["y"]):
                self.current["matrix"] = rotated
                self.current["x"] += offset
                return

    def drop(self):
        while self.move(0, 1):
            pass
        self.lock_piece()

    def lock_piece(self):
        for row_index, row in enumerate(self.current["matrix"]):
            for column_index, cell in enumerate(row):
                if cell == "#":
                    board_x = self.current["x"] + column_index
                    board_y = self.current["y"] + row_index
                    if board_y < 0:
                        self.game_over = True
                        return
                    self.board[board_y][board_x] = (self.current["color"], self.current["mascot"])

        remaining_rows = [row for row in self.board if any(cell is None for cell in row)]
        cleared = BOARD_HEIGHT - len(remaining_rows)
        if cleared:
            self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(cleared)] + remaining_rows
            self.lines += cleared
            self.score += (0, 100, 300, 500, 800)[cleared] * self.level
            self.level = self.lines // 10 + 1
        self.spawn_piece()

    def handle_key(self, event):
        key = event.keysym.lower()
        if key == "r":
            self.restart()
            return
        if key == "p" and not self.game_over:
            self.paused = not self.paused
            self.draw()
            return
        if self.paused or self.game_over:
            return

        if key == "left":
            self.move(-1, 0)
        elif key == "right":
            self.move(1, 0)
        elif key == "down":
            if self.move(0, 1):
                self.score += 1
            else:
                self.lock_piece()
        elif key == "up":
            self.rotate()
        elif key == "space":
            self.drop()
        else:
            return
        self.draw()

    def schedule_tick(self):
        delay = max(90, 550 - (self.level - 1) * 40)
        self.timer_id = self.root.after(delay, self.tick)

    def tick(self):
        self.timer_id = None
        if not self.paused and not self.game_over:
            if not self.move(0, 1):
                self.lock_piece()
            self.draw()
        self.schedule_tick()

    def draw_cell(self, canvas, x, y, color, size=CELL_SIZE, mascot=None):
        padding = 2
        left = x * size + padding
        top = y * size + padding
        canvas.create_rectangle(
            left,
            top,
            (x + 1) * size - padding,
            (y + 1) * size - padding,
            fill=color,
            outline="",
        )
        if mascot is not None:
            self.draw_mascot(canvas, left, top, size - padding * 2, mascot)

    def draw_mascot(self, canvas, left, top, size, mascot):
        center_x = left + size / 2
        center_y = top + size / 2
        stroke = max(1, size // 12)

        if mascot == "germ":
            for dx, dy in ((-0.35, -0.95), (0.35, -0.95), (0.95, -0.35), (0.95, 0.35),
                           (0.35, 0.95), (-0.35, 0.95), (-0.95, 0.35), (-0.95, -0.35)):
                canvas.create_line(
                    center_x + dx * size * 0.24,
                    center_y + dy * size * 0.24,
                    center_x + dx * size * 0.38,
                    center_y + dy * size * 0.38,
                    fill="#315b35",
                    width=stroke,
                )
            canvas.create_oval(
                center_x - size * 0.29,
                center_y - size * 0.29,
                center_x + size * 0.29,
                center_y + size * 0.29,
                fill="#a8e879",
                outline="#315b35",
                width=stroke,
            )
        else:
            canvas.create_polygon(
                center_x,
                top + size * 0.08,
                left + size * 0.84,
                top + size * 0.54,
                center_x + size * 0.26,
                top + size * 0.86,
                center_x,
                top + size * 0.94,
                center_x - size * 0.26,
                top + size * 0.86,
                left + size * 0.16,
                top + size * 0.54,
                fill="#a8e9f2",
                outline="#286777",
                width=stroke,
            )

        eye_y = center_y - size * 0.04
        eye_radius = max(1, size * 0.055)
        for eye_x in (center_x - size * 0.11, center_x + size * 0.11):
            canvas.create_oval(
                eye_x - eye_radius,
                eye_y - eye_radius,
                eye_x + eye_radius,
                eye_y + eye_radius,
                fill="#18202b",
                outline="",
            )
        canvas.create_arc(
            center_x - size * 0.13,
            center_y - size * 0.02,
            center_x + size * 0.13,
            center_y + size * 0.19,
            start=200,
            extent=140,
            style=tk.ARC,
            outline="#315b35" if mascot == "germ" else "#286777",
            width=stroke,
        )

    def draw(self):
        self.board_canvas.delete("all")
        self.score_var.set(f"{self.score:06d}")
        self.lines_var.set(str(self.lines))
        self.level_var.set(str(self.level))

        for row_index, row in enumerate(self.board):
            for column_index, cell in enumerate(row):
                if cell is not None:
                    color, mascot = cell
                    self.draw_cell(self.board_canvas, column_index, row_index, color, mascot=mascot)

        for column in range(BOARD_WIDTH + 1):
            x = column * CELL_SIZE
            self.board_canvas.create_line(x, 0, x, CANVAS_HEIGHT, fill="#202a35")
        for row in range(BOARD_HEIGHT + 1):
            y = row * CELL_SIZE
            self.board_canvas.create_line(0, y, CANVAS_WIDTH, y, fill="#202a35")

        if not self.game_over:
            ghost_y = self.current["y"]
            while self.is_valid(self.current["matrix"], self.current["x"], ghost_y + 1):
                ghost_y += 1
            self.draw_piece(self.current, ghost_y, ghost=True)
            self.draw_piece(self.current)

        self.draw_next_piece()
        if self.paused or self.game_over:
            message = "일시정지" if self.paused else "게임 종료"
            self.board_canvas.create_rectangle(35, 250, CANVAS_WIDTH - 35, 340, fill="#10161e", outline="#647386")
            self.board_canvas.create_text(CANVAS_WIDTH // 2, 278, text=message, fill="#f2f5f8", font=("Segoe UI", 20, "bold"))
            if self.game_over:
                self.board_canvas.create_text(CANVAS_WIDTH // 2, 312, text="R 키를 눌러 다시 시작", fill="#c0cad4", font=("Segoe UI", 10))

    def draw_piece(self, piece, y=None, ghost=False):
        y = piece["y"] if y is None else y
        color = "#536170" if ghost else piece["color"]
        for row_index, row in enumerate(piece["matrix"]):
            for column_index, cell in enumerate(row):
                board_y = y + row_index
                if cell == "#" and board_y >= 0:
                    self.draw_cell(
                        self.board_canvas,
                        piece["x"] + column_index,
                        board_y,
                        color,
                        mascot=None if ghost else piece["mascot"],
                    )

    def draw_next_piece(self):
        self.next_canvas.delete("all")
        _, matrix, color = self.next_piece
        size = 22
        for row_index, row in enumerate(matrix):
            for column_index, cell in enumerate(row):
                if cell == "#":
                    left = 16 + column_index * size
                    top = 6 + row_index * size
                    self.next_canvas.create_rectangle(
                        left,
                        top,
                        left + size - 3,
                        top + size - 3,
                        fill=color,
                        outline="",
                    )
                    self.draw_mascot(self.next_canvas, left, top, size - 3, self.next_mascot)


if __name__ == "__main__":
    window = tk.Tk()
    TetrisGame(window)
    window.mainloop()