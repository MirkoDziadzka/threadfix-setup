#!/bin/bash

ROOT=$(cd $(dirname "$0") && pwd)
#HOME="${ROOT}"
CACHE="${ROOT}/cache"
BUILD="${ROOT}/build"

#
# preparation
#

mkdir -p "${CACHE}"
mkdir -p "${BUILD}"
#
# install maven
#
MAVENREPO="http://artfiles.org/apache.org/maven/maven-3/3.1.1/binaries/apache-maven-3.1.1-bin.zip"
MAVENDIR="${BUILD}/apache-maven-3.1.1"
MAVENZIP="${CACHE}/apache-maven-3.1.1-bin.zip"

if [ ! -f "${MAVENZIP}" ] ; then 
    curl ${MAVENREPO} -o "${MAVENZIP}"
else
    echo using cached file "${MAVENZIP}"
fi

rm -rf "${MAVENDIR}"
unzip -q "${MAVENZIP}" -d "${BUILD}"
test -d "${MAVENDIR}" || exit 1

export M2_HOME="${MAVENDIR}"
export M2=$M2_HOME/bin

PATH=${MS}:$PATH

#
# Download threadfix
#

THREADFIX_SOURCE="${CACHE}/$threadfix-source"
THREADFIX_WAR="${BUILD}/threadfix.war"
THREADFIX_INSTALL_DIR="${ROOT}/Threadfix"
THREADFIX_INSTALL_ZIP="${CACHE}/ThreadFix_2.1M2.zip"

rm -f "${THREADFIX_WAR}"

if [ -d "${THREADFIX_SOURCE}" ] ; then
    (cd "${THREADFIX_SOURCE}" && git checkout riverbed-waf && git pull)
else
    git clone -b riverbed-waf --single-branch https://github.com/MirkoDziadzka/threadfix.git "${THREADFIX_SOURCE}"
fi
test -d "${THREADFIX_SOURCE}" || exit 1

(cd ${THREADFIX_SOURCE} && mvn clean package &&  mv "threadfix-main/target/threadfix-2.1-SNAPSHOT.war" "${THREADFIX_WAR}")


#
# unzip ThreadFix community distribution
#

rm -rf "${THREADFIX_INSTALL_DIR}"
if [ ! -f "${THREADFIX_INSTALL_ZIP}" ] ; then
    if [ -z "${EXT_DEP_CACHE_DIR}" ] ; then
        (svn update "${EXT_DEP_CACHE_DIR}" && cp -v "${EXT_DEP_CACHE_DIR}/ThreadFix_2.1M2.zip" "${THREADFIX_INSTALL_ZIP}")
    else
        svn export http://svn.r.lab.nbttech.com/svn/wod/external/ThreadFix_2.1M2.zip "${THREADFIX_INSTALL_ZIP}"
    fi
fi

test -f "${THREADFIX_INSTALL_ZIP}" || exit 1
unzip -q "${THREADFIX_INSTALL_ZIP}" -d "${ROOT}"
test -d "${THREADFIX_INSTALL_DIR}" || exit 1

cp -v "${THREADFIX_WAR}" "${THREADFIX_INSTALL_DIR}"/tomcat/webapps/threadfix.war

exit 0

