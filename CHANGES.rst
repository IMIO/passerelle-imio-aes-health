Changelog
=========

0.1.17
------------------
- [TELE-1306] remove passerelle.compat [nhi]

0.1.16
------------------
- [TELE-1125] use iateleservicesCreateDeb pipeline function [nhi]
- [TELE-1144] set install path in jenkins params [nhi]
- set author to iA.Teleservices team [nhi]

0.1.15
------------------
- [TELE-1119] add -k to avoid SSL error following the Infra advice about that
  [dmshd]

0.1.14
------------------
- clean workspace on successful build
  [nhi]

0.1.13
------------------
- split fpm on multiple lines
  [nhi]

0.1.12
------------------
- fix quotes
  [nhi]

0.1.11
------------------

- use no-auto-depends
  [nhi]

0.1.10
------------------

- set django requirement version from 1.11 to 2.3
- set dependencies to false in fpm command
  [nhi]

0.1.9
------------------

- set django requirement version from 1:1.11 to 2:2.3
  [nhi]

0.1.8
------------------

- set django requirement version from 1.11 to 2.3
- set epoch=1
  [nhi]

0.1.7
------------------

- set django requirement version from 1.11.0 to 2.3.30
  [nhi]

0.1.6
------------------

- set django requirement version at 1.1.11 to 1.2.3
  [nhi]

0.1.5
------------------

- set django requirement version at 1.11 to 2.3
  [nhi]

0.1.4
------------------

- remove django 2.3 as max dependency
  [nhi]

0.1.3
------------------

- replace python3-django from dependencies by django
  [nhi]

0.1.2
------------------

- update versionning scheme to remove letters
  [nhi]

0.1.1n
------------------

- fix Jenkinsfile's fpm command
  [nhi]

0.1.1m
------------------

- adapt Jenkinsfile's fpm command because it add python- to dependencies
  [nhi]

0.1.1l
------------------

- set depends to python3-django
  [nhi]

0.1.1k
------------------

- declare only python3 as programming language
- re set django only as required
  [nhi]

0.1.1j
------------------

- set python3-django as required
  [nhi]

0.1.1i
------------------

- remove python 3.7.3 as required
- set django version between 1.11 and 2.2 as required
- fix typo in changelog
  [nhi]

0.1.1h
------------------

- set python 3.7.3 as required
  [nhi]

0.1.1g
------------------

- set django 2.2 as required
  [nhi]

0.1.1f
------------------

- use commune's site instead of school's one
- use python 3.7.3 only
  [nhi]

0.1.1e
------------------

- do not request healthsheet from AES if no child id given
  [nhi]

0.1.1d
------------------

- merge master and buster
  [nhi]

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
