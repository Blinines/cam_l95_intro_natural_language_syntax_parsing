import subprocess

subprocess.call("pip install benepar[cpu]", shell=True)
subprocess.call("python -m spacy download en", shell=True)