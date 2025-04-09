import tkinter as tk
from tkinter import ttk, messagebox
import time

try:
    import clipboard
    import keyboard
except ImportError as e:
    messagebox.showerror("알림", f"{e}\n라이브러리가 올바르지 않습니다!\nlibraryInstall.bat을 한번 실행시켜주세요")

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("수강신청 매크로")
        self.root.geometry("420x350")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        root.iconbitmap("images/icon.ico")

        self.copyable = True
        self.doEnter = True
        self.style = None
        self.tree = None
        self.data = self.read_data("초기설정.txt")
        
        # 쿨타임 << 개고생 원인 / 고마워요 딥시크
        self.last_key_time = 0
        self.cooldown = 0.05
        
        self.toggle_copy_label = None
        self.toggle_copy_ = None
        self.doEnter_label = None
        self.doEnter_ = None
        
        self.setup_ui()
        self.setup_hotkeys()
        
    def read_data(self, filename):
        data = []
        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line_count, line in enumerate(file, start=1):
                    line = line.strip()
                    if line:
                        subject, professor = line.split(maxsplit=1)
                        data.append((line_count, subject, professor))
        except FileNotFoundError:
            messagebox.showerror("알림", f"{filename}이 존재하지 않습니다!\nreadme.txt를 읽어주세요")
            exit()
        
        if len(data) > 10:
            messagebox.showerror("알림", "수업의 개수가 10보다 많습니다!\nreadme.txt를 읽어주세요")
            exit()
        elif len(data) < 1:
            messagebox.showerror("알림", "초기설정이 완료되지 않았습니다!\nreadme.txt를 읽어주세요")
            exit()
        
        return data
    
    def setup_ui(self):
        self.configure_root_style()
        self.configure_treeview_style()
        self.create_treeview()
        self.create_labels()
        self.arrange_widgets()
    
    def configure_root_style(self):
        self.root.configure(bg='#262626')
    
    def configure_treeview_style(self):
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview",
                             background="#262626",
                             fieldbackground="#262626",
                             foreground="#c0c0c0")
        self.style.configure("Treeview.Heading",
                             background="#262626",
                             fieldbackground="#262626",
                             foreground="#c0c0c0")
        self.style.map("Treeview",
                       background=[('selected', 'skyblue')],
                       foreground=[('selected', 'gray')])
        self.style.map("Treeview.Heading",
                       background=[('selected', '#262626')],
                       foreground=[('selected', '#c0c0c0')])
    
    def create_treeview(self):
        columns = ("번호", "교과목명", "담당 교수")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10, style="Treeview")
        
        self.tree.heading("번호", text="번호")
        self.tree.heading("교과목명", text="교과목명")
        self.tree.heading("담당 교수", text="담당 교수")
        
        self.tree.column("번호", anchor="center", width=5)
        self.tree.column("교과목명", anchor="center", width=200, stretch=False)
        self.tree.column("담당 교수", anchor="center", width=150, stretch=False)
        
        for row in self.data:
            self.tree.insert("", "end", values=row)
    
    def create_labels(self):
        self.toggle_copy_ = self.create_label("복붙", "white")
        self.doEnter_ = self.create_label("자동엔터", "white")
        self.toggle_copy_label = self.create_label("활성화", "green")
        self.doEnter_label = self.create_label("활성화", "green")
        
        self.create_hotkey_label("단축키 : Ctrl+Q", 0)
        self.create_hotkey_label("단축키 : Ctrl+Shift+Q", 1)
    
    def create_label(self, initial_text, fg_color):
        return tk.Label(self.root, text=initial_text, font=("Arial", 12), fg=fg_color, bg="#262626")
    
    def create_hotkey_label(self, text, column):
        label = tk.Label(self.root, text=text, font=("Arial", 12), bg="#262626", fg="white")
        label.grid(row=3, column=column, pady=5, sticky="ew")
    
    def arrange_widgets(self):
        self.tree.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        
        self.toggle_copy_.grid(row=1, column=0, pady=5, sticky="ew")
        self.doEnter_.grid(row=1, column=1, pady=5, sticky="ew")
        self.toggle_copy_label.grid(row=2, column=0, pady=5, sticky="ew")
        self.doEnter_label.grid(row=2, column=1, pady=5, sticky="ew")
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
    
    def setup_hotkeys(self):
        keyboard.add_hotkey("ctrl+q", self.toggle_copy)
        keyboard.add_hotkey("ctrl+shift+q", self.toggle_doEnter)
        keyboard.hook(self.selectKey)
        self.tree.bind("<Button-1>", lambda e: "break")
    
    def toggle_copy(self):
        self.copyable = not self.copyable
        status_text = "활성화" if self.copyable else "비활성화"
        self.toggle_copy_label.config(text=status_text, fg="green" if self.copyable else "red")
    
    def toggle_doEnter(self):
        self.doEnter = not self.doEnter
        status_text = "활성화" if self.doEnter else "비활성화"
        self.doEnter_label.config(text=status_text, fg="green" if self.doEnter else "red")
    
    def selectKey(self, event):
        current_time = time.time()
        if current_time - self.last_key_time < self.cooldown:
            return  # 쿨타임 중이면 무시
        
        if not self.copyable:
            return
        key = event.name
        if key not in "1234567890":
            return
        key = "10" if key=="0" else key
        index = int(key) - 1
        children = self.tree.get_children()
        
        if 0 <= index < len(children):
            item_id = children[index]
            self.tree.selection_set(item_id)
            self.tree.focus(item_id)
            value = self.tree.item(item_id, 'values')[1]
            clipboard.copy(value)
            keyboard.send("ctrl+a")
            time.sleep(.05)
            keyboard.send("ctrl+v")
            if self.doEnter:
                keyboard.send("enter")
        
        self.last_key_time = time.time()
    
    def run(self):
        self.root.mainloop()

# 실행
root = tk.Tk()
app = Application(root)
app.run()
