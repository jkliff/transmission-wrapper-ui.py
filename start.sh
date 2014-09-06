# params: [list port], [path to config file]
SCRIPT_PATH=$(readlink -f $0)
BASE=$(dirname "$SCRIPT_PATH")

cd $BASE

echo starting transmission-wrapper-ui.py
nohup python src/transmission-wrapper-ui.py $* > transmission-wrapper-ui.log  &
echo $! > transmission-wrapper-ui.pid
