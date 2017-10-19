set curdir=""
for %%i in ("%~dp0\.") do (
  set curdir=%%~ni
)
cd ..
packpanda --dir %curdir% --name Arrival --version 1.0 --bam --pyc --fast
pause