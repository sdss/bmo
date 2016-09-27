/****************************************************************************
** Form implementation generated from reading ui file 'mainform.ui'
**
** Created: Wed Feb 16 11:05:56 2005
**      by: The User Interface Compiler ($Id: qt/main.cpp   3.3.3   edited Nov 24 2003 $)
**
** WARNING! All changes made in this file will be lost!
****************************************************************************/

#include "mainform.h"

#include <qvariant.h>
#include <qlayout.h>
#include <qtooltip.h>
#include <qwhatsthis.h>
#include <qaction.h>
#include <qmenubar.h>
#include <qpopupmenu.h>
#include <qtoolbar.h>
#include <qimage.h>
#include <qpixmap.h>

#include "../mainform.ui.h"
/*
 *  Constructs a mainform as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 *
 */
mainform::mainform( QWidget* parent, const char* name, WFlags fl )
    : QMainWindow( parent, name, fl )
{
    (void)statusBar();
    if ( !name )
	setName( "mainform" );
    setCentralWidget( new QWidget( this, "qt_central_widget" ) );
    mainformLayout = new QVBoxLayout( centralWidget(), 11, 6, "mainformLayout"); 

    // actions
    fileOpenAction = new QAction( this, "fileOpenAction" );
    fileOpenAction->setIconSet( QIconSet( QPixmap::fromMimeSource( "fileopen" ) ) );
    fileExitAction = new QAction( this, "fileExitAction" );
    fileExitAction->setIconSet( QIconSet( QPixmap::fromMimeSource( "undo" ) ) );
    helpContentsAction = new QAction( this, "helpContentsAction" );
    helpIndexAction = new QAction( this, "helpIndexAction" );
    helpAboutAction = new QAction( this, "helpAboutAction" );
    editOptionsAction = new QAction( this, "editOptionsAction" );
    cameraSetupAction = new QAction( this, "cameraSetupAction" );
    cameraSetupAction->setToggleAction( FALSE );


    // toolbars


    // menubar
    MenuBar = new QMenuBar( this, "MenuBar" );


    fileMenu = new QPopupMenu( this );
    fileOpenAction->addTo( fileMenu );
    fileMenu->insertSeparator();
    fileExitAction->addTo( fileMenu );
    MenuBar->insertItem( QString(""), fileMenu, 1 );

    editMenu = new QPopupMenu( this );
    editOptionsAction->addTo( editMenu );
    MenuBar->insertItem( QString(""), editMenu, 2 );

    Camera = new QPopupMenu( this );
    Camera->insertSeparator();
    cameraSetupAction->addTo( Camera );
    MenuBar->insertItem( QString(""), Camera, 3 );

    helpMenu = new QPopupMenu( this );
    helpContentsAction->addTo( helpMenu );
    helpIndexAction->addTo( helpMenu );
    helpMenu->insertSeparator();
    helpAboutAction->addTo( helpMenu );
    MenuBar->insertItem( QString(""), helpMenu, 4 );

    languageChange();
    resize( QSize(622, 416).expandedTo(minimumSizeHint()) );
    clearWState( WState_Polished );

    // signals and slots connections
    connect( fileOpenAction, SIGNAL( activated() ), this, SLOT( fileOpen() ) );
    connect( fileExitAction, SIGNAL( activated() ), this, SLOT( fileExit() ) );
    connect( helpIndexAction, SIGNAL( activated() ), this, SLOT( helpIndex() ) );
    connect( helpContentsAction, SIGNAL( activated() ), this, SLOT( helpContents() ) );
    connect( helpAboutAction, SIGNAL( activated() ), this, SLOT( helpAbout() ) );
    connect( editOptionsAction, SIGNAL( activated() ), this, SLOT( editOptions() ) );
    connect( cameraSetupAction, SIGNAL( activated() ), this, SLOT( cameraSetup() ) );
    init();
}

/*
 *  Destroys the object and frees any allocated resources
 */
mainform::~mainform()
{
    destroy();
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void mainform::languageChange()
{
    setCaption( tr( "SBIG CCDOps Lite" ) );
    fileOpenAction->setText( tr( "Open" ) );
    fileOpenAction->setMenuText( tr( "&Open..." ) );
    fileOpenAction->setAccel( tr( "Ctrl+O" ) );
    fileExitAction->setText( tr( "Exit" ) );
    fileExitAction->setMenuText( tr( "E&xit" ) );
    fileExitAction->setAccel( QString::null );
    helpContentsAction->setText( tr( "Contents" ) );
    helpContentsAction->setMenuText( tr( "&Contents..." ) );
    helpContentsAction->setAccel( QString::null );
    helpIndexAction->setText( tr( "Index" ) );
    helpIndexAction->setMenuText( tr( "&Index..." ) );
    helpIndexAction->setAccel( QString::null );
    helpAboutAction->setText( tr( "About" ) );
    helpAboutAction->setMenuText( tr( "&About" ) );
    helpAboutAction->setAccel( QString::null );
    editOptionsAction->setText( tr( "&Options" ) );
    editOptionsAction->setMenuText( tr( "&Options" ) );
    editOptionsAction->setToolTip( tr( "Options" ) );
    cameraSetupAction->setText( tr( "cameraSetup" ) );
    cameraSetupAction->setMenuText( tr( "Show Camera Panel" ) );
    cameraSetupAction->setToolTip( tr( "Setup camera" ) );
    cameraSetupAction->setAccel( tr( "Ctrl+I" ) );
    if (MenuBar->findItem(1))
        MenuBar->findItem(1)->setText( tr( "&File" ) );
    if (MenuBar->findItem(2))
        MenuBar->findItem(2)->setText( tr( "&Edit" ) );
    if (MenuBar->findItem(3))
        MenuBar->findItem(3)->setText( tr( "&Camera" ) );
    if (MenuBar->findItem(4))
        MenuBar->findItem(4)->setText( tr( "&Help" ) );
}

