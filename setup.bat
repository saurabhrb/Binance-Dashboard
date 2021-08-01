git submodule update --init --recursive
git config --global user.email "saurabhbadenkalat@gmail.com"
git config --global user.name "saurabhrb"
git fetch origin

cd Binance_Futures_python
git add -A . && git stash && git stash pop && git clean -fx
git fetch origin
git checkout main
cd ..

rmdir binance_f
mklink binance_f Binance_Futures_python\binance_f