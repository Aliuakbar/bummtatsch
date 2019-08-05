import random
import subprocess

"""
TODO:
- distributions
- proximity
- tonleitern?
"""
ly_file = "notes.ly"
pdf_file = "notes.pdf"
pdf_viewer = "zathura"

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
    print(f"Using notes: {notes}")
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


def create_lilypond_file(key="c", modifier="major", time_signature=(4,
                                                                           4),
                         n=16, octave_range=(1, 2), note_lengths=(0, 4)):
    """
    key: e.g "c", "g", "fis", "as", default to "c"
    modifier: "major" or "minor", defaults to "major"
    time_signature: takt, (3, 4) <-> 3 / 4
    n: # takte (oder wiemer demm au seit, defaults to 16
    octave_range: (1, 2) <-> oktaven mit c' und c'' (absolut)
    note_lengths: (longest, shortest) tone, as power of 2
                         defaults to (0, 4) <-> 1, 16
    """
    time1, time2 = time_signature
    print("Composing...")
    notes = random_compose(n, time1 / time2, note_lengths, octave_range)
    print(f"Writing to {ly_file} ...")
    with open(ly_file, "w") as file:
        formatted = template.format(key=key, modifier=modifier, time1=time1,
                                    time2=time2, notes=notes,)
        file.write(formatted)
    print("Success")

def main():
    print("Drinking coffee...")
    create_lilypond_file("ges", "major", (11, 16), 32, (1, 2), (1, 5))
    # compile with lilypond to pdf
    print("Compiling to PDF...")
    process = subprocess.Popen(["lilypond", "-s", ly_file], stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(error)
    print(f"Created {pdf_file}")
    # open up the pdf with an pdf viewer if supplied
    if pdf_viewer:
        print("Opening pdf...")
        process = subprocess.Popen([pdf_viewer, pdf_file], stdout=subprocess.PIPE)
        output, error = process.communicate()
    else:
        print("No pdf viewer supplied")

if __name__ == "__main__":
    main()
