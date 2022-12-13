from textual.app import App
from textual.containers import Container
from textual.widgets import Header, Footer, Static


class GoodWidget(Static):
    def compose(self):
        yield Static("Works")


class ProblemWidget(Static):
    def on_mount(self):
        self.update("Breaks in timer")


class ScrollApp(App):

    BINDINGS = [
        ("g", "add_good_widget", "Good"),
        ("p", "add_problem_widget", "Problem"),
        ("ctrl+g", "start_good_timer", "Start good timer"),
        ("ctrl+p", "start_problem_timer", "Start problem timer"),
        ("r", "reset", "Reset"),
        ("q", "quit", "Quit"),
    ]

    def compose(self):
        """Called to add widgets to the app."""
        self.good_timer = self.set_interval(
            0.2, self.action_add_good_widget, pause=True
        )
        self.problem_timer = self.set_interval(
            0.2, self.action_add_problem_widget, pause=True
        )
        yield Header()
        yield Footer()
        yield Container(id="widgets")

    def action_add_good_widget(self):
        new_widget = GoodWidget()
        self.query_one("#widgets").mount(new_widget)
        new_widget.scroll_visible()

    def action_add_problem_widget(self):
        new_widget = ProblemWidget()
        self.query_one("#widgets").mount(new_widget)
        new_widget.scroll_visible()

    def action_start_good_timer(self):
        self.good_timer.resume()

    def action_start_problem_timer(self):
        self.problem_timer.resume()

    def action_reset(self):
        self.good_timer.pause()
        self.problem_timer.pause()
        for widget in reversed(self.query_one("#widgets").children):
            widget.remove()


if __name__ == "__main__":
    app = ScrollApp()
    app.run()
