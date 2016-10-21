TEMPLATE	= app
LANGUAGE	= C++

CONFIG	+= qt debug warn_on release

LIBS	+= libcfitsio.so

unix:LIBS	+= -lsbigudrv

HEADERS	+= globalT.h \
	imagefip.h \
	showimg.h \
	csbigcam.h \
	csbigimg.h

SOURCES	+= main.cpp \
	csbigcam.cpp \
	csbigimg.cpp \
	imagefip.cpp \
	showimg.cpp

FORMS	= mainform.ui \
	cameracontrol.ui \
	contrastform.ui \
	imageinfoform.ui \
	linksetupform.ui

IMAGES	= images/filenew \
	images/fileopen \
	images/filesave \
	images/print \
	images/undo \
	images/redo \
	images/editcut \
	images/editcopy \
	images/editpaste \
	images/searchfind

unix {
  UI_DIR = .ui
  MOC_DIR = .moc
  OBJECTS_DIR = .obj
}

