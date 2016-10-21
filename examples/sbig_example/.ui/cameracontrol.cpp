/****************************************************************************
** Form implementation generated from reading ui file 'cameracontrol.ui'
**
** Created: Wed Feb 16 11:06:05 2005
**      by: The User Interface Compiler ($Id: qt/main.cpp   3.3.3   edited Nov 24 2003 $)
**
** WARNING! All changes made in this file will be lost!
****************************************************************************/

#include "cameracontrol.h"

#include <qvariant.h>
#include <qgroupbox.h>
#include <qlabel.h>
#include <qtabwidget.h>
#include <qwidget.h>
#include <qpushbutton.h>
#include <qcombobox.h>
#include <qcheckbox.h>
#include <qlineedit.h>
#include <qlayout.h>
#include <qtooltip.h>
#include <qwhatsthis.h>
#include "../cameracontrol.ui.h"

/*
 *  Constructs a cameraControl as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 *
 *  The dialog will by default be modeless, unless you set 'modal' to
 *  TRUE to construct a modal dialog.
 */
cameraControl::cameraControl( QWidget* parent, const char* name, bool modal, WFlags fl )
    : QDialog( parent, name, modal, fl )
{
    if ( !name )
	setName( "cameraControl" );

    groupBox3 = new QGroupBox( this, "groupBox3" );
    groupBox3->setGeometry( QRect( 210, 220, 150, 50 ) );

    ccdTempLbl = new QLabel( groupBox3, "ccdTempLbl" );
    ccdTempLbl->setGeometry( QRect( 10, 20, 120, 20 ) );

    groupBox1_2 = new QGroupBox( this, "groupBox1_2" );
    groupBox1_2->setGeometry( QRect( 10, 220, 200, 50 ) );

    statusLbl = new QLabel( groupBox1_2, "statusLbl" );
    statusLbl->setGeometry( QRect( 10, 20, 180, 20 ) );
    statusLbl->setFrameShape( QLabel::NoFrame );

    tabWidget = new QTabWidget( this, "tabWidget" );
    tabWidget->setGeometry( QRect( 10, 10, 350, 210 ) );

    tab = new QWidget( tabWidget, "tab" );

    linkLabel = new QLabel( tab, "linkLabel" );
    linkLabel->setGeometry( QRect( 9, 4, 31, 31 ) );
    linkLabel->setAlignment( int( QLabel::AlignVCenter | QLabel::AlignRight ) );

    shutdownButton = new QPushButton( tab, "shutdownButton" );
    shutdownButton->setGeometry( QRect( 229, 4, 103, 31 ) );

    textLabel9 = new QLabel( tab, "textLabel9" );
    textLabel9->setGeometry( QRect( 48, 41, 75, 31 ) );
    textLabel9->setAlignment( int( QLabel::AlignVCenter | QLabel::AlignRight ) );

    textLabel11 = new QLabel( tab, "textLabel11" );
    textLabel11->setGeometry( QRect( 48, 78, 75, 31 ) );
    textLabel11->setAlignment( int( QLabel::AlignVCenter | QLabel::AlignRight ) );

    ccdCB = new QComboBox( FALSE, tab, "ccdCB" );
    ccdCB->setGeometry( QRect( 129, 78, 97, 31 ) );

    resolutionCB = new QComboBox( FALSE, tab, "resolutionCB" );
    resolutionCB->setGeometry( QRect( 129, 41, 97, 31 ) );

    linkSetupButton = new QPushButton( tab, "linkSetupButton" );
    linkSetupButton->setGeometry( QRect( 46, 4, 77, 31 ) );

    establishButton = new QPushButton( tab, "establishButton" );
    establishButton->setGeometry( QRect( 129, 4, 94, 31 ) );

    groupBox1 = new QGroupBox( tab, "groupBox1" );
    groupBox1->setGeometry( QRect( 10, 110, 330, 60 ) );

    enableChkBox = new QCheckBox( groupBox1, "enableChkBox" );
    enableChkBox->setGeometry( QRect( 11, 24, 70, 23 ) );
    enableChkBox->setChecked( TRUE );

    textLabel12 = new QLabel( groupBox1, "textLabel12" );
    textLabel12->setGeometry( QRect( 87, 20, 70, 30 ) );
    textLabel12->setAlignment( int( QLabel::AlignVCenter | QLabel::AlignRight ) );

    coolingUpdateButton = new QPushButton( groupBox1, "coolingUpdateButton" );
    coolingUpdateButton->setGeometry( QRect( 224, 19, 85, 31 ) );

    coolingSetpoint = new QLineEdit( groupBox1, "coolingSetpoint" );
    coolingSetpoint->setGeometry( QRect( 158, 23, 50, 23 ) );
    coolingSetpoint->setMaximumSize( QSize( 50, 32767 ) );
    tabWidget->insertTab( tab, QString("") );

    TabPage = new QWidget( tabWidget, "TabPage" );

    textLabel7 = new QLabel( TabPage, "textLabel7" );
    textLabel7->setGeometry( QRect( 49, 77, 76, 31 ) );
    textLabel7->setAlignment( int( QLabel::AlignVCenter | QLabel::AlignRight ) );

    textLabel6 = new QLabel( TabPage, "textLabel6" );
    textLabel6->setGeometry( QRect( 59, 37, 64, 31 ) );
    textLabel6->setAlignment( int( QLabel::AlignVCenter | QLabel::AlignRight ) );

    darkFrameCB = new QComboBox( FALSE, TabPage, "darkFrameCB" );
    darkFrameCB->setGeometry( QRect( 131, 77, 77, 31 ) );
    darkFrameCB->setMaximumSize( QSize( 80, 32767 ) );

    grabButton = new QPushButton( TabPage, "grabButton" );
    grabButton->setGeometry( QRect( 186, 36, 69, 30 ) );

    exposureFld = new QLineEdit( TabPage, "exposureFld" );
    exposureFld->setGeometry( QRect( 129, 38, 50, 26 ) );
    exposureFld->setMaximumSize( QSize( 50, 32767 ) );
    tabWidget->insertTab( TabPage, QString("") );
    languageChange();
    resize( QSize(371, 281).expandedTo(minimumSizeHint()) );
    clearWState( WState_Polished );

    // signals and slots connections
    connect( coolingUpdateButton, SIGNAL( clicked() ), this, SLOT( updateCoolingClicked() ) );
    connect( shutdownButton, SIGNAL( clicked() ), this, SLOT( shutdownClicked() ) );
    connect( establishButton, SIGNAL( clicked() ), this, SLOT( establishLinkClicked() ) );
    connect( linkSetupButton, SIGNAL( clicked() ), this, SLOT( linkSetupClicked() ) );
    connect( grabButton, SIGNAL( clicked() ), this, SLOT( grabClicked() ) );
    connect( coolingUpdateButton, SIGNAL( clicked() ), this, SLOT( updateCoolingClicked() ) );

    // buddies
    textLabel12->setBuddy( coolingSetpoint );
    textLabel6->setBuddy( exposureFld );
    init();
}

/*
 *  Destroys the object and frees any allocated resources
 */
cameraControl::~cameraControl()
{
    destroy();
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void cameraControl::languageChange()
{
    setCaption( tr( "Camera Control" ) );
    groupBox3->setTitle( tr( "CCD Temp" ) );
    ccdTempLbl->setText( tr( "Unknown" ) );
    groupBox1_2->setTitle( tr( "Camera Status" ) );
    statusLbl->setText( tr( "Link not established" ) );
    linkLabel->setText( tr( "Link:" ) );
    shutdownButton->setText( tr( "Sh&utdown" ) );
    shutdownButton->setAccel( QKeySequence( tr( "Alt+U" ) ) );
    textLabel9->setText( tr( "Resolution:" ) );
    textLabel11->setText( tr( "Active CCD:" ) );
    ccdCB->clear();
    ccdCB->insertItem( tr( "Imaging" ) );
    ccdCB->insertItem( tr( "Tracking" ) );
    resolutionCB->clear();
    resolutionCB->insertItem( tr( "High" ) );
    resolutionCB->insertItem( tr( "Medium" ) );
    resolutionCB->insertItem( tr( "Low" ) );
    linkSetupButton->setText( tr( "&Setup" ) );
    linkSetupButton->setAccel( QKeySequence( tr( "Alt+S" ) ) );
    establishButton->setText( tr( "&Establish" ) );
    establishButton->setAccel( QKeySequence( tr( "Alt+E" ) ) );
    groupBox1->setTitle( tr( "Cooling" ) );
    enableChkBox->setText( tr( "Enable" ) );
    textLabel12->setText( tr( "Setpoint:" ) );
    coolingUpdateButton->setText( tr( "&Update" ) );
    coolingUpdateButton->setAccel( QKeySequence( tr( "Alt+U" ) ) );
    coolingSetpoint->setText( tr( "." ) );
    coolingSetpoint->setInputMask( tr( "#09.99; " ) );
    tabWidget->changeTab( tab, tr( "Link/Setup" ) );
    textLabel7->setText( tr( "Dark Frame:" ) );
    textLabel6->setText( tr( "Exposure:" ) );
    darkFrameCB->clear();
    darkFrameCB->insertItem( tr( "None" ) );
    darkFrameCB->insertItem( tr( "Only" ) );
    darkFrameCB->insertItem( tr( "Also" ) );
    grabButton->setText( tr( "&Grab" ) );
    grabButton->setAccel( QKeySequence( tr( "Alt+G" ) ) );
    exposureFld->setInputMask( tr( "09.999; " ) );
    tabWidget->changeTab( TabPage, tr( "Grab" ) );
}

