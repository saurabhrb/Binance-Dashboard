git submodule update --init --recursive
git config --global user.email "saurabhbadenkalat@gmail.com"
git config --global user.name "saurabhrb"
git fetch origin

cd Binance_Futures_python
git add -A . && git stash && git stash pop && git clean -fx
git fetch origin
git checkout main
git reset origin/main --hard
cd ..

rm -rf binance_f
ln -s Binance_Futures_python/binance_f binance_f

echo "Done"
