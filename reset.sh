# remove folders
rm -rf ./ckpt &&
rm -rf ./skill_library/skill &&
rm -rf ./voyager/web/env/browser/workspace &&
mkdir ./voyager/web/env/browser/workspace &&
rm -rf ./voyager/code_interpreter/env/python/workspace &&
mkdir ./voyager/code_interpreter/env/python/workspace &&
python start.py
