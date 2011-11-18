#!/bin/bash
set -o errexit
set -o nounset
set -o verbose

# Must NOT contain argument seperator. Glob supported.
readonly THREADS="$((
    ($(sed -n 's/^processor\s*:\s*\([0-9]\+\)$/\1/p' /proc/cpuinfo \
        | tail -n 1) \
    + 1) * 2
))"

# == Python 3.2 == #
readonly PY_ARCHIVE='python.tar.xz'
readonly PY_DIR='Python-*'
readonly PY_URL='http://python.org/ftp/python/3.2.2/Python-3.2.2.tar.xz'

cd /tmp
wget -O "${ARCHIVE}" "${URL}"
xz --decompress --stdout "${ARCHIVE}" | tar -x
cd ${DIR}
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
readonly EI_URL='git//github.com/Man-UP/emailit.git'

cd "${HOME}"
git clone "${EI_URL}"

