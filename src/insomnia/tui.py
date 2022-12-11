from textual.app import App
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer, Header, Static
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn


class SleepinessDisplay(Static):
    sleepiness = reactive(0.0)

    def on_mount(self):
        self.progressbar = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        )
        self.sleepingtask = self.progressbar.add_task("Sleeping", start=False)
        self.set_interval(1 / 10, self.update_widget)

    def watch_sleepiness(self, sleepiness):
        print(f"Sleepiness update: {sleepiness}")
        self.progressbar.update(self.sleepingtask, completed=sleepiness)

    def update_widget(self):
        self.update(self.progressbar)


class CurrentActivityWidget(Widget):
    tracking_state = reactive(True)

    def toggle_tracking_state(self):
        self.tracking_state = not self.tracking_state

    def watch_tracking_state(self, is_tracking):
        if is_tracking:
            self.query_one("#tracking_state").update(
                "Tracking sleep and wake states..."
            )
        else:
            self.query_one("#tracking_state").update("Paused tracking states")

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

    def compose(self):
        self.set_interval(1, self.check_sleep)
        yield Header()
        yield Footer()
        yield Container(id="past_periods")
        yield CurrentActivityWidget(id="current_activity")

    def action_toggle_tracking_state(self):
        self.query_one("#current_activity").toggle_tracking_state()

    def check_sleep(self):
        self.query_one("#past_periods").mount(Static("Hi"))


def main():
    app = InsomniaApp()
    app.run()


if __name__ == "__main__":
    main()
