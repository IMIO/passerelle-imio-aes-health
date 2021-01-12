Changelog
=========

0.1.1c
------------------

- init buster branch that will become master later and adapt Jenkinsfile for Nexus (Debian Buster packages)
  [dmuyshond]
- rename tst_connection as test_connection
- [MPP-37] add docstrings
- [MPPMSGA-168] add method to get healthsheet's options
  [nhi]

0.1.1b
------------------

- Added some fixes for python3
  [boulch]

0.1.1a
------------------

- Adapt Jenkinsfile to install package python3/dist-package instead of python2

0.0.3a
------------------
- change required package to python3-passerelle instead of passerelle
- also change  programming language since it is now Python 3

It has been asked by Entr'Ouvert : https://dev.entrouvert.org/issues/43958#note-2
Without that, the jenkins build is failing cause python-passerelle is not available anymore. Now it is python3-passerelle

0.0.2a
------------------

- Fix imports for python3 AND python2 compatibily.

0.0.1a
------------------

- firsts commits
