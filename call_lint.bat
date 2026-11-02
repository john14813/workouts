@echo off
cls
rem pylint having issues with 1.8.2, this works at cmd line:
rem pylint --extension-pkg-whitelist=pydantic main.py
rem but better work-around is adding .pylintrc file in home dir, per https://github.com/samuelcolvin/pydantic/issues/1961

rem set PGM=python -m pylint -d C0114, W0611
set PGM=python -m pylint -d missing-class-docstring,missing-module-docstring,unused-import,arguments-renamed

rem loop through py files in each dir
for %%x in (
	config
	utility
	workouts
) do (
	echo "%%x" is the item in loop	
    %PGM% %%x.py  > lint\%%x.txt
    rem line count
    find /c /v "" %%x.py > line_count_%%x.txt
)

rem find "rated" lint\*.txt
echo Pylint Rating Summary
findstr "rated" lint\*.txt | find "rated at 10.00/10"
findstr "rated" lint\*.txt | find /v "rated at 10.00/10"

echo Line Counts
rem find ":" line_count*.txt
powershell -Command "Get-Content line_count*.txt -Tail 1"
del line_count*.txt

rem find /c /v "" *.py
