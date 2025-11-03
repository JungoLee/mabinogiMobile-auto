# -*- coding: utf-8 -*-
"""
Rich Monitor - 예쁜 CLI UI로 실시간 모니터링
"""

import sys
import os
import time
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import box

import pyautogui


class RichMonitor:
    """Rich 라이브러리를 사용한 예쁜 모니터"""

    def __init__(self):
        self.console = Console()
        self.logs = []
        self.max_logs = 15
        self.stats = {
            "start_time": datetime.datetime.now(),
            "screenshot_count": 0,
            "click_count": 0,
            "key_press_count": 0,
            "current_story": "Waiting...",
            "status": "Ready"
        }

    def add_log(self, message, level="INFO"):
        """로그 추가"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # 레벨에 따른 색상
        color_map = {
            "INFO": "cyan",
            "SUCCESS": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "DEBUG": "blue"
        }
        color = color_map.get(level, "white")

        log_entry = {
            "time": timestamp,
            "level": level,
            "message": message,
            "color": color
        }

        self.logs.append(log_entry)

        # 최대 로그 수 유지
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def update_stats(self, key, value):
        """통계 업데이트"""
        self.stats[key] = value

    def create_header(self):
        """헤더 생성"""
        title = Text("Mabinogi Mobile Auto", style="bold magenta")
        subtitle = Text("Real-time Game Automation Monitor", style="dim")
        return Panel(
            Text.assemble(title, "\n", subtitle),
            box=box.DOUBLE,
            border_style="magenta"
        )

    def create_stats_panel(self):
        """통계 패널 생성"""
        elapsed = datetime.datetime.now() - self.stats["start_time"]
        elapsed_str = str(elapsed).split('.')[0]

        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column("Key", style="cyan")
        stats_table.add_column("Value", style="yellow")

        stats_table.add_row("Uptime", elapsed_str)
        stats_table.add_row("Screenshots", str(self.stats["screenshot_count"]))
        stats_table.add_row("Clicks", str(self.stats["click_count"]))
        stats_table.add_row("Key Presses", str(self.stats["key_press_count"]))
        stats_table.add_row("Current Story", self.stats["current_story"])

        # 상태에 따른 색상
        status = self.stats["status"]
        status_color = "green" if status == "Running" else "yellow"
        stats_table.add_row("Status", f"[{status_color}]{status}[/{status_color}]")

        return Panel(stats_table, title="Statistics", border_style="blue")

    def create_mouse_info_panel(self):
        """마우스 정보 패널"""
        x, y = pyautogui.position()
        pixel_color = pyautogui.pixel(x, y)

        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column("Key", style="cyan")
        info_table.add_column("Value", style="green")

        info_table.add_row("Position", f"({x}, {y})")
        info_table.add_row("Pixel Color", f"RGB{pixel_color}")

        screen_w, screen_h = pyautogui.size()
        info_table.add_row("Screen Size", f"{screen_w} x {screen_h}")

        return Panel(info_table, title="Mouse Info", border_style="green")

    def create_log_panel(self):
        """로그 패널 생성"""
        if not self.logs:
            log_text = Text("No logs yet...", style="dim")
        else:
            log_lines = []
            for log in self.logs:
                time_text = Text(f"[{log['time']}]", style="dim")
                level_text = Text(f" {log['level']:8}", style=f"bold {log['color']}")
                message_text = Text(f" {log['message']}", style=log['color'])

                log_lines.append(Text.assemble(time_text, level_text, message_text))

            log_text = Text("\n").join(log_lines)

        return Panel(
            log_text,
            title="Logs",
            border_style="yellow",
            height=self.max_logs + 2
        )

    def create_layout(self):
        """전체 레이아웃 생성"""
        layout = Layout()

        # 레이아웃 구조
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )

        # 메인을 좌우로 분할
        layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )

        # 우측을 상하로 분할
        layout["right"].split_column(
            Layout(name="stats"),
            Layout(name="mouse")
        )

        # 각 영역에 컨텐츠 배치
        layout["header"].update(self.create_header())
        layout["left"].update(self.create_log_panel())
        layout["stats"].update(self.create_stats_panel())
        layout["mouse"].update(self.create_mouse_info_panel())
        layout["footer"].update(
            Panel(
                Text("Press 'Q' to quit | 'S' to screenshot | 'T' to test log",
                     style="bold cyan", justify="center"),
                border_style="dim"
            )
        )

        return layout

    def run(self):
        """모니터 실행"""
        self.console.clear()
        self.add_log("Monitor started", "SUCCESS")
        self.update_stats("status", "Running")

        try:
            with Live(self.create_layout(), console=self.console, refresh_per_second=4) as live:
                iteration = 0

                while True:
                    iteration += 1

                    # 레이아웃 업데이트
                    live.update(self.create_layout())

                    # 키 입력 체크 (간단한 방법)
                    # 실제로는 keyboard 라이브러리 사용 가능

                    time.sleep(0.25)

                    # 테스트: 3초마다 자동 로그 추가
                    if iteration % 12 == 0:
                        test_messages = [
                            ("Monitoring game screen...", "INFO"),
                            ("Quest detected!", "SUCCESS"),
                            ("Clicking button at (500, 300)", "INFO"),
                            ("Waiting for loading...", "WARNING"),
                        ]
                        msg, level = test_messages[(iteration // 12) % len(test_messages)]
                        self.add_log(msg, level)

                        # 통계 업데이트
                        if "Clicking" in msg:
                            self.stats["click_count"] += 1
                        elif "screenshot" in msg.lower():
                            self.stats["screenshot_count"] += 1

        except KeyboardInterrupt:
            self.add_log("Monitor stopped by user", "WARNING")
            self.update_stats("status", "Stopped")
            time.sleep(1)


def demo_with_progress():
    """진행 바 데모"""
    console = Console()

    console.print("\n[bold magenta]Story Execution Demo[/bold magenta]\n")

    stories = ["Quest Story", "Trade Story", "Daily Content Story"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:

        main_task = progress.add_task("[cyan]Overall Progress", total=len(stories))

        for story in stories:
            story_task = progress.add_task(f"[yellow]{story}", total=100)

            for i in range(100):
                time.sleep(0.02)
                progress.update(story_task, advance=1)

            progress.update(main_task, advance=1)
            console.print(f"[green]✓[/green] {story} completed!")

    console.print("\n[bold green]All stories completed![/bold green]\n")


def main():
    """메인 함수"""
    console = Console()

    console.print("\n[bold cyan]Select Monitor Mode:[/bold cyan]")
    console.print("  1. Real-time Monitor (Live UI)")
    console.print("  2. Progress Bar Demo")
    console.print()

    choice = console.input("[yellow]Enter choice (1/2): [/yellow]")

    if choice == "1":
        monitor = RichMonitor()
        monitor.run()
    elif choice == "2":
        demo_with_progress()
    else:
        console.print("[red]Invalid choice![/red]")


if __name__ == "__main__":
    main()
