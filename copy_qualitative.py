#!/usr/bin/env python3
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "figures", "access_pictrues")
OUT = os.path.join(HERE, "figures", "qualitative")

METHODS = [
    ("regnerf", "RegNeRF"),
    ("sparsenerf", "SparseNeRF"),
    ("3dgs", "3DGS"),
    ("corgs", "CoR-GS"),
    ("dropgaussian", "DropGaussian"),
    ("d2gs", "D2GS"),
    ("ours", "Ours"),
    ("gt", "GT"),
]


def norm(s):
    return re.sub(r"[\s（）()_-]+", "", s).lower()


def main():
    os.makedirs(OUT, exist_ok=True)
    files = [
        f
        for f in os.listdir(SRC)
        if f.lower().endswith(".png") and "hires" not in f.lower()
    ]
    missed = []
    copied = 0
    for scene in (1, 2, 3):
        cand = [f for f in files if f.startswith(f"{scene}_")]
        for key, label in METHODS:
            hits = [f for f in cand if key in norm(f) or norm(label) in norm(f)]
            if key == "3dgs":
                hits = [f for f in hits if "d2gs" not in norm(f)]
            if key == "ours":
                hits = [f for f in hits if "drop" not in norm(f)]
            if len(hits) != 1:
                missed.append((scene, label, hits, cand))
                print("MISS", scene, label, hits)
                continue
            dst = os.path.join(OUT, f"s{scene}_{key}.png")
            shutil.copy2(os.path.join(SRC, hits[0]), dst)
            print("OK", hits[0], "->", os.path.basename(dst))
            copied += 1
    print("copied", copied)
    print("out_count", len(os.listdir(OUT)))
    if missed:
        print("source files:")
        for f in sorted(files):
            print(" ", f)
        sys.exit(1)


if __name__ == "__main__":
    main()
