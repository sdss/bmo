/****************************************************************************
** $Id: qt/imagefip.cpp   3.3.3   edited May 27 2003 $
**
** Copyright (C) 1992-2000 Trolltech AS.  All rights reserved.
**
** This file is part of an example program for Qt.  This example
** program may be used, distributed and modified without limitation.
**
*****************************************************************************/

#include "imagefip.h"
#include <qimage.h>

/* XPM */
static const char *image_xpm[] = {
"16 16 6 1",
" 	c None",
".	c #000000",
"+	c #008080",
"@	c #FFFFFF",
"#	c #808000",
"$	c #FF0000",
".........       ",
".@@@@@@@..      ",
".@@@@@@@.@.     ",
".@@@@@@@....    ",
".@@@@@@@@@@.    ",
".@....@@@@@.    ",
".@.##...@@@.    ",
".@.##...@@@.    ",
".@.##.@@@@@.    ",
".@.##.@@$@@.    ",
".@.##.@$$$@.    ",
".@....@@$@@.    ",
".@@@@@@@@@@.    ",
".@@@@@@@@@@.    ",
".@@@@@@@@@@.    ",
"............    "};

ImageIconProvider::ImageIconProvider( QWidget *parent, const char *name ) :
    QFileIconProvider( parent, name ),
    imagepm(image_xpm)
{
    fmts.append("SBIG");
}

ImageIconProvider::~ImageIconProvider()
{
}

const QPixmap * ImageIconProvider::pixmap( const QFileInfo &fi )
{
    QString ext = fi.extension().upper();
    if ( fmts.contains(ext) ) {
 return &imagepm;
    } else {
 return QFileIconProvider::pixmap(fi);
    }
}
