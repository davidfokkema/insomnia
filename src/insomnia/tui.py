import random
import time
import humanize

from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from textual.app import App
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer, Header, Static


CHECK_DELAY = 1
MIN_SLEEP_DURATION = 60


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
    tracking_state = reactive(True)

    def toggle_tracking_state(self):
        self.tracking_state = not self.tracking_state

    def watch_tracking_state(self, is_tracking):
        if is_tracking:
            self.query_one("#tracking_state").update("Tracking...")
        else:
            self.query_one("#tracking_state").update("Paused tracking")

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

        self.set_interval(CHECK_DELAY, self.check_sleep)
        yield Header(show_clock=True)
        yield Footer()
        yield Container(id="past_periods")
        yield CurrentActivityWidget(id="current_activity")

    def action_toggle_tracking_state(self):
        self.query_one("#current_activity").toggle_tracking_state()

    async def check_sleep(self):
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
        await self.query_one("#past_periods").mount(log_active)
        await self.query_one("#past_periods").mount(log_slept)
        log_slept.scroll_visible()


def main():
    app = InsomniaApp()
    app.run()


if __name__ == "__main__":
    main()
