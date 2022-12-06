import time

import humanize
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn

DELAY = 1

print("Tracking sleeps...")

sleeping = awake = 0
t_last_wake = t_prev = time.time()
with Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    refresh_per_second=1 / DELAY,
) as progress:
    activity = progress.add_task("[blue]Sleepiness", total=1)
    while True:
        time.sleep(DELAY)
        t = time.time()
        if t - t_prev > 2 * DELAY:
            print(
                f"I was active for {humanize.precisedelta(t_prev - t_last_wake)} until {time.ctime(t_prev)}"
            )
            t_last_wake = t
            print(
                f"Woke up at {time.ctime(t)}; I was sleeping for {humanize.naturaldelta(t - t_prev)}"
            )
            sleeping += t - t_prev
        else:
            awake += t - t_prev
        t_prev = t
        progress.update(activity, completed=sleeping / (awake + sleeping))
