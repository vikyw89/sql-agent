def run():
    import subprocess

    # build, bump and publish
    subprocess.run(args="poetry version patch && poetry publish --build", shell=True)