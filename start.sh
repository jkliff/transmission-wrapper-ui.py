# params: [list port], [path to config file]

nohup python transmission-wrapper-ui.py $* > transmission-wrapper-ui.log  &
echo $! > transmission-wrapper-ui.pid
