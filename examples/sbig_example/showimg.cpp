/****************************************************************************
** $Id: qt/showimg.cpp   3.3.3   edited May 27 2003 $
**
** Copyright (C) 1992-2000 Trolltech AS.  All rights reserved.
**
** This file is part of an example program for Qt.  This example
** program may be used, distributed and modified without limitation.
**
*****************************************************************************/

#include "showimg.h"
#include "contrastform.h"
#include "imageinfoform.h"
#include <qmenubar.h>
#include <qfiledialog.h>
#include <qmessagebox.h>
#include <qpopupmenu.h>
#include <qlabel.h>
#include <qpainter.h>
#include <qapplication.h>
#include <qclipboard.h>

#define MIN_RANGE 64

typedef enum { ZOOM_1TO4, ZOOM_1TO2, ZOOM_1TO1,
			   ZOOM_2TO1, ZOOM_4TO1} IMAGE_ZOOM;

class MyScroller:public QScrollView{
public:
	MyScroller(QWidget* parent):
			QScrollView(parent, "myscroller", WStaticContents)
	{
		resizeContents(0, 0);
		ppm = NULL;
	}
	
	void changePixmap(QPixmap *pm)
	{
		ppm = pm;
		if ( ppm != NULL )
			resizeContents(pm->width(), pm->height());
		updateContents();
	}
protected:
	void drawContents(QPainter* p, int cx, int cy, int cw, int ch)
	{
		if (ppm != NULL &&  ppm->size() != QSize( 0, 0 ) )   // is an image loaded?
			p->drawPixmap(0, 0, *ppm);
		cx = cy = cw = ch = 0; // so don't get compiler warning
	}
	
	QPixmap *ppm;
};

/*
  In the constructor, we just pass the standard parameters on to
  QWidget.
  
  The menu uses a single slot to simplify the process of adding
  more items to the options menu.
*/
ImageViewer::ImageViewer( QWidget *parent, const char *name, int wFlags )
	: QWidget( parent, name, wFlags ),
	helpmsg( 0 )
{
	pickx = -1;
	picky = -1;
	pSbigImg = new CSBIGImg;
	
	menubar = new QMenuBar(this);
	menubar->setSeparator( QMenuBar::InWindowsStyle );
	
	QStrList fmt = QImage::outputFormats();
	savepixmap = new QPopupMenu( menubar );
	for (const char* f = fmt.first(); f; f = fmt.next())
		savepixmap->insertItem( f );
	connect( savepixmap, SIGNAL(activated(int)), this, SLOT(savePixmap(int)) );
	
	file = new QPopupMenu( menubar );
	menubar->insertItem( "&File", file );
	file->insertItem( "&New window", this,  SLOT(newWindow()), CTRL+Key_N );
	file->insertItem( "&Open...", this,  SLOT(openFile()), CTRL+Key_O );
	si = file->insertItem( "Save as...", this, SLOT(saveImage()), CTRL+Key_S );
	sp = file->insertItem( "Save pixmap", savepixmap );
	file->insertSeparator();
	file->insertItem( "Close", this,  SLOT(close()) );
	
	zoom = new QPopupMenu(menubar);
	zoom->insertItem("Zoom out 1:4", this, SLOT(zoom1To4()));
	zoom->insertItem("Zoom out 1:2", this, SLOT(zoom1To2()));
	zoom->insertItem("Show at 1:1", this, SLOT(zoom1To1()));
	zoom->insertItem("Zoom in 2:1", this, SLOT(zoom2To1()));
	zoom->insertItem("Zoom in 4:1", this, SLOT(zoom4To1()));
	
	edit =  new QPopupMenu( menubar );
	menubar->insertItem( "&Edit", edit );
	edit->insertItem("&Horizontal flip", this, SLOT(hFlip()), ALT+Key_H);
	edit->insertItem("&Vertical flip", this, SLOT(vFlip()), ALT+Key_V);
	edit->insertItem("&Rotate 180", this, SLOT(rot180()), ALT+Key_R);
	edit->insertSeparator();
	ac = edit->insertItem("&Auto Contrast", this, SLOT(autoContrast()), ALT+Key_A);
	sc = edit->insertItem("&Manual Contrast...", this, SLOT(showContrast()), ALT+Key_M);
	iv = edit->insertItem("Invert &Video...", this, SLOT(inverseVideo()), ALT+Key_V);
	zz = edit->insertItem("Zoom", zoom);
	edit->insertSeparator();
	sii = edit->insertItem("Show &Image Info...", this, SLOT(showImageInfo()),ALT+Key_I);
	setMenuItemFlags();
	
	menubar->insertSeparator();
	
	QPopupMenu* help = new QPopupMenu( menubar );
	menubar->insertItem( "&Help", help );
	help->insertItem( "Help!", this, SLOT(giveHelp()), CTRL+Key_H );
	
	status = new QLabel(this);
	status->setFrameStyle( QFrame::WinPanel | QFrame::Sunken );
	status->setFixedHeight( fontMetrics().height() + 4 );
	
	setMouseTracking( TRUE );
	
	msp = new MyScroller(this);
}

ImageViewer::~ImageViewer()
{
	if ( pSbigImg != NULL )
		delete pSbigImg;
}

void ImageViewer::setImage(CSBIGImg *pImg)
{
	pSbigImg = pImg;
	loadImage(QString::null, TRUE);
}

/*
  Set the menu items to reflect the current status.
*/
void ImageViewer::setMenuItemFlags()
{
	bool valid_image = pm.size() != QSize( 0, 0 );
	file->setItemEnabled( sp, valid_image );
	file->setItemEnabled( si, valid_image );
	edit->setItemEnabled( sc, valid_image );
	edit->setItemEnabled( ac, valid_image );
	edit->setItemEnabled( iv, valid_image );
	edit->setItemEnabled( zz, valid_image );
	edit->setItemEnabled(sii, valid_image);
}

void ImageViewer::updateStatus()
{
	if ( pm.size() == QSize( 0, 0 ) ) {
		if ( !filename.isEmpty() )
			status->setText("Could not load image");
		else
			status->setText("No image - select Open from File menu.");
	} else {
		QString message, moremsg;
		int num, den;
		getZoomFactors(num, den);
		message.sprintf("Zoom %d:%d", num, den);
		if (image.valid(pickx, picky)) {
			unsigned short vid, *pVid = pSbigImg->GetImagePointer();
			vid = pVid[(long)picky*pSbigImg->GetWidth()+pickx];
			moremsg.sprintf(" Pixel(%d,%d)=%u ADU", pickx+1, picky+1, vid);
			message += moremsg;
		}
		status->setText(message);
	}
}

/*
  This function saves the converted image.
*/
void ImageViewer::savePixmap( int item )
{
	const char* fmt = savepixmap->text(item);
	QString savefilename = QFileDialog::getSaveFileName(QString::null, QString::null, this, filename);
	if ( !savefilename.isEmpty() )
		if ( !pm.save( savefilename, fmt ) )
			QMessageBox::warning( this, "Save failed", "Error saving file" );
}

void ImageViewer::saveImage()
{
	QString selFilter;
	SBIG_IMAGE_FORMAT sbigIF;
	QString savefilename = QFileDialog::getSaveFileName(QString::null, 
              "SBIG Images (*.sbig);;FITS Images (*.fits)", 
              this, filename,
              QString::null,
              &selFilter);
	if ( !savefilename.isEmpty() ) {
		if ( selFilter.find("FITS") != -1 ) {
			sbigIF = SBIF_FITS;
			if ( savefilename.find(".") == - 1)
				savefilename += ".fits";
		} else {
			sbigIF = SBIF_COMPRESSED;
			if ( savefilename.find(".") == - 1)
				savefilename += ".sbig";
		}
		if ( pSbigImg->SaveImage( savefilename, sbigIF)  != SBFE_NO_ERROR )
			QMessageBox::warning( this, "Save failed", "Error saving SBIG format file." );
		else
			setCaption(savefilename);
	}
}

void ImageViewer::newWindow()
{
 ImageViewer* that = new ImageViewer(0, "new window", WDestructiveClose);
 that->setCaption("SBIG Image Viewer");
 that->show();
}

/*
  This function is the slot for processing the Open menu item.
*/
void ImageViewer::openFile()
{
 QString msg;
 QString newfilename = QFileDialog::getOpenFileName( "/home/matt/images",
														"SBIG Images (*.sbig);;All files (*.*)",
														this );
	
	if ( !newfilename.isEmpty() ) {
		if ( !loadImage(newfilename) )
			status->setText("Error opening SBIG Format Image");
	}
}

bool ImageViewer::loadImage(const QString& fileName, bool bAutoContrast /* = FALSE */)
{
	bool ok = TRUE;
	int dim;
	
	QApplication::setOverrideCursor( waitCursor ); // this might take time
	if ( fileName.length() != 0 ) {
		filename = fileName;
		if ( pSbigImg->OpenImage(fileName) != SBFE_NO_ERROR )
			ok = FALSE;
	}
	image.reset();
	if ( ok && image.create(pSbigImg->GetWidth(), pSbigImg->GetHeight(), 8) ) {
		image.setNumColors(256);
		dim = pSbigImg->GetWidth();
		if ( pSbigImg->GetHeight() > dim )
			dim = pSbigImg->GetHeight();
		if ( dim <= 32 )
			imgZoom = ZOOM_4TO1;
		else if ( dim <= 128 )
			imgZoom = ZOOM_2TO1;
		else if ( dim <= 768 )
			imgZoom = ZOOM_1TO1;
		else if ( dim <= 1536 )
			imgZoom = ZOOM_1TO2;
		else
			imgZoom = ZOOM_1TO4;
		pickx = -1;
		if ( bAutoContrast )
			pSbigImg->AutoBackgroundAndRange();
		videoInverted = FALSE;
		createPalette();
		reconvertImage();
		setCaption( filename );
		int num, den, h, w;
		int mbh, sh;
		getZoomFactors(num, den);
		w = (pSbigImg->GetWidth() * num)/den;
		h = (pSbigImg->GetHeight() * num)/den;
		mbh = menubar->heightForWidth( w );
		sh = status->height();
		resize( w+4, h+sh+mbh+4 );    // we resize to fit image
	}
	updateStatus();
	setMenuItemFlags();
	QApplication::restoreOverrideCursor(); // restore original cursor
	return ok;
}

void ImageViewer::updateImageBits()
{
	int i, j;
	unsigned char *pDest;
	unsigned short *pVid;
	long back, range, vid;
	
	pDest = image.bits();
	back = pSbigImg->GetBackground();
	range = pSbigImg->GetRange();
	if ( range < MIN_RANGE )
		range = MIN_RANGE;
	pVid = pSbigImg->GetImagePointer();
	for(i=0; i<pSbigImg->GetHeight(); i++) {
		for(j=0; j<pSbigImg->GetWidth(); j++) {
			vid = *pVid++;
			vid -= back;
			if ( vid < 0 )
				vid = 0;
			else if ( vid >= range )
				vid = 255;
			else
				vid = (vid * 255)/range;
			pDest[j] = vid;
		}
		pDest += image.bytesPerLine();
	}
}

bool ImageViewer::reconvertImage()
{
	bool success = FALSE;
	
	if ( image.isNull() ) return FALSE;
	
	QApplication::setOverrideCursor( waitCursor ); // this might take time
	updateImageBits();
	if ( pm.convertFromImage(image, 0) )
	{
		scale();
		success = TRUE;    // load successful
	} else {
		pm.resize(0,0);    // couldn't load image
	}
	msp->changePixmap(&pm);
	updateStatus();
	setMenuItemFlags();
	QApplication::restoreOverrideCursor(); // restore original cursor
	return success;    // TRUE if loaded OK
}

/*
  This functions scales the pixmap in the member variable "pm" based
  on the imgZoom member var puts the resulting pixmap in the member variable "pmScaled".
*/

void ImageViewer::scale()
{
	QWMatrix m;    // transformation matrix
	if ( image.isNull() ) return;
	
	switch ( imgZoom ) {
	case ZOOM_1TO4: m.scale(0.25, 0.25); break;
	case ZOOM_1TO2: m.scale(0.50, 0.50); break;
	case ZOOM_2TO1: m.scale(2.0, 2.0); break;
	case ZOOM_4TO1: m.scale(4.0, 4.0);break;
	default: return;
	}
	QApplication::setOverrideCursor( waitCursor ); // this might take time
	pm = pm.xForm( m );  // create scaled pixmap
	QApplication::restoreOverrideCursor(); // restore original cursor
}

/*
  The resize event handler, if a valid pixmap was loaded it will call
  scale() to fit the pixmap to the new widget size.
*/

void ImageViewer::resizeEvent( QResizeEvent * )
{
	int mbh, sh;
	mbh = menubar->heightForWidth( width() );
	sh = status->height();
	status->setGeometry(0, height() -sh, width(), sh);
	msp->setGeometry(0, mbh, width(), height() - mbh - sh);
}

bool ImageViewer::convertEvent( QMouseEvent* e, int& x, int& y)
{
	int num, den;
	getZoomFactors(num, den);
	
	if ( pm.size() != QSize( 0, 0 ) ) {
		int nx = (e->x() -2);
		int ny = (e->y()-menubar->heightForWidth( width() ) - 2);
		if ( msp->horizontalScrollBar() != NULL)
			nx += msp->horizontalScrollBar()->value();
		if ( msp->verticalScrollBar() != NULL)
			ny += msp->verticalScrollBar()->value();
		nx = (nx * den)/num;
		ny = (ny * den)/num;
		if (nx != x || ny != y ) {
			x = nx;
			y = ny;
			updateStatus();
			return TRUE;
		}
	}
	return FALSE;
}

/*
  Record the pixel position of interest.
*/
void ImageViewer::mouseMoveEvent( QMouseEvent *e )
{
	if (convertEvent(e,pickx,picky)) 
		updateStatus();
}

/*
  Explain anything that might be confusing.
*/
void ImageViewer::giveHelp()
{
	if (!helpmsg) {
		QString helptext =
				"<b>Usage:</b> <tt>SBIGImgView <i>filename ...</i></tt>"
				"<p>Supported input formats:"
				"<blockquote>";
		helptext += "SBIG Compressed SBIG Uncompressed";
		helptext += "</blockquote>";
		
		helpmsg = new QMessageBox( "Help", helptext,
								   QMessageBox::Information, QMessageBox::Ok, 0, 0, 0, 0, FALSE );
	}
	helpmsg->show();
	helpmsg->raise();
}

void ImageViewer::createPalette()
{
	for(int i=0; i<256; i++)
		image.setColor(videoInverted ? 255 - i : i, qRgb(i,i,i));
}

void ImageViewer::hFlip()
{
	pSbigImg->HorizontalFlip();
	reconvertImage();
}

void ImageViewer::vFlip()
{
	pSbigImg->VerticalFlip();
	reconvertImage();
}

void ImageViewer::rot180()
{
	pSbigImg->HorizontalFlip();
	pSbigImg->VerticalFlip();
	reconvertImage();
}

void ImageViewer::deltaZoom()
{
	pickx = -1;
	reconvertImage();
}

void ImageViewer::zoom1To4()
{
	imgZoom = ZOOM_1TO4;
	deltaZoom();
}

void ImageViewer::zoom1To2()
{
	imgZoom = ZOOM_1TO2;
	deltaZoom();
}

void ImageViewer::zoom1To1()
{
	imgZoom = ZOOM_1TO1;
	deltaZoom();
}

void ImageViewer::zoom2To1()
{
	imgZoom = ZOOM_2TO1;
	deltaZoom();
}

void ImageViewer::zoom4To1()
{
	imgZoom = ZOOM_4TO1;
	deltaZoom();
}

void ImageViewer::autoContrast()
{
	pSbigImg->AutoBackgroundAndRange();
	reconvertImage();
}

void ImageViewer::showContrast()
{    
	contrastForm contrast(this);
	contrast.m_uBack = pSbigImg->GetBackground();
	contrast.m_uRange = pSbigImg->GetRange();
	
	contrast.setControls();
	if ( contrast.exec() ) {
		pSbigImg->SetBackground(contrast.m_uBack);
		pSbigImg->SetRange(contrast.m_uRange);
		reconvertImage();
	}
}

void ImageViewer::showImageInfo()
{
	QString m1, m2, m3;
	int colPos = 18, i;
	struct tm mytm;
	
	imageInfoForm iif(this);
	m2.sprintf("<u>Image Parameters</u>"); m1 += m2;
	m3 = filename;
	if ( (i=m3.findRev('/')) != -1 ) {
		m3 = m3.right(m3.length() - i - 1);
		m3 = ".../" + m3;
	}
	m2.sprintf("\n%*s: %s", colPos,"File name",m3.ascii());m1 += m2;
	mytm = pSbigImg->GetImageStartTime();
	m2.sprintf("\n%*s: %02d/%02d/%04d  Time:%02d:%02d:%02d", colPos,"Observation Date",
			   mytm.tm_mon+1, mytm.tm_mday, mytm.tm_year+1900, mytm.tm_hour, mytm.tm_min, mytm.tm_sec);m1 += m2;
	m2.sprintf("\n%*s: %s", colPos,"Observer",pSbigImg->GetObserver().c_str());m1 += m2;
	m2.sprintf("\n%*s: %s", colPos,"Note",pSbigImg->GetImageNote().c_str());m1 += m2;
	m2.sprintf("\n%*s: %s", colPos,"Acq. Software",pSbigImg->GetSoftware().c_str());m1 += m2;
	
	m2.sprintf("\n<u>CCD Parameters</u>"); m1 += m2;
	m2.sprintf("\n%*s: %s", colPos,"Camera",pSbigImg->GetCameraModel().c_str());m1 += m2;
	m2.sprintf("\n%*s: %1.3lf Seconds", colPos,"Exposure",pSbigImg->GetExposureTime());m1 += m2;
	m2.sprintf("\n%*s: %u of %1.3lf Sec.  Pedestal:%u", colPos,"Exposures",
			   pSbigImg->GetNumberExposures(), pSbigImg->GetEachExposure(), pSbigImg->GetPedestal());m1 += m2;
	m2.sprintf("\n%*s: %d Pixels Wide x %d Pixels High", colPos,"Image Size",
			   pSbigImg->GetWidth(), pSbigImg->GetHeight());m1 += m2;
	m2.sprintf("\n%*s: %1.1lf x %1.1lf microns", colPos,"Pixel Size",
			   1000.0*pSbigImg->GetPixelWidth(), 1000.0*pSbigImg->GetPixelHeight());m1 += m2;
	m2.sprintf("\n%*s: %1.2lf Degrees C", colPos,"Temperature",pSbigImg->GetCCDTemperature());m1 += m2;
	m2.sprintf("\n%*s: %1.2lf", colPos,"Response Factor",pSbigImg->GetResponseFactor());m1 += m2;
	m2.sprintf("\n%*s: %1.2lf e-/ADU", colPos,"Electronic Gain",pSbigImg->GetEGain());m1 += m2;
	
	m2.sprintf("\n<u>Telescope Parameters</u>"); m1 += m2;
	m2.sprintf("\n%*s: %1.2lf Inches", colPos,"Focal Length",pSbigImg->GetFocalLength());m1 += m2;
	m2.sprintf("\n%*s: %1.4lf Square Inches", colPos,"Aperture Area",pSbigImg->GetApertureArea());m1 += m2;
	m2.sprintf("\n%*s: %s", colPos,"Optical Filter",pSbigImg->GetFilter().c_str());m1 += m2;
	if ( pSbigImg->GetTrackExposure() < 0.001 )
		m3 = "Unknown";
	else
		m3.sprintf("%1.3lf Seconds", pSbigImg->GetTrackExposure());
	m2.sprintf("\n%*s: %s", colPos,"Tracking",m3.ascii());m1 += m2;
	
	iif.m_msg = m1;
	iif.setupDialog();
	iif.exec();
}

void ImageViewer::inverseVideo(void)
{
	videoInverted = !videoInverted;
	createPalette();
	reconvertImage();
}

void ImageViewer::getZoomFactors(int &num, int &den) {
	switch ( imgZoom ) {
	case ZOOM_1TO4: num = 1; den = 4; break;
	case ZOOM_1TO2: num = 1; den = 2; break;
	case ZOOM_2TO1: num = 2; den = 1; break;
	case ZOOM_4TO1: num = 4; den = 1; break;
	default: num = den = 1; break;
	}
}
