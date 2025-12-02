import tkinter as tk
from tkinter import messagebox
import random
import requests


class WordleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Game")
        self.root.configure(bg="#121213")
        self.root.resizable(False, False)

        # Colors
        self.bg_color = "#121213"
        self.tile_bg = "#3a3a3c"
        self.correct_color = "#538d4e"
        self.present_color = "#b59f3b"
        self.absent_color = "#3a3a3c"
        self.text_color = "#ffffff"
        self.key_bg = "#818384"

        # Game settings
        self.word_length = 5
        self.max_attempts = 6
        self.game_over = False

        # Load online word list
        self.words = self.load_online_word_bank()
        if not self.words:
            messagebox.showerror("Error", "Could not load word list.")
            self.root.destroy()
            return

        self.target_word = random.choice(self.words)

        # Answer debug print
        print("DEBUG (answer):", self.target_word)

        self.current_row = 0
        self.current_col = 0

        self.setup_ui()

    def load_online_word_bank(self):
        url = "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words"

        try:
            response = requests.get(url)
            response.raise_for_status()

            all_words = [w.strip().upper() for w in response.text.splitlines()]
            filtered = [w for w in all_words if len(w) == self.word_length]

            return filtered

        except Exception as e:
            print("Error loading online word list:", e)
            return []

    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(pady=10)

        title = tk.Label(title_frame, text="WORDLE",
                         font=("Helvetica", 36, "bold"),
                         fg=self.text_color, bg=self.bg_color)
        title.pack()

        subtitle = tk.Label(title_frame,
                            text=f"Guess the {self.word_length}-letter word in {self.max_attempts} tries",
                            font=("Helvetica", 12),
                            fg="#bbbbbb", bg=self.bg_color)
        subtitle.pack()

        # Board
        self.board_frame = tk.Frame(self.root, bg=self.bg_color)
        self.board_frame.pack(pady=10)

        self.tiles = []
        for row in range(self.max_attempts):
            row_tiles = []
            row_frame = tk.Frame(self.board_frame, bg=self.bg_color)
            row_frame.pack(pady=2)

            for col in range(self.word_length):
                tile = tk.Label(row_frame, text="", font=("Helvetica", 28, "bold"),
                                width=2, height=1, bg=self.tile_bg, fg=self.text_color,
                                relief="solid", borderwidth=2)
                tile.pack(side="left", padx=2)
                row_tiles.append(tile)

            self.tiles.append(row_tiles)

        # Keyboard
        self.keyboard_frame = tk.Frame(self.root, bg=self.bg_color)
        self.keyboard_frame.pack(pady=10)

        self.key_buttons = {}
        keyboard_layout = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '⌫']
        ]

        for row in keyboard_layout:
            row_frame = tk.Frame(self.keyboard_frame, bg=self.bg_color)
            row_frame.pack(pady=3)

            for key in row:
                width = 5 if key in ['ENTER', '⌫'] else 3
                btn = tk.Button(row_frame, text=key,
                                font=("Helvetica", 11, "bold"),
                                width=width, height=1,
                                bg=self.key_bg, fg=self.text_color,
                                relief="flat",
                                command=lambda k=key: self.key_press(k))
                btn.pack(side="left", padx=2)
                self.key_buttons[key] = btn

        # New game button
        new_game_btn = tk.Button(self.root, text="New Game",
                         font=("Helvetica", 12, "bold"),
                         bg=self.correct_color, fg=self.text_color,
                         relief="flat",
                         padx=20, pady=8,
                         command=self.new_game)
        new_game_btn.pack(pady=10)

        # Rules button
        rules_btn = tk.Button(self.root, text="Rules",
                      font=("Helvetica", 12, "bold"),
                      bg="#444444", fg=self.text_color,
                      relief="flat",
                      padx=20, pady=8,
                      command=self.show_rules)
        rules_btn.pack(pady=5)
        

        self.root.bind('<Key>', self.keyboard_input)

    def show_rules(self):
        rules_window = tk.Toplevel(self.root)
        rules_window.title("How to Play Wordle")
        rules_window.configure(bg="#121213")
        rules_window.resizable(False, False)

        tk.Label(
            rules_window,
            text="HOW TO PLAY",
            font=("Helvetica", 20, "bold"),
            fg="white",
            bg="#121213"
        ).pack(pady=10)

        rules_text = (
            "• You have 6 tries to guess the 5-letter word.\n\n"
            "• GREEN tile = Correct letter in the correct spot.\n\n"
            "• YELLOW tile = Letter is in the word but wrong spot.\n\n"
            "• GREY tile = Letter not in the word.\n\n"
            "• Extra: YELLOW tiles show the correct position number\n"
            "  (1–5) in the top-right corner.\n\n"
            "• Press ENTER to submit a guess.\n"
            "• Press BACKSPACE to delete a letter.\n\n"
            "Good luck!"
        )

        tk.Label(
            rules_window,
            text=rules_text,
            font=("Helvetica", 12),
            fg="#dddddd",
            bg="#121213",
            justify="left"
        ).pack(padx=20, pady=10)

        tk.Button(
            rules_window,
            text="Close",
            font=("Helvetica", 12, "bold"),
            bg="#538d4e",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=rules_window.destroy
        ).pack(pady=10)


    def key_press(self, key):
        if self.game_over:
            return

        if key == '⌫':
            self.delete_letter()
        elif key == 'ENTER':
            self.submit_word()
        else:
            self.add_letter(key)

    def keyboard_input(self, event):
        if self.game_over:
            return

        key = event.char.upper()
        if key.isalpha():
            self.add_letter(key)
        elif event.keysym == 'BackSpace':
            self.delete_letter()
        elif event.keysym == 'Return':
            self.submit_word()

    def add_letter(self, letter):
        if self.current_col < self.word_length:
            tile = self.tiles[self.current_row][self.current_col]
            tile.config(text=letter, borderwidth=3)
            self.current_col += 1

    def delete_letter(self):
        if self.current_col > 0:
            self.current_col -= 1
            tile = self.tiles[self.current_row][self.current_col]
            tile.config(text="", borderwidth=2)

    def submit_word(self):
        if self.current_col != self.word_length:
            messagebox.showwarning("Invalid", "Not enough letters!")
            return

        guess = ''.join(self.tiles[self.current_row][i].cget("text")
                        for i in range(self.word_length))

        # Word validation (optional)
        # if guess not in self.words:
        #     messagebox.showwarning("Invalid", "Not a valid word!")
        #     return

        self.check_guess(guess)

        if guess == self.target_word:
            messagebox.showinfo("Congratulations!",
                                f"You won! The word was {self.target_word}")
            self.game_over = True
            return

        self.current_row += 1
        self.current_col = 0

        if self.current_row >= self.max_attempts:
            messagebox.showinfo("Game Over",
                                f"You lost! The word was {self.target_word}")
            self.game_over = True

    def check_guess(self, guess):
        target = list(self.target_word)
        colors = [self.absent_color] * self.word_length

        # Exact matches
        for i in range(self.word_length):
            if guess[i] == target[i]:
                colors[i] = self.correct_color
                target[i] = None

        # Yellow matches
        for i in range(self.word_length):
            tile = self.tiles[self.current_row][i]
            tile.correct_spot = None

            if colors[i] == self.absent_color and guess[i] in target:
                colors[i] = self.present_color

                # Correct index (1–5)
                correct_index = self.target_word.index(guess[i]) + 1
                tile.correct_spot = correct_index

                target[target.index(guess[i])] = None

        # Apply colors and corner numbers
        for i in range(self.word_length):
            tile = self.tiles[self.current_row][i]
            tile.config(bg=colors[i], borderwidth=0)

            # Clear old labels
            for child in tile.place_slaves():
                child.destroy()

            # Add number label for yellow
            if colors[i] == self.present_color and tile.correct_spot:
                corner = tk.Label(tile, text=str(tile.correct_spot),
                                  font=("Helvetica", 7, "bold"),
                                  bg=self.present_color, fg="white")
                corner.place(relx=0.95, rely=0.05, anchor="ne")

            # Keyboard color updates
            letter = guess[i]
            kb = self.key_buttons.get(letter)

            if not kb:
                continue

            current = kb.cget("bg")

            # Priority: GREEN > YELLOW > GREY
            if colors[i] == self.correct_color:
                kb.config(bg=self.correct_color)
            elif colors[i] == self.present_color and current != self.correct_color:
                kb.config(bg=self.present_color)
            elif current == self.key_bg:
                kb.config(bg=self.absent_color)

    def new_game(self):
        self.root.destroy()
        main()


def main():
        root = tk.Tk()
        WordleGame(root)
        root.mainloop()


if __name__ == "__main__":
    main()
