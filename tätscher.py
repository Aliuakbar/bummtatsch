import random
import subprocess
import click

"""
TODO:
- distributions
- proximity
- tonleitern?
"""
ly_file = "notes.ly"
pdf_file = "notes.pdf"

REST_PROB = 6 # 1/x probability
DOT_PROB = 3

# simple lilypond template
template = """\\version "2.14.1"
\\score {{
  \\new Staff {{
    \\clef treble
    \\key {key} \\{modifier}
    \\time {time1}/{time2}
    {notes}

   }}
}}
"""

def random_compose(n , time, note_lengths, octave_range):
    # randomly composes a melody with given conditions
    result = []
    notes = "cdefgab"
    click.echo(f"Using notes: {notes}")
    lengths = [2**i for i in range(note_lengths[0], note_lengths[1] + 1)]
    for _ in range(n):
        current = time
        previous = []
        while current > 0:
            if previous and previous[2] == ".":
                l = int(previous[1]) * 2
            else:
                l = random.choice(list(filter(lambda x: 1/x <= current, lengths)))
                if 1 / l * 1.5 <= current and l != 2**note_lengths[0]:
                    if random.randint(1, DOT_PROB) == 1:
                        m = "."
            # rests can't follow each other
            if previous and previous[0] != "r" and random.randint(1, REST_PROB) == 1:
                v = "r"
            else:
                o0, o1 = octave_range
                v = random.choice(notes) + "'" * random.randint(o0, o1)
            m = ""
            current -= 1 / l
            if m:
                current -= 1 / l * 1 / 2
            d = l * 1.5 if m else l
            l = str(l)
            result.append(v + l + m)
            previous = [v , l , m]
    return " ".join(result)


def create_lilypond_file(key, modifier, time_signature, n, octave_range, note_lengths):
    time1, time2 = time_signature
    click.echo("Composing...")
    notes = random_compose(n, time1 / time2, note_lengths, octave_range)
    click.echo(f"Writing to {ly_file} ...")
    with open(ly_file, "w") as file:
        formatted = template.format(key=key, modifier=modifier, time1=time1,
                                    time2=time2, notes=notes,)
        file.write(formatted)
    click.echo("Success")

@click.command()
@click.option("-k", '--key', default='c', help="e.g 'c', 'g', 'fis', 'as'")
@click.option("--minor", "modifier", flag_value="minor")
@click.option("--major", "modifier", flag_value="major", default=True)
@click.option("-t", "--time-signature", default=(4, 4), help='takt, (3, 4) <-> 3 / 4')
@click.option("-n", default=16, help='# takte (oder wiemer demm au seit')
@click.option("-o", "--octave-range", default=(1, 2), help="(1, 2) <-> oktaven mit c' und c'' (absolut)")
@click.option("-l", "--note-lengths", default=(0, 4), help="(longest, shortest) tone, as power of 2")
def bumm(*args, **kwargs):
    click.echo("Drinking coffee...")
    create_lilypond_file(*args, **kwargs)
    # compile with lilypond to pdf
    click.echo("Compiling to PDF...")
    process = subprocess.Popen(["lilypond", "-s", ly_file], stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(error)
    click.echo(f"Created {pdf_file}")
    # open up the pdf with an pdf viewer if supplied
    click.echo("Opening pdf...")
    click.launch(pdf_file)

if __name__ == "__main__":
    bumm()
