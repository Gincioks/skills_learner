# remove folders
rm -rf ./ckpt &&
rm -rf ./skill_library/skill &&
rm -rf ./voyager/web/env/browser/workspace &&
mkdir ./voyager/web/env/browser/workspace &&
rm -rf ./python_env/workspace &&
mkdir ./python_env/workspace &&
python start.py
