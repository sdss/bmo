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
#include <qradiobutton.h>
#include <qlineedit.h>
#include <qtimer.h>
#include <qimage.h>
#include <qmessagebox.h>
#include <qhostaddress.h>
#include <qfiledialog.h>

#include "csbigcam.h"
#include "showimg.h"
#include "globalT.h"
#include "linksetupform.h"


QTimer *timer=(QTimer *)0;
CSBIGCam *camera;
CSBIGImg *image;

void cameraControl::init() 
{
 
 QString str;
 coolingSetpoint->setText("0.00");
 str.setNum(globals.exposure);
 exposureFld->setText(str.ascii());
 resolutionCB->setCurrentItem(globals.resolution);
 ccdCB->setCurrentItem(globals.activeCCD);
 
 timer = new QTimer(this);    
 timer->start(1000);
 connect(timer, SIGNAL(timeout()), this, SLOT(timerTick()));
 updateStatus();
 
 image = new CSBIGImg();
 camera = new CSBIGCam(); 
 if (camera->GetError() != CE_NO_ERROR) {
  QMessageBox::information((QWidget*)0, "CCDOpsLite", "Error creating camera object.");
  delete camera;
  camera = (CSBIGCam*)0;
 }    
}

void cameraControl::destroy() 
{
 if (camera) {
  camera->CloseDevice();
  camera->CloseDriver();
  globals.connected = FALSE;
  globals.activeCCD = ccdCB->currentItem();
  globals.resolution = resolutionCB->currentItem();
  globals.exposure = exposureFld->text().toDouble();
 }
}

void cameraControl::linkSetupClicked()
{
	linkSetupForm ls(this);
	ls.exec();
}

void cameraControl::grabClicked()
{
 int err;
 
 QApplication::setOverrideCursor( waitCursor );
 
 camera->SetExposureTime(exposureFld->text().toDouble());
 
 SBIG_DARK_FRAME df = (SBIG_DARK_FRAME)darkFrameCB->currentItem();
 switch (df) {
 case 0: df = SBDF_LIGHT_ONLY; break;
 case 1: df = SBDF_DARK_ONLY; break;
 case 2: df = SBDF_DARK_ALSO; break;
 default: df = SBDF_LIGHT_ONLY; break;
 }
 camera->SetReadoutMode(resolutionCB->currentItem());
 camera->SetActiveCCD((CCD_REQUEST)(ccdCB->currentItem()));
 statusLbl->setText("Grabbing image...");
 if ( (err=camera->GrabImage(image, df)) != CE_NO_ERROR ) {
  QApplication::restoreOverrideCursor();
  QMessageBox::information((QWidget*)0, "CCDOpsLite", "Grab error."); 
  return;
 }
 
 QApplication::restoreOverrideCursor();
 
 ImageViewer *w = new ImageViewer(0, "new window", Qt::WDestructiveClose | Qt::WResizeNoErase );
 w->setCaption("SBIG Image Viewer");
 w->show();
 w->setImage(image);
 image = new CSBIGImg;
 statusLbl->setText("Grab complete.");
}

void cameraControl::establishLinkClicked()
{
	int err;
	OpenDeviceParams odp;
	
	if ( globals.portType == PT_USB )
		odp.deviceType = DEV_USB;
	else if ( globals.portType == PT_ETHERNET ) {
		QHostAddress adr;
		adr.setAddress(globals.ip);
		odp.ipAddress = adr.ip4Addr();
		odp.deviceType = DEV_ETH;
	}
	else {
		QMessageBox::information((QWidget*)0, "CCDOpsLite", "Invalid port type."); 
		return;
	}
	
	if ((err=camera->OpenDriver()) != CE_NO_ERROR) {
		QMessageBox::information((QWidget*)0, "CCDOpsLite", "Error opening camera driver.");
		return;
	}
	
	if ((err=camera->OpenDevice(odp)) != CE_NO_ERROR) {
		QMessageBox::information((QWidget*)0, "CCDOpsLite", "Error opening camera device.");
		return;
	}
	
	if ((err=camera->EstablishLink()) != CE_NO_ERROR) {
		QMessageBox::information((QWidget*)0, "CCDOpsLite", "Error establishing link to camera.");
		return;
	}
	
	QString *camType = new QString(camera->GetCameraTypeString().c_str());
	*camType = "Link to:" + *camType;
	if ( globals.portType == PT_USB )
		*camType += " on USB";
	else
		*camType += " on Ethernet";	
	statusLbl->setText(camType->ascii());
	
	globals.connected = TRUE;
	updateStatus();
	
	MY_LOGICAL enabled;
	double ccdTemp, setpointTemp, percentTE;
	QString qs;
	camera->QueryTemperatureStatus(enabled, ccdTemp, setpointTemp, percentTE);
	enableChkBox->setChecked(enabled);
	qs.setNum(setpointTemp, 'f',2);
	coolingSetpoint->setText(qs.ascii());
}

void cameraControl::shutdownClicked()
{
	if (camera) {
		camera->CloseDevice();
		camera->CloseDriver();
	}
	
	globals.connected = FALSE;
	statusLbl->setText("Link not established");
	updateStatus();
}

void cameraControl::updateStatus()
{
	if (globals.connected) {
		coolingUpdateButton->setEnabled(TRUE);
		establishButton->setEnabled(FALSE);
		shutdownButton->setEnabled(TRUE);
		grabButton->setEnabled(TRUE);
		
		double temp, setpt, percentTE;
		MY_LOGICAL ena;
		camera->QueryTemperatureStatus(ena, temp, setpt, percentTE);
		
		QString str = QString("%1C @ TE=%1%").arg(temp,0,'f',2).arg(100.0*percentTE,1,'f',0);
		ccdTempLbl->setText(str.ascii());
	}
	else {
		coolingUpdateButton->setEnabled(FALSE);
		establishButton->setEnabled(TRUE);
		shutdownButton->setEnabled(FALSE);
		grabButton->setEnabled(FALSE);
		ccdTempLbl->setText("Unknown");
	} 
}

void cameraControl::timerTick()
{
	updateStatus();
}

void cameraControl::updateCoolingClicked()
{
	camera->SetTemperatureRegulation(enableChkBox->isChecked(),
									 coolingSetpoint->text().toDouble());
}
