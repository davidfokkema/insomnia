from textual.app import App
from textual.containers import Container
from textual.widgets import Header, Footer, Static


class CurrentActivityWidget(Static):
    tracking_state = True

    def on_mount(self):
        self.update_widget()

    def toggle_tracking_state(self):
        self.tracking_state = not self.tracking_state
        self.update_widget()

    def update_widget(self):
        if self.tracking_state:
            self.update("Tracking sleep and wake states...")
        else:
            self.update("Paused tracking states")


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
