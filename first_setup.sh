#!/bin/bash

# Look out for conflicts between git and cmssw
if [ ! -f ${CMSSW_BASE}/src/.git/HEAD ];
then
    echo "You seem to be on Ingrid and CMSSW area appears not to be set up correctly. Check README carefully."
    echo
    return 1
fi
pushd ${CMSSW_BASE}/src/cp3_llbb/GridIn > /dev/null
# configure the origin repository
GITHUBUSERNAME=`git config user.github`
GITHUBUSERREMOTE=`git remote -v | grep upstream | awk '{print $2}' | head -n 1 | cut -d / -f 2`
git remote add origin git@github.com:${GITHUBUSERNAME}/${GITHUBUSERREMOTE}

# Add the remaining forks
git remote add AlexandreMertens https://github.com/AlexandreMertens/GridIn.git
git remote add blinkseb https://github.com/blinkseb/GridIn.git
git remote add BrieucF https://github.com/BrieucF/GridIn.git
git remote add mdelcourt https://github.com/mdelcourt/GridIn.git
git remote add OlivierBondu https://github.com/OlivierBondu/GridIn.git
git remote add pieterdavid https://github.com/pieterdavid/GridIn.git
git remote add sdevissc https://github.com/sdevissc/GridIn.git
git remote add swertz https://github.com/swertz/GridIn.git

pushd ${CMSSW_BASE}/src/cp3_llbb/GridIn/test > /dev/null
ln -s -d ${CMSSW_BASE}/src/cp3_llbb/Datasets/datasets datasets
ln -s -d ${CMSSW_BASE}/src/cp3_llbb/Datasets/analyses analyses
popd > /dev/null
popd > /dev/null
