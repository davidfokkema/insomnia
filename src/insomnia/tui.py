from textual.app import App
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer, Header, Static


class CurrentActivityWidget(Widget):
    tracking_state = reactive(True)

    def toggle_tracking_state(self):
        self.tracking_state = not self.tracking_state

    def render(self):
        if self.tracking_state:
            return "Tracking sleep and wake states..."
        else:
            return "Paused tracking states"


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
        yield CurrentActivityWidget(id="current")

    def action_toggle_tracking_state(self):
        self.query_one("#current").toggle_tracking_state()

    def check_sleep(self):
        self.query_one("#past_periods").mount(Static("Hi"))


def main():
    app = InsomniaApp()
    app.run()


if __name__ == "__main__":
    main()
