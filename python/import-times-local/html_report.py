from argparse import ArgumentParser
from collections import deque
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


microseconds = int


@dataclass
class Import:
    module: str
    self: microseconds
    cumulative: microseconds
    level: int
    dependencies: list["Import"] = field(default_factory=list)

    @classmethod
    def parse(cls, line: str) -> "Import":
        data = line[len("import time:") :]
        self, cumulative, text = data.split(" | ", 2)
        n = len(text)
        name = text.lstrip()
        level = (n - len(name)) // 2
        return cls(name, int(self), int(cumulative), level)

    def html(self, total):
        output = f"""
            <details style="padding-left: 1em">
                <summary>
                    <progress value="{self.cumulative}" max="{total}" style="width: 10em;"></progress>
                    <code>{self.module}</code>
                    <span style="color: #888; font-size:small; font-family: arial;">{self.cumulative / 1000:.3f} ms</span>
                    <span style="color: #888; font-size:small; font-family: arial;">({self.cumulative / total:.2%})</span>
                    </summary>
        """

        for dep in sorted(self.dependencies, key=lambda dep: dep.cumulative, reverse=True):
            output += dep.html(total)
        output += "</details>\n"
        return output


def parse_import_time_report(filename: Path) -> Import:
    root = Import("root", 0, 0, level=-1)
    stack = deque([root])
    for line in filename.read_text().splitlines()[::-1][:-1]:
        if not line.startswith("import time:"):
            continue
        import_ = Import.parse(line)
        while stack[-1].level >= import_.level:
            stack.pop()

        stack[-1].dependencies.append(import_)
        stack.append(import_)
    root.cumulative = sum(dep.cumulative for dep in root.dependencies)
    return root


def main():
    argp = ArgumentParser()

    argp.add_argument("filename", type=Path)

    args = argp.parse_args()

    root = parse_import_time_report(args.filename)

    print(root.html(root.cumulative))


if __name__ == "__main__":
    main()
