def run():
    import subprocess

    # build
    subprocess.run(args="poetry build", shell=True)

    # bump the version
    subprocess.run(args="poetry version patch", shell=True)

    # publish
    subprocess.run(args="poetry publish", shell=True)
