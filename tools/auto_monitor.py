# -*- coding: utf-8 -*-
"""
Auto Monitor - 자동으로 시작하는 실시간 모니터
"""

import sys
import os
import time
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# UTF-8 인코딩 강제
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import pyautogui
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box


class AutoMonitor:
    """자동 시작 실시간 모니터"""

    def __init__(self):
        self.console = Console()
        self.start_time = datetime.datetime.now()
        self.frame_count = 0
        self.logs = []
        self.max_logs = 10
        self.stats = {
            "clicks": 0,
            "screenshots": 0,
            "key_presses": 0
        }

    def add_log(self, message, level="INFO"):
        """로그 추가"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": "cyan",
            "SUCCESS": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "DEBUG": "blue"
        }
        color = color_map.get(level, "white")

        self.logs.append((timestamp, level, message, color))
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def create_header(self):
        """헤더 생성"""
        elapsed = datetime.datetime.now() - self.start_time
        elapsed_str = str(elapsed).split('.')[0]

        title = Text("GAME AUTOMATION MONITOR", style="bold magenta", justify="center")
        subtitle = Text(f"Uptime: {elapsed_str} | Frame: {self.frame_count}",
                       style="dim", justify="center")

        return Panel(
            Text.assemble(title, "\n", subtitle),
            box=box.DOUBLE,
            border_style="magenta"
        )

    def create_mouse_panel(self):
        """마우스 정보 패널"""
        try:
            x, y = pyautogui.position()
            color = pyautogui.pixel(x, y)
            screen_w, screen_h = pyautogui.size()
        except Exception as e:
            x, y = 0, 0
            color = (0, 0, 0)
            screen_w, screen_h = 0, 0

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="cyan", width=12)
        table.add_column("Value", style="yellow")

        table.add_row("X", str(x))
        table.add_row("Y", str(y))
        table.add_row("RGB", f"{color}")
        table.add_row("Screen", f"{screen_w}x{screen_h}")

        return Panel(table, title="Mouse", border_style="green", box=box.ROUNDED)

    def create_logs_panel(self):
        """로그 패널"""
        if not self.logs:
            content = Text("Waiting for logs...", style="dim")
        else:
            lines = []
            for timestamp, level, message, color in self.logs[-10:]:  # 최근 10개만
                line = Text.assemble(
                    Text(f"[{timestamp}]", style="dim"),
                    Text(f" {level:7}", style=f"bold {color}"),
                    Text(f" {message}", style=color)
                )
                lines.append(line)
            content = Text("\n").join(lines)

        return Panel(
            content,
            title="Activity Log",
            border_style="yellow",
            box=box.ROUNDED,
            height=self.max_logs + 2
        )

    def create_stats_panel(self):
        """통계 패널"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Stat", style="cyan", width=12)
        table.add_column("Value", style="green")

        table.add_row("Status", "[green]ACTIVE[/green]")
        table.add_row("Clicks", str(self.stats["clicks"]))
        table.add_row("Screenshots", str(self.stats["screenshots"]))
        table.add_row("Keys", str(self.stats["key_presses"]))

        return Panel(table, title="Stats", border_style="blue", box=box.ROUNDED)

    def create_layout(self):
        """레이아웃 생성"""
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )

        layout["body"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )

        layout["right"].split_column(
            Layout(name="mouse"),
            Layout(name="stats")
        )

        # 컨텐츠 배치
        layout["header"].update(self.create_header())
        layout["left"].update(self.create_logs_panel())
        layout["mouse"].update(self.create_mouse_panel())
        layout["stats"].update(self.create_stats_panel())
        layout["footer"].update(
            Panel(
                Text("Ctrl+C to stop | Monitoring your screen in real-time",
                     style="bold cyan", justify="center"),
                border_style="dim"
            )
        )

        return layout

    def simulate_activity(self):
        """활동 시뮬레이션"""
        messages = [
            ("System initialized", "SUCCESS"),
            ("Monitoring game window...", "INFO"),
            ("Detecting game state...", "INFO"),
            ("Quest available detected", "SUCCESS"),
            ("Preparing to click button", "INFO"),
            ("Button clicked at (500, 300)", "SUCCESS"),
            ("Waiting for response...", "WARNING"),
            ("Action completed successfully", "SUCCESS"),
            ("Checking next task...", "INFO"),
            ("All systems operational", "SUCCESS"),
        ]

        import random
        msg, level = random.choice(messages)
        self.add_log(msg, level)

        # 통계 업데이트
        if "click" in msg.lower():
            self.stats["clicks"] += 1
        elif "screenshot" in msg.lower():
            self.stats["screenshots"] += 1
        elif "key" in msg.lower():
            self.stats["key_presses"] += 1

    def run(self, duration=20):
        """모니터 실행"""
        self.console.clear()
        self.add_log("Monitor started successfully", "SUCCESS")
        self.add_log("Initializing monitoring system...", "INFO")

        try:
            with Live(
                self.create_layout(),
                console=self.console,
                refresh_per_second=2
            ) as live:

                end_time = time.time() + duration

                while time.time() < end_time:
                    self.frame_count += 1

                    # 레이아웃 업데이트
                    live.update(self.create_layout())

                    # 주기적으로 활동 시뮬레이션
                    if self.frame_count % 3 == 0:
                        self.simulate_activity()

                    time.sleep(0.5)

                self.add_log(f"Monitor session ended ({duration}s)", "SUCCESS")
                time.sleep(1)

        except KeyboardInterrupt:
            self.add_log("Monitor stopped by user", "WARNING")
            time.sleep(1)
        except Exception as e:
            self.add_log(f"Error: {str(e)}", "ERROR")


def main():
    """메인 함수"""
    console = Console()

    console.print("\n[bold cyan]Starting Auto Monitor...[/bold cyan]")
    console.print("[dim]Monitoring will run for 20 seconds[/dim]\n")

    time.sleep(1)

    monitor = AutoMonitor()
    monitor.run(duration=20)

    console.print("\n[bold green]Monitoring session completed![/bold green]\n")


if __name__ == "__main__":
    main()
