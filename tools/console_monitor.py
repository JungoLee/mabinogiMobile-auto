# -*- coding: utf-8 -*-
"""
Console Monitor - 실시간 콘솔 모니터링 (Rich 사용)
실시간으로 마우스 위치, 화면 정보, 로그를 표시합니다
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


class ConsoleMonitor:
    """콘솔 기반 실시간 모니터"""

    def __init__(self):
        self.console = Console()
        self.start_time = datetime.datetime.now()
        self.frame_count = 0
        self.logs = []
        self.max_logs = 10

    def add_log(self, message, level="INFO"):
        """로그 추가"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": "cyan",
            "SUCCESS": "green",
            "WARNING": "yellow",
            "ERROR": "red"
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
        table.add_column("Key", style="cyan", width=15)
        table.add_column("Value", style="yellow")

        table.add_row("Position", f"({x}, {y})")
        table.add_row("Pixel Color", f"RGB{color}")
        table.add_row("Screen Size", f"{screen_w} x {screen_h}")

        return Panel(table, title="Mouse Info", border_style="green", box=box.ROUNDED)

    def create_logs_panel(self):
        """로그 패널"""
        if not self.logs:
            content = Text("No logs yet...", style="dim")
        else:
            lines = []
            for timestamp, level, message, color in self.logs:
                line = Text.assemble(
                    Text(f"[{timestamp}]", style="dim"),
                    Text(f" {level:8}", style=f"bold {color}"),
                    Text(f" {message}", style=color)
                )
                lines.append(line)
            content = Text("\n").join(lines)

        return Panel(
            content,
            title="Recent Logs",
            border_style="yellow",
            box=box.ROUNDED,
            height=self.max_logs + 2
        )

    def create_stats_panel(self):
        """통계 패널"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Stat", style="cyan", width=15)
        table.add_column("Value", style="green")

        table.add_row("Status", "[green]RUNNING[/green]")
        table.add_row("Mode", "Monitoring")
        table.add_row("FPS", "~2")

        return Panel(table, title="Statistics", border_style="blue", box=box.ROUNDED)

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
                Text("Press Ctrl+C to stop | Monitoring in progress...",
                     style="bold cyan", justify="center"),
                border_style="dim"
            )
        )

        return layout

    def run(self, duration=30):
        """모니터 실행"""
        self.console.clear()
        self.add_log("Monitor started", "SUCCESS")

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

                    # 주기적으로 로그 추가
                    if self.frame_count % 5 == 0:
                        messages = [
                            ("Monitoring game screen...", "INFO"),
                            ("Checking game state...", "INFO"),
                            ("All systems normal", "SUCCESS"),
                            ("Waiting for trigger...", "INFO"),
                        ]
                        msg, level = messages[(self.frame_count // 5) % len(messages)]
                        self.add_log(msg, level)

                    time.sleep(0.5)

                self.add_log(f"Monitor completed ({duration}s)", "SUCCESS")

        except KeyboardInterrupt:
            self.add_log("Monitor stopped by user", "WARNING")
        except Exception as e:
            self.add_log(f"Error: {str(e)}", "ERROR")


def main():
    """메인 함수"""
    console = Console()

    console.print("\n[bold cyan]Console Monitor[/bold cyan]\n")
    console.print("This will monitor your screen for 15 seconds")
    console.print("Move your mouse around to see the position change\n")

    choice = console.input("[yellow]Press Enter to start (or type duration in seconds): [/yellow]").strip()

    duration = 15
    if choice.isdigit():
        duration = int(choice)

    monitor = ConsoleMonitor()
    monitor.run(duration=duration)

    console.print("\n[bold green]Monitoring completed![/bold green]\n")


if __name__ == "__main__":
    main()
