import operator
import random
import time
from dataclasses import dataclass, field

import humanize
import psutil
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from textual.app import App
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Footer, Header, Static

CHECK_DELAY = 1
MIN_SLEEP_DURATION = 60


@dataclass(order=True)
class ProcessStats:
    """Process statistics like name and cpu times."""

    name: str
    user_time: float
    sys_time: float
    total_time: float = field(init=False)

    def __post_init__(self):
        self.total_time = self.user_time + self.sys_time

    def __add__(self, other):
        return ProcessStats(
            self.name, self.user_time + other.user_time, self.sys_time + other.sys_time
        )

    def __sub__(self, other):
        return ProcessStats(
            self.name, self.user_time - other.user_time, self.sys_time - other.sys_time
        )


def get_process_statistics():
    """Get process statistics like name and cpu times.

    Returns:
        A dict where the keys are made up of tuples containing the
        process ID and process creation time. This ensures that every process
        gets a unique key, even if process IDs are reused. Each value is a
        ProcessStats instance.
    """
    return {
        (p.info["pid"], p.info["create_time"]): ProcessStats(
            name=p.info["name"],
            user_time=p.info["cpu_times"][0],
            sys_time=p.info["cpu_times"][1],
        )
        for p in psutil.process_iter(attrs=["pid", "create_time", "name", "cpu_times"])
        if p.info["cpu_times"] is not None
    }


class SleepinessDisplay(Static):
    sleepiness = reactive(0.0)

    def on_mount(self):
        self.progressbar = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
        )
        self.sleepingtask = self.progressbar.add_task("Steady sleep", total=1.0)

    def watch_sleepiness(self, sleepiness):
        self.log(f"Sleepiness update: {sleepiness}")
        self.progressbar.update(self.sleepingtask, completed=sleepiness)
        self.update(self.progressbar)


class CurrentActivityWidget(Static):
    is_tracking = reactive(True)

    def toggle_is_tracking(self):
        self.is_tracking = not self.is_tracking

    def watch_is_tracking(self, is_tracking):
        if is_tracking:
            self.query_one("#tracking_state").update("Tracking...")
        else:
            self.query_one("#tracking_state").update("Tracking paused...")

    def compose(self):
        yield Static(id="tracking_state")
        yield SleepinessDisplay(id="sleepiness")


class InsomniaApp(App):
    """An app for tracking wakeful moments during supposed sleep periods."""

    CSS_PATH = "insomnia.css"

    BINDINGS = [
        ("t", "toggle_tracking_state()", "Toggle tracking"),
        ("q", "quit()", "Quit"),
    ]

    sleeping = awake = 0

    def compose(self):
        self.t_prev_wake_event = self.t_prev_check = time.time()

        self.sleep_timer = self.set_interval(CHECK_DELAY, self.check_for_sleep)
        yield Header(show_clock=True)
        yield Footer()
        yield Container(id="past_activity")
        yield CurrentActivityWidget(id="current_activity")

    async def action_toggle_tracking_state(self):
        if self.query_one("#current_activity").is_tracking:
            tracking_msg = Static("Stopped tracking sleeps", classes="log stopped")
            self.awake += time.time() - self.t_prev_check
            self.sleep_timer.pause()
        else:
            tracking_msg = Static("Started tracking sleeps", classes="log started")
            self.t_prev_wake_event = self.t_prev_check = time.time()
            self.sleep_timer.resume()
        self.query_one("#current_activity").toggle_is_tracking()
        await self.query_one("#past_activity").mount(tracking_msg)
        tracking_msg.scroll_visible()

    async def check_for_sleep(self):
        """Check if computer was sleeping since last check.

        This method checks the elapsed time since the previous check. If more
        time has passed then MIN_SLEEP_DURATION it assumes that the computer has
        been sleeping. It is therefore important that you call this method
        regularly. Say, once per second.

        """
        now = time.time()
        delta_prev_check = now - self.t_prev_check
        if delta_prev_check > MIN_SLEEP_DURATION:  # or random.random() > 0.95:
            # Just woke up from sleep
            await self.log_sleep_period(
                active_duration=self.t_prev_check - self.t_prev_wake_event,
                sleep_duration=delta_prev_check,
            )
            # Update timestamps and durations
            self.t_prev_wake_event = now
            self.sleeping += delta_prev_check
        else:
            # Still active
            self.awake += delta_prev_check
        # Update common timestamp and sleepiness
        self.t_prev_check = now
        self.query_one("#sleepiness").sleepiness = self.sleeping / (
            self.awake + self.sleeping
        )

    async def log_sleep_period(self, active_duration, sleep_duration):
        """Log active and sleep entries after wake up.

        Args:
            active_duration (float): duration of last active period in seconds.
            sleep_duration (float): duration of sleep period in seconds.
        """
        # Add log entry to finish up last active period
        log_active = Static(
            f"{time.ctime(self.t_prev_wake_event)} — Active for {humanize.precisedelta(active_duration)}",
            classes="log active",
        )
        # Add log entry for the sleep period
        log_slept = Static(
            f"{time.ctime(self.t_prev_check)} — Slept for {humanize.precisedelta(sleep_duration)}",
            classes="log slept",
        )
        # Await mounting the widgets and scroll to the end
        await self.query_one("#past_activity").mount(log_active)
        await self.query_one("#past_activity").mount(log_slept)
        log_slept.scroll_visible()


def main():
    baseline_stats = get_process_statistics()
    process_stats = {}
    print(len(baseline_stats))
    time.sleep(1)
    for _ in range(5):
        process_stats |= get_process_statistics()
        print(len(process_stats))
        time.sleep(2)

    delta = [
        latest_stats - baseline_stats.get(k, ProcessStats(None, 0, 0))
        for k, latest_stats in process_stats.items()
    ]
    print(len(delta))
    print(sorted(delta, key=operator.attrgetter("total_time"), reverse=True)[:5])
    print()
    print()

    # app = InsomniaApp()
    # app.run()


if __name__ == "__main__":
    main()
