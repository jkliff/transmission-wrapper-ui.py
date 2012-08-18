rm -rf target
mkdir target
cp start.sh stop.sh src/*py target
TARGET=transmission-fe.py-`date +%F%z`
tar -czf $TARGET.tar.gz target

