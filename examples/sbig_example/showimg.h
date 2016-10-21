/****************************************************************************
** $Id: qt/showimg.h   3.3.3   edited May 27 2003 $
**
** Copyright (C) 1992-2000 Trolltech AS.  All rights reserved.
**
** This file is part of an example program for Qt.  This example
** program may be used, distributed and modified without limitation.
**
*****************************************************************************/

#ifndef SHOWIMG_H
#define SHOWIMG_H

#include "csbigimg.h"
#include <qwidget.h>
#include <qimage.h>
#include <qscrollview.h>


class QLabel;
class QMenuBar;
class QPopupMenu;
class MyScroller;
class ImageViewer : public QWidget
{
 Q_OBJECT
public:
 ImageViewer( QWidget *parent=0, const char *name=0, int wFlags=0 );
 ~ImageViewer();
 bool loadImage( const QString& , bool bAutoContrast = FALSE);
 void setImage (CSBIGImg *pImg);
 
protected:
 void resizeEvent( QResizeEvent * );
 void mouseMoveEvent( QMouseEvent * );
 
private:
 void scale();
 
 bool convertEvent( QMouseEvent* e, int& x, int& y);
 CSBIGImg *pSbigImg;
 QString     filename;
 QImage image;   // the loaded image
 QPixmap pm;   // the converted pixmap
 MyScroller *msp;
 
 QMenuBar   *menubar;
 QPopupMenu  *file;
 QPopupMenu   *savepixmap;
 QPopupMenu  *edit;
 QPopupMenu *zoom;
 
 QWidget    *helpmsg;
 QLabel     *status;
 int         sp, sc, zz, ac, iv, si, sii; // menu item ids
 int pickx, picky;
 int imgZoom;
 bool videoInverted;
 void updateStatus();
 void setMenuItemFlags();
 bool  reconvertImage();
 void updateImageBits();
 void deltaZoom();
 void getZoomFactors(int &num, int&den);
 void createPalette();
 
private slots:
 void hFlip();
 void vFlip();
 void rot180();
 void showContrast();
 void showImageInfo();
 void zoom4To1();
 void zoom2To1();
 void zoom1To1();
 void zoom1To2();
 void zoom1To4();
 void autoContrast();
 void inverseVideo();
 
 void newWindow();
 void openFile();
 void savePixmap(int);
 void saveImage();
 void giveHelp();
};

#endif // SHOWIMG_H
