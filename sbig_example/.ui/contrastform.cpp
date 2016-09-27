/****************************************************************************
** Form implementation generated from reading ui file 'contrastform.ui'
**
** Created: Wed Feb 16 11:06:13 2005
**      by: The User Interface Compiler ($Id: qt/main.cpp   3.3.3   edited Nov 24 2003 $)
**
** WARNING! All changes made in this file will be lost!
****************************************************************************/

#include "contrastform.h"

#include <qvariant.h>
#include <qlabel.h>
#include <qlineedit.h>
#include <qpushbutton.h>
#include <qlayout.h>
#include <qtooltip.h>
#include <qwhatsthis.h>
#include <qimage.h>
#include <qpixmap.h>

#include "../contrastform.ui.h"
/*
 *  Constructs a contrastForm as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 *
 *  The dialog will by default be modeless, unless you set 'modal' to
 *  TRUE to construct a modal dialog.
 */
contrastForm::contrastForm( QWidget* parent, const char* name, bool modal, WFlags fl )
    : QDialog( parent, name, modal, fl )
{
    if ( !name )
	setName( "contrastForm" );
    contrastFormLayout = new QVBoxLayout( this, 11, 6, "contrastFormLayout"); 

    layout36 = new QGridLayout( 0, 1, 1, 0, 6, "layout36"); 

    rangeLabel = new QLabel( this, "rangeLabel" );

    layout36->addWidget( rangeLabel, 1, 0 );

    backLabel = new QLabel( this, "backLabel" );

    layout36->addWidget( backLabel, 0, 0 );

    backEdit = new QLineEdit( this, "backEdit" );
    backEdit->setMaxLength( 6 );

    layout36->addWidget( backEdit, 0, 1 );

    rangeEdit = new QLineEdit( this, "rangeEdit" );
    rangeEdit->setMaxLength( 5 );

    layout36->addWidget( rangeEdit, 1, 1 );
    contrastFormLayout->addLayout( layout36 );
    spacer5 = new QSpacerItem( 20, 16, QSizePolicy::Minimum, QSizePolicy::Expanding );
    contrastFormLayout->addItem( spacer5 );

    applyButton = new QPushButton( this, "applyButton" );
    contrastFormLayout->addWidget( applyButton );
    languageChange();
    resize( QSize(124, 108).expandedTo(minimumSizeHint()) );
    clearWState( WState_Polished );

    // signals and slots connections
    connect( applyButton, SIGNAL( clicked() ), this, SLOT( onApply() ) );

    // tab order
    setTabOrder( backEdit, rangeEdit );
    setTabOrder( rangeEdit, applyButton );

    // buddies
    rangeLabel->setBuddy( rangeEdit );
    backLabel->setBuddy( backEdit );
}

/*
 *  Destroys the object and frees any allocated resources
 */
contrastForm::~contrastForm()
{
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void contrastForm::languageChange()
{
    setCaption( tr( "Contrast" ) );
    rangeLabel->setText( tr( "&Range:" ) );
    backLabel->setText( tr( "&Back:" ) );
    backEdit->setText( QString::null );
    backEdit->setInputMask( tr( "00000 ; " ) );
    rangeEdit->setInputMask( tr( "00000; " ) );
    applyButton->setText( tr( "&Apply" ) );
    applyButton->setAccel( QKeySequence( tr( "Alt+A" ) ) );
}

