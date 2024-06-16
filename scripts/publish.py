def run():
    import subprocess

    # build, bump and publish
    subprocess.run(args="poetry publish --build", shell=True)