def run():
    import subprocess

    # bump the version
    subprocess.run(args="poetry version patch", shell=True)

    # publish
    subprocess.run(args="poetry publish", shell=True)
