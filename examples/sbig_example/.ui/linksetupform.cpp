/****************************************************************************
** Form implementation generated from reading ui file 'linksetupform.ui'
**
** Created: Wed Feb 16 11:06:23 2005
**      by: The User Interface Compiler ($Id: qt/main.cpp   3.3.3   edited Nov 24 2003 $)
**
** WARNING! All changes made in this file will be lost!
****************************************************************************/

#include "linksetupform.h"

#include <qvariant.h>
#include <qpushbutton.h>
#include <qlineedit.h>
#include <qlabel.h>
#include <qbuttongroup.h>
#include <qradiobutton.h>
#include <qlayout.h>
#include <qtooltip.h>
#include <qwhatsthis.h>
#include <qimage.h>
#include <qpixmap.h>

#include "../linksetupform.ui.h"
/*
 *  Constructs a linkSetupForm as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 *
 *  The dialog will by default be modeless, unless you set 'modal' to
 *  TRUE to construct a modal dialog.
 */
linkSetupForm::linkSetupForm( QWidget* parent, const char* name, bool modal, WFlags fl )
    : QDialog( parent, name, modal, fl )
{
    if ( !name )
	setName( "linkSetupForm" );

    cancelButton = new QPushButton( this, "cancelButton" );
    cancelButton->setGeometry( QRect( 167, 96, 82, 31 ) );

    ethAddr = new QLineEdit( this, "ethAddr" );
    ethAddr->setGeometry( QRect( 128, 65, 121, 23 ) );

    okButton = new QPushButton( this, "okButton" );
    okButton->setGeometry( QRect( 103, 96, 58, 31 ) );
    okButton->setDefault( TRUE );

    textLabelEthAddr = new QLabel( this, "textLabelEthAddr" );
    textLabelEthAddr->setGeometry( QRect( 12, 65, 110, 23 ) );
    textLabelEthAddr->setAlignment( int( QLabel::AlignVCenter | QLabel::AlignRight ) );

    buttonGroup3 = new QButtonGroup( this, "buttonGroup3" );
    buttonGroup3->setGeometry( QRect( 11, 2, 239, 60 ) );

    radioButtonUSB = new QRadioButton( buttonGroup3, "radioButtonUSB" );
    radioButtonUSB->setGeometry( QRect( 117, 15, 83, 23 ) );

    radioButtonEth = new QRadioButton( buttonGroup3, "radioButtonEth" );
    radioButtonEth->setGeometry( QRect( 117, 34, 83, 23 ) );
    languageChange();
    resize( QSize(260, 133).expandedTo(minimumSizeHint()) );
    clearWState( WState_Polished );

    // signals and slots connections
    connect( okButton, SIGNAL( clicked() ), this, SLOT( onOK() ) );
    connect( cancelButton, SIGNAL( clicked() ), this, SLOT( close() ) );
    connect( radioButtonEth, SIGNAL( clicked() ), this, SLOT( portTypeSelected() ) );
    connect( radioButtonUSB, SIGNAL( clicked() ), this, SLOT( portTypeSelected() ) );

    // tab order
    setTabOrder( ethAddr, okButton );
    setTabOrder( okButton, cancelButton );

    // buddies
    textLabelEthAddr->setBuddy( ethAddr );
    init();
}

/*
 *  Destroys the object and frees any allocated resources
 */
linkSetupForm::~linkSetupForm()
{
    destroy();
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void linkSetupForm::languageChange()
{
    setCaption( tr( "Link Setup" ) );
    cancelButton->setText( tr( "Cancel" ) );
    ethAddr->setText( QString::null );
    okButton->setText( tr( "OK" ) );
    textLabelEthAddr->setText( tr( "Ethernet &Address" ) );
    buttonGroup3->setTitle( tr( "&Port/Interface" ) );
    radioButtonUSB->setText( tr( "&USB" ) );
    radioButtonUSB->setAccel( QKeySequence( tr( "Alt+U" ) ) );
    radioButtonEth->setText( tr( "&Ethernet" ) );
    radioButtonEth->setAccel( QKeySequence( tr( "Alt+E" ) ) );
}

