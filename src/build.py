#!/usr/bin/env python3

import sys
import os
from uhigh import UHighCompiler

def build_project(project_dir: str):
    compiler = UHighCompiler()
    output = []

    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".uh"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    source = f.read()
                compiled = compiler.compile(source, root)
                output.append(compiled)

    output_file = os.path.join(project_dir, "output.masm")
    with open(output_file, 'w') as f:
        f.write('\n'.join(output))

    print(f"Build complete. Output written to {output_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: build.py <project_directory>")
        sys.exit(1)

    project_dir = sys.argv[1]
    build_project(project_dir)

if __name__ == "__main__":
    main()
