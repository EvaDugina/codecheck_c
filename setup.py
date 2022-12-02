from setuptools import setup, find_packages

with open("README.md", "r") as readme_fp:
    readme = readme_fp.read()

setup(name="codecheck",
      author="Igor Chernousov",
      author_email="chernousov.id@gmail.com",
      version="0.0.1",
      description="Utility for automatic code check with various tools",
      long_description=readme,
      long_description_content_type="text/markdown",
      url="https://vega.fcyb.mirea.ru/gitlab/chernousov/codecheck",
      packages=["codecheck"],
      entry_points={"console_scripts" : [
          "codecheck = codecheck.__main__:main"]},
)