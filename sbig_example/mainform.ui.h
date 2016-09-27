/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you want to add, delete, or rename functions or slots, use
** Qt Designer to update this file, preserving your code.
**
** You should not define a constructor or destructor in this file.
** Instead, write your code in functions called init() and destroy().
** These will automatically be called by the form's constructor and
** destructor.
*****************************************************************************/

#include <qapplication.h>
#include <qcombobox.h>
#include <qfiledialog.h>
#include <qmessagebox.h>

#include "mainform.h"
#include "cameracontrol.h"
#include "showimg.h"
#include "globalT.h"

//globalT globals;

cameraControl *cc;

void mainform::init() 
{
 cc = new cameraControl(this);
 cc->show();
}

void mainform::destroy()
{
 delete cc;
}

void mainform::fileOpen()
{
	QString msg;
	QString newfilename = QFileDialog::getOpenFileName( "~/images",
              "SBIG Images (*.sbig);;All files (*.*)",
              this );
	if ( !newfilename.isEmpty() ) {
		ImageViewer *w = new ImageViewer(0, "new window",
										 Qt::WDestructiveClose | Qt::WResizeNoErase );
		if ( w->loadImage(newfilename) )
			 w->show();
		else
			QMessageBox::information((QWidget*)0, "CCDOpsLite", "Error Opening Image");
	}
}

void mainform::closeEvent(QCloseEvent *)
{
    fileExit();
}


void mainform::fileExit()
{
    QApplication::exit(0);
}


void mainform::helpIndex()
{
    
}


void mainform::helpContents()
{

}

void mainform::helpAbout()
{

}

void mainform::editOptions()
{

}

void mainform::cameraSetup()
{
	cc->show();
}
