# cspell: ignore customtkinter padx pady pystray wraplength

import customtkinter as ctk
from tkinter import messagebox
import datetime
import os
import threading
import time
import sys
import pystray
from PIL import Image, ImageDraw

# 设置customtkinter主题
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class AutoShutdownApp:
    def __init__(self, root=None):
        self.root = root
        self.is_running = False
        self.shutdown_thread = None
        self.shutdown_time = None
        self.tray_icon = None
        
        if root:
            self.setup_gui()
        
    def setup_gui(self):
        """设置现代化图形界面"""
        self.root.title("自动关机工具")
        self.root.geometry("500x830")
        self.root.resizable(False, False)
        
        # 设置关闭窗口时的行为
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
        # 设置窗口图标（可选）
        # self.root.iconbitmap("icon.ico")  # 如果有图标文件的话
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建现代化界面组件"""
        # 主框架
        main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题区域
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="⏰ 自动关机工具",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#2E86AB"
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="安全可靠的定时关机解决方案",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 10))
        
        # 当前时间显示
        time_display_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        time_display_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.current_time_label = ctk.CTkLabel(
            time_display_frame,
            text="正在获取时间...",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2E86AB"
        )
        self.current_time_label.pack(pady=15)
        self.update_current_time()
        
        # 定时关机设置卡片
        self.create_time_setting_card(main_frame)
        
        # 倒计时设置卡片
        self.create_countdown_card(main_frame)
        
        # 状态显示区域
        self.create_status_display(main_frame)
        
        # 按钮区域
        self.create_button_area(main_frame)
        
        # 底部提示
        self.create_footer(main_frame)
        
    def create_time_setting_card(self, parent):
        """创建定时关机设置卡片"""
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", padx=20, pady=(0, 15))
        
        # 卡片标题
        card_title = ctk.CTkLabel(
            card,
            text="🕐 定时关机设置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        card_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # 时间输入区域
        input_frame = ctk.CTkFrame(card, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(input_frame, text="设置关机时间:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        
        # 小时选择
        self.hour_var = ctk.StringVar(value="18")
        hour_combo = ctk.CTkComboBox(
            input_frame,
            values=[f"{i:02d}" for i in range(24)],
            variable=self.hour_var,
            width=80,
            height=35,
            corner_radius=8
        )
        hour_combo.grid(row=0, column=1, padx=(0, 5))
        
        ctk.CTkLabel(input_frame, text="时").grid(row=0, column=2, padx=(0, 10))
        
        # 分钟选择
        self.minute_var = ctk.StringVar(value="00")
        minute_combo = ctk.CTkComboBox(
            input_frame,
            values=[f"{i:02d}" for i in range(60)],
            variable=self.minute_var,
            width=80,
            height=35,
            corner_radius=8
        )
        minute_combo.grid(row=0, column=3, padx=(0, 5))
        
        ctk.CTkLabel(input_frame, text="分").grid(row=0, column=4)
        
    def create_countdown_card(self, parent):
        """创建倒计时设置卡片"""
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", padx=20, pady=(0, 15))
        
        # 卡片标题
        card_title = ctk.CTkLabel(
            card,
            text="⏱️ 倒计时关机",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        card_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # 倒计时输入区域
        input_frame = ctk.CTkFrame(card, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(input_frame, text="倒计时时间:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        
        # 小时选择
        self.countdown_hour_var = ctk.StringVar(value="0")
        hour_combo = ctk.CTkComboBox(
            input_frame,
            values=[f"{i:02d}" for i in range(24)],
            variable=self.countdown_hour_var,
            width=80,
            height=35,
            corner_radius=8
        )
        hour_combo.grid(row=0, column=1, padx=(0, 5))
        
        ctk.CTkLabel(input_frame, text="小时").grid(row=0, column=2, padx=(0, 10))
        
        # 分钟选择
        self.countdown_minute_var = ctk.StringVar(value="30")
        minute_combo = ctk.CTkComboBox(
            input_frame,
            values=[f"{i:02d}" for i in range(60)],
            variable=self.countdown_minute_var,
            width=80,
            height=35,
            corner_radius=8
        )
        minute_combo.grid(row=0, column=3, padx=(0, 5))
        
        ctk.CTkLabel(input_frame, text="分钟").grid(row=0, column=4)
        
    def create_status_display(self, parent):
        """创建状态显示区域"""
        status_frame = ctk.CTkFrame(parent, corner_radius=12)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # 状态标题
        status_title = ctk.CTkLabel(
            status_frame,
            text="📊 状态信息",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        status_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="🔴 未设置关机任务",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#E74C3C"
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.shutdown_time_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.shutdown_time_label.pack(anchor="w", padx=20, pady=(0, 15))
        
    def create_button_area(self, parent):
        """创建按钮区域"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # 主要操作按钮
        self.start_button = ctk.CTkButton(
            button_frame,
            text="🚀 开始定时关机",
            command=self.start_shutdown,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#27AE60",
            hover_color="#219A52"
        )
        self.start_button.pack(fill="x", pady=(0, 10))
        
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ 取消关机",
            command=self.cancel_shutdown,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="#E74C3C",
            hover_color="#C0392B",
            state="disabled"
        )
        self.cancel_button.pack(fill="x", pady=(0, 10))
        
        # 立即关机按钮
        shutdown_now_btn = ctk.CTkButton(
            button_frame,
            text="⚡ 立即关机",
            command=self.shutdown_now,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="#E67E22",
            hover_color="#D35400"
        )
        shutdown_now_btn.pack(fill="x")
        
    def create_footer(self, parent):
        """创建底部信息"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        info_text = "💡 设置关机后可以最小化到系统托盘，程序会在后台继续运行"
        info_label = ctk.CTkLabel(
            footer_frame,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=400
        )
        info_label.pack(pady=10)
        
    def update_current_time(self):
        """更新当前时间显示"""
        if hasattr(self, 'current_time_label'):
            current_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
            self.current_time_label.configure(text=f"🕒 当前时间: {current_time}")
            if self.root:
                self.root.after(1000, self.update_current_time)
        
    def start_shutdown(self):
        """开始定时关机"""
        if self.is_running:
            messagebox.showwarning("警告", "已有定时关机任务在运行！")
            return
            
        # 获取定时关机时间
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise ValueError("时间格式错误")
                
            # 计算关机时间
            now = datetime.datetime.now()
            shutdown_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 如果设置的时间已经过去，则设置为明天
            if shutdown_time < now:
                shutdown_time += datetime.timedelta(days=1)
                
            time_difference = shutdown_time - now
            total_seconds = time_difference.total_seconds()
            
        except ValueError:
            # 如果定时时间设置错误，尝试使用倒计时
            try:
                countdown_hours = int(self.countdown_hour_var.get())
                countdown_minutes = int(self.countdown_minute_var.get())
                
                if countdown_hours < 0 or countdown_minutes < 0:
                    raise ValueError("倒计时时间不能为负数")
                    
                total_seconds = countdown_hours * 3600 + countdown_minutes * 60
                shutdown_time = datetime.datetime.now() + datetime.timedelta(seconds=total_seconds)
                
            except ValueError:
                messagebox.showerror("错误", "请输入有效的时间！")
                return
        
        if total_seconds < 60:
            messagebox.showwarning("警告", "关机时间必须至少1分钟！")
            return
            
        self.is_running = True
        self.shutdown_time = shutdown_time
        
        # 更新界面状态
        self.start_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.status_label.configure(
            text="🟢 已设置定时关机", 
            text_color="#27AE60"
        )
        self.shutdown_time_label.configure(
            text=f"📅 计划关机时间: {shutdown_time.strftime('%Y年%m月%d日 %H:%M:%S')}"
        )
        
        # 启动后台线程执行关机任务
        self.shutdown_thread = threading.Thread(target=self.execute_shutdown, args=(total_seconds,))
        self.shutdown_thread.daemon = True
        self.shutdown_thread.start()
        
        messagebox.showinfo("提示", 
            f"✅ 已设置定时关机！\n\n"
            f"📅 关机时间: {shutdown_time.strftime('%Y年%m月%d日 %H:%M:%S')}\n"
            f"⏰ 剩余时间: {self.format_time(total_seconds)}\n\n"
            f"程序将转为后台运行，可在系统托盘中查看状态。")
        
    def format_time(self, seconds):
        """格式化时间显示"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}小时{minutes}分钟"
        
    def execute_shutdown(self, delay_seconds):
        """执行关机操作"""
        try:
            # 等待指定时间
            remaining_time = delay_seconds
            while remaining_time > 0 and self.is_running:
                time.sleep(1)
                remaining_time -= 1
                
                # 每60秒更新一次托盘提示
                if remaining_time % 60 == 0 and self.tray_icon:
                    minutes_left = remaining_time // 60
                    self.update_tray_tooltip(f"自动关机工具 - 剩余时间: {minutes_left}分钟")
            
            if self.is_running and remaining_time <= 0:
                # 执行关机命令
                if os.name == 'nt':  # Windows
                    os.system("shutdown /s /f /t 0")
                else:  # Linux/Mac
                    os.system("shutdown -h now")
                    
        except Exception as e:
            print(f"关机过程中出现错误: {e}")
            
    def cancel_shutdown(self):
        """取消关机"""
        self.is_running = False
        # 更新界面状态
        self.start_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        self.status_label.configure(
            text="🟡 已取消关机", 
            text_color="#F39C12"
        )
        self.shutdown_time_label.configure(text="")
        
        # 取消系统关机任务（仅Windows）
        if os.name == 'nt':
            os.system("shutdown /a")
            
        if self.tray_icon:
            self.update_tray_tooltip("自动关机工具 - 未设置关机")
            
        messagebox.showinfo("提示", "✅ 已取消定时关机！")
        
    def shutdown_now(self):
        """立即关机"""
        if messagebox.askyesno("确认关机", "⚠️  确定要立即关机吗？\n\n请确保已保存所有工作！"):
            if os.name == 'nt':  # Windows
                os.system("shutdown /s /f /t 0")
            else:  # Linux/Mac
                os.system("shutdown -h now")
    
    def create_tray_icon(self):
        """创建系统托盘图标"""
        # 创建现代化图标
        image = Image.new('RGB', (64, 64), color='#2E86AB')
        draw = ImageDraw.Draw(image)
        # 绘制一个简单的时钟图标
        draw.ellipse([12, 12, 52, 52], fill='white', outline='#2E86AB', width=3)
        draw.line([32, 32, 32, 20], fill='#2E86AB', width=3)  # 时针
        draw.line([32, 32, 45, 32], fill='#E74C3C', width=2)  # 分针
        
        # 托盘菜单
        menu = (
            pystray.MenuItem("🪟 显示窗口", self.show_window),
            pystray.MenuItem("❌ 取消关机", self.cancel_shutdown),
            pystray.MenuItem("🚪 退出", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("auto_shutdown", image, "自动关机工具", menu)
    
    def update_tray_tooltip(self, tooltip):
        """更新托盘提示"""
        if self.tray_icon:
            self.tray_icon.title = tooltip
    
    def minimize_to_tray(self):
        """最小化到系统托盘"""
        if self.root:
            self.root.withdraw()  # 隐藏窗口
        messagebox.showinfo("提示", 
            "🔄 程序已转为后台运行\n\n"
            "📌 可在系统托盘中查看状态\n"
            "🖱️ 右键点击托盘图标可进行操作")
        
    def show_window(self):
        """显示主窗口"""
        if self.root:
            self.root.deiconify()  # 显示窗口
            self.root.lift()
            self.root.focus_force()
    
    def quit_app(self):
        """退出应用程序"""
        self.is_running = False
        if self.tray_icon:
            self.tray_icon.stop()
        if self.root:
            self.root.quit()
        sys.exit(0)
    
    def run_tray(self):
        """运行托盘图标"""
        self.create_tray_icon()
        self.tray_icon.run()

def main():
    # 创建主窗口
    root = ctk.CTk()
    app = AutoShutdownApp(root)
    
    # 启动托盘图标在后台线程运行
    tray_thread = threading.Thread(target=app.run_tray)
    tray_thread.daemon = True
    tray_thread.start()
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()