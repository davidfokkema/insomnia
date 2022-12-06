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

    BINDINGS = [("t", "toggle_tracking_state()", "Toggle tracking")]

    def compose(self):
        self.current_activity_widget = CurrentActivityWidget(id="current")
        yield Header()
        yield Footer()
        yield Container(id="past_periods")
        yield self.current_activity_widget

    def action_toggle_tracking_state(self):
        self.current_activity_widget.toggle_tracking_state()


def main():
    app = InsomniaApp()
    app.run()


if __name__ == "__main__":
    main()
