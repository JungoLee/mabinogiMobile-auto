# -*- coding: utf-8 -*-
"""
Simple Rich Demo - Windows 콘솔 호환 버전
"""

import sys
import os
import time

# UTF-8 인코딩 강제 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Rich 임포트
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich import box

console = Console()


def demo1_simple_output():
    """간단한 출력 데모"""
    console.clear()
    console.print("\n[bold cyan]Demo 1: Simple Colored Output[/bold cyan]\n")

    console.print("[green]SUCCESS:[/green] Game started successfully!")
    console.print("[yellow]WARNING:[/yellow] Low health detected")
    console.print("[red]ERROR:[/red] Connection failed")
    console.print("[blue]INFO:[/blue] Loading quest data...")
    console.print("[magenta]DEBUG:[/magenta] Mouse position: (500, 300)")

    time.sleep(2)


def demo2_table():
    """테이블 데모"""
    console.clear()
    console.print("\n[bold cyan]Demo 2: Statistics Table[/bold cyan]\n")

    table = Table(title="Game Statistics", box=box.ROUNDED)

    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_column("Status", justify="center")

    table.add_row("Quests Completed", "15", "[green]OK[/green]")
    table.add_row("Gold Collected", "50,000", "[green]OK[/green]")
    table.add_row("Items Traded", "8", "[yellow]WARN[/yellow]")
    table.add_row("Daily Tasks", "3/5", "[cyan]IN PROGRESS[/cyan]")

    console.print(table)
    time.sleep(2)


def demo3_panel():
    """패널 데모"""
    console.clear()
    console.print("\n[bold cyan]Demo 3: Log Panel[/bold cyan]\n")

    log_content = """[dim][10:30:15][/dim] [green]INFO[/green]     Quest window opened
[dim][10:30:16][/dim] [cyan]INFO[/cyan]     Looking for available quests
[dim][10:30:17][/dim] [green]SUCCESS[/green]  Quest found!
[dim][10:30:18][/dim] [yellow]INFO[/yellow]     Clicking quest at (500, 300)
[dim][10:30:19][/dim] [green]SUCCESS[/green]  Quest accepted"""

    panel = Panel(
        log_content,
        title="Recent Logs",
        border_style="yellow",
        box=box.ROUNDED
    )

    console.print(panel)
    time.sleep(2)


def demo4_progress():
    """진행바 데모"""
    console.clear()
    console.print("\n[bold cyan]Demo 4: Progress Bar[/bold cyan]\n")

    stories = [
        "Loading Quest Story...",
        "Loading Trade Story...",
        "Loading Daily Story...",
        "Initializing Monitor...",
        "Starting Automation..."
    ]

    for story in track(stories, description="[cyan]Preparing automation"):
        time.sleep(0.5)

    console.print("\n[bold green]All stories loaded successfully![/bold green]")
    time.sleep(2)


def demo5_live_stats():
    """실시간 통계 데모"""
    console.clear()
    console.print("\n[bold cyan]Demo 5: Live Statistics (10 seconds)[/bold cyan]\n")

    for i in range(10):
        # 화면 클리어 (간단한 방법)
        console.print("\n" * 50)

        # 통계 테이블 생성
        table = Table(title=f"Live Monitor - Iteration {i+1}/10", box=box.SIMPLE)
        table.add_column("Stat", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Uptime", f"{i+1} seconds")
        table.add_row("Screenshots", str(i * 2))
        table.add_row("Clicks", str(i * 3))
        table.add_row("Status", "[green]Running[/green]" if i < 9 else "[yellow]Stopping[/yellow]")

        console.print(table)
        console.print(f"\n[dim]Updating in {1} second...[/dim]")

        time.sleep(1)

    console.print("\n[bold green]Demo completed![/bold green]")


def main():
    """메인 함수"""
    try:
        console.clear()
        console.print("\n[bold magenta]Rich Library Demo for Game Automation[/bold magenta]\n")

        demos = [
            ("Simple Colored Output", demo1_simple_output),
            ("Statistics Table", demo2_table),
            ("Log Panel", demo3_panel),
            ("Progress Bar", demo4_progress),
            ("Live Statistics", demo5_live_stats)
        ]

        for i, (name, func) in enumerate(demos, 1):
            console.print(f"\n[cyan]{i}. Running demo: {name}[/cyan]")
            time.sleep(1)
            func()

        console.clear()
        console.print("\n[bold green]All demos completed![/bold green]\n")
        console.print("Rich library can be used to create:")
        console.print("  - Colored logs with different severity levels")
        console.print("  - Statistics tables that update in real-time")
        console.print("  - Panels for organizing information")
        console.print("  - Progress bars for long-running tasks")
        console.print("  - Live monitoring dashboards")
        console.print()

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
