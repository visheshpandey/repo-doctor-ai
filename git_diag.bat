@echo off
echo Running git status... > git_diag.txt
git status >> git_diag.txt 2>&1
echo. >> git_diag.txt
echo Running git add... >> git_diag.txt
git add --all >> git_diag.txt 2>&1
echo. >> git_diag.txt
echo Running git commit... >> git_diag.txt
git commit -m "Automated commit including frontend" >> git_diag.txt 2>&1
echo. >> git_diag.txt
echo Running git push... >> git_diag.txt
git push origin main >> git_diag.txt 2>&1
echo. >> git_diag.txt
echo Done! >> git_diag.txt
