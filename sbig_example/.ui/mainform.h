/****************************************************************************
** Form interface generated from reading ui file 'mainform.ui'
**
** Created: Wed Feb 16 11:05:30 2005
**      by: The User Interface Compiler ($Id: qt/main.cpp   3.3.3   edited Nov 24 2003 $)
**
** WARNING! All changes made in this file will be lost!
****************************************************************************/

#ifndef MAINFORM_H
#define MAINFORM_H

#include <qvariant.h>
#include <qmainwindow.h>

class QVBoxLayout;
class QHBoxLayout;
class QGridLayout;
class QSpacerItem;
class QAction;
class QActionGroup;
class QToolBar;
class QPopupMenu;

class mainform : public QMainWindow
{
    Q_OBJECT

public:
    mainform( QWidget* parent = 0, const char* name = 0, WFlags fl = WType_TopLevel );
    ~mainform();

    QMenuBar *MenuBar;
    QPopupMenu *fileMenu;
    QPopupMenu *editMenu;
    QPopupMenu *Camera;
    QPopupMenu *helpMenu;
    QAction* fileOpenAction;
    QAction* fileExitAction;
    QAction* helpContentsAction;
    QAction* helpIndexAction;
    QAction* helpAboutAction;
    QAction* editOptionsAction;
    QAction* cameraSetupAction;

public slots:
    virtual void fileOpen();
    virtual void closeEvent( QCloseEvent * );
    virtual void fileExit();
    virtual void helpIndex();
    virtual void helpContents();
    virtual void helpAbout();
    virtual void editOptions();
    virtual void cameraSetup();

protected:
    QVBoxLayout* mainformLayout;

protected slots:
    virtual void languageChange();

private:
    void init();
    virtual void destroy();

};

#endif // MAINFORM_H
