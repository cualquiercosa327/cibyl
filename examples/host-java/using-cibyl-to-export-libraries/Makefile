######################################################################
##
## Copyright (C) 2005,  Blekinge Institute of Technology
##
## Filename:      Makefile
## Author:        Simon Kagstrom <simon.kagstrom@gmail.com>
## Description:   Makefile
##
## $Id: Makefile 13560 2007-02-10 07:39:53Z ska $
##
######################################################################
SUBDIRS = c
RESOURCES=
TARGET   =

CIBYL_SYSCALL_SETS ?= ansi
JAVA_OPTS=

all: tmpclasses/LibraryWrapper.java

include $(CIBYL_BASE)/build/Rules-java.mk

tmpclasses/StandaloneMain.java: StandaloneMain.java
	cp $< $@
tmpclasses/LibraryWrapper.java: LibraryWrapper.java
	cp $< $@