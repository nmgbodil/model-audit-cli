# 461-repo

This is the codebase for our ECE 461 project

THe phase-1 `run` script that serves as the CLI entrypoint for the project.  
It currently supports three commands required by the specification:

 `./run install`  
  Installs project dependencies and exits with code 0 on success.

 `./run test`  
  Runs the pytest test suite, generates JUnit + coverage XML reports, and prints a summary
  of passed/failed test cases and code coverage percentage.

 `./run urls.txt`  
  Reads a list of URLs and evaluates each. For now, metrics return
  placeholder values, formatted as NDJSON lines. 


## Contributors
* [Noddie Mgbodille](https://github.com/nmgbodil)
* [Will Ott](https://github.com/willott29)
* [Trevor Ju](https://github.com/teajuw)
* [Anna Stark](https://github.com/annastarky)
