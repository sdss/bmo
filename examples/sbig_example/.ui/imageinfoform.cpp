/****************************************************************************
** Form implementation generated from reading ui file 'imageinfoform.ui'
**
** Created: Wed Feb 16 11:06:18 2005
**      by: The User Interface Compiler ($Id: qt/main.cpp   3.3.3   edited Nov 24 2003 $)
**
** WARNING! All changes made in this file will be lost!
****************************************************************************/

#include "imageinfoform.h"

#include <qvariant.h>
#include <qtextedit.h>
#include <qpushbutton.h>
#include <qlayout.h>
#include <qtooltip.h>
#include <qwhatsthis.h>
#include <qimage.h>
#include <qpixmap.h>

#include "../imageinfoform.ui.h"
/*
 *  Constructs a imageInfoForm as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 *
 *  The dialog will by default be modeless, unless you set 'modal' to
 *  TRUE to construct a modal dialog.
 */
imageInfoForm::imageInfoForm( QWidget* parent, const char* name, bool modal, WFlags fl )
    : QDialog( parent, name, modal, fl )
{
    if ( !name )
	setName( "imageInfoForm" );
    QFont f( font() );
    f.setFamily( "Courier" );
    setFont( f ); 

    infoText = new QTextEdit( this, "infoText" );
    infoText->setGeometry( QRect( 10, 10, 400, 330 ) );
    infoText->setTextFormat( QTextEdit::PlainText );

    doneButton = new QPushButton( this, "doneButton" );
    doneButton->setGeometry( QRect( 10, 350, 100, 27 ) );
    doneButton->setMaximumSize( QSize( 100, 32767 ) );
    languageChange();
    resize( QSize(423, 381).expandedTo(minimumSizeHint()) );
    clearWState( WState_Polished );

    // signals and slots connections
    connect( doneButton, SIGNAL( clicked() ), this, SLOT( reject() ) );
}

/*
 *  Destroys the object and frees any allocated resources
 */
imageInfoForm::~imageInfoForm()
{
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void imageInfoForm::languageChange()
{
    setCaption( tr( "Image Information" ) );
    infoText->setText( QString::null );
    doneButton->setText( tr( "Done" ) );
}

