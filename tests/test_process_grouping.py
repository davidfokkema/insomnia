from insomnia.tui import ProcessStats


processes = {
    (123, 123456): ProcessStats("foo", 10, 20),
    (456, 494943): ProcessStats("bar", 11, 22),
    (355, 494948): ProcessStats("foo", 9, 9),
}

cumulative = {}
for proc in processes.values():
    cumulative[proc.name] = (
        cumulative.get(proc.name, ProcessStats(proc.name, 0, 0)) + proc
    )
print(cumulative)
