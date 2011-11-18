#!/bin/bash
set -o errexit
set -o nounset
set -o verbose

readonly THREADS="$((
    ($(sed -n 's/^processor\s*:\s*\([0-9]\+\)$/\1/p' /proc/cpuinfo \
        | tail -n 1) \
    + 1) * 2
))"

# == Python 3.2 == #
readonly PY_ARCHIVE='python.tar.xz'
# Must NOT contain argument seperator. Glob supported.
readonly PY_DIR='Python-*'
readonly PY_URL='http://python.org/ftp/python/3.2.2/Python-3.2.2.tar.xz'

cd /tmp
wget -O "${PY_ARCHIVE}" "${PY_URL}"
xz --decompress --stdout "${PY_ARCHIVE}" | tar -x
cd ${PY_DIR}
./configure --prefix="${HOME}" --exec-prefix="${HOME}"
make -j "${THREADS}" install

# == Markdown == #
readonly MD_DIR='Python-Markdown'
readonly MD_URL='git://github.com/waylan/Python-Markdown.git'

cd /tmp
git clone "${MD_URL}"
cd "${MD_DIR}"
find -name '*.py' -exec sed -i 's/print\s*\([^(]*\)$/print(\1)/g' {} \;
2to3 --nobackups --write .
python3.2 setup.py install

# == Emailit == #
readonly EI_URL='git://github.com/Man-UP/emailit.git'

cd "${HOME}/public"
git clone "${EI_URL}"

# == Permissions == #
cd
readonly PY_INSTALL_DIR='bin/ include/ lib/ share/ public/'
find ${PY_INSTALL_DIR} -type d -exec chmod 755 {} \;
find ${PY_INSTALL_DIR} -type f -perm -u=r -exec chmod go+r {} \;
find ${PY_INSTALL_DIR} -type f -perm -u=x -exec chmod go+x {} \;


