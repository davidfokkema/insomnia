import random
import time
import humanize

from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from textual.app import App
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer, Header, Static

CHECK_DELAY = 0.1
MIN_SLEEP_DURATION = 2


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
        self.t_last_wake = self.t_prev = time.time()

        self.set_interval(CHECK_DELAY, self.check_sleep)
        yield Header()
        yield Footer()
        yield Container(id="past_periods")
        yield CurrentActivityWidget(id="current_activity")

    def action_toggle_tracking_state(self):
        self.query_one("#current_activity").toggle_tracking_state()

    def check_sleep(self):
        now = time.time()
        delta_t = now - self.t_prev
        if delta_t > MIN_SLEEP_DURATION or random.random() > 0.95:
            # Just woke up from sleep
            log_active = Static(
                f"{time.ctime(self.t_last_wake)} — Active for {humanize.precisedelta(self.t_prev - self.t_last_wake)}",
                classes="log active",
            )
            log_slept = Static(
                f"{time.ctime(self.t_prev)} — Slept for {humanize.naturaldelta(now - self.t_prev)}",
                classes="log slept",
            )
            self.query_one("#past_periods").mount(log_active)
            self.query_one("#past_periods").mount(log_slept)
            # log_slept.scroll_visible()
            self.t_last_wake = now
            self.sleeping += delta_t
        else:
            # Still active
            self.awake += delta_t
        self.t_prev = now
        self.query_one("#sleepiness").sleepiness = self.sleeping / (
            self.awake + self.sleeping
        )


def main():
    app = InsomniaApp()
    app.run()


if __name__ == "__main__":
    main()
