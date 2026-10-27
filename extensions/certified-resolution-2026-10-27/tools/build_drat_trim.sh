#!/usr/bin/env sh
# Fetch and build the EXACT drat-trim revision used for every certified upper
# bound in this extension.  The binary is intentionally not committed.
#
#   pinned commit : 2e3b2dc0ecf938addbd779d42877b6ed69d9a985  (2024-11-25)
#   drat-trim.c   : sha256 d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee
#   binary built here with gcc 16.2.1 : sha256
#                   e17cd2e8de37c4c43bf88360ae3d17740781fe971175bf0b0c935ee3aae4ae19
#                   (a different compiler will give a different binary hash;
#                    the SOURCE hash is the invariant to check)
#
# Why the extra flag: the upstream Makefile uses -std=c99 with no feature-test
# macro, and modern glibc then hides the POSIX declaration of getc_unlocked
# (used at drat-trim.c:986), so the upstream recipe does not compile.
# -D_POSIX_C_SOURCE=200809L exposes the declaration WITHOUT editing the source
# and without changing the language standard.
set -e
PIN=2e3b2dc0ecf938addbd779d42877b6ed69d9a985
DIR="$(cd "$(dirname "$0")" && pwd)/drat-trim"
if [ ! -d "$DIR/.git" ]; then
  git clone https://github.com/marijnheule/drat-trim.git "$DIR"
fi
cd "$DIR"
git fetch --quiet origin
git checkout --quiet "$PIN"
WANT=d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee
GOT=$(sha256sum drat-trim.c | cut -d' ' -f1)
if [ "$WANT" != "$GOT" ]; then
  echo "drat-trim.c hash mismatch: expected $WANT got $GOT" >&2
  exit 1
fi
gcc drat-trim.c -std=c99 -D_POSIX_C_SOURCE=200809L -O2 -o drat-trim
echo "built $DIR/drat-trim"
echo "source sha256 $GOT  (pinned revision verified)"
echo "binary sha256 $(sha256sum drat-trim | cut -d' ' -f1)  (compiler-dependent)"
