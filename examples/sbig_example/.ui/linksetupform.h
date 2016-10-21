/****************************************************************************
** Form interface generated from reading ui file 'linksetupform.ui'
**
** Created: Wed Feb 16 11:05:30 2005
**      by: The User Interface Compiler ($Id: qt/main.cpp   3.3.3   edited Nov 24 2003 $)
**
** WARNING! All changes made in this file will be lost!
****************************************************************************/

#ifndef LINKSETUPFORM_H
#define LINKSETUPFORM_H

#include <qvariant.h>
#include <qdialog.h>

class QVBoxLayout;
class QHBoxLayout;
class QGridLayout;
class QSpacerItem;
class QPushButton;
class QLineEdit;
class QLabel;
class QButtonGroup;
class QRadioButton;

class linkSetupForm : public QDialog
{
    Q_OBJECT

public:
    linkSetupForm( QWidget* parent = 0, const char* name = 0, bool modal = FALSE, WFlags fl = 0 );
    ~linkSetupForm();

    QPushButton* cancelButton;
    QLineEdit* ethAddr;
    QPushButton* okButton;
    QLabel* textLabelEthAddr;
    QButtonGroup* buttonGroup3;
    QRadioButton* radioButtonUSB;
    QRadioButton* radioButtonEth;

public slots:
    virtual void onOK();
    virtual void portTypeSelected();

protected:

protected slots:
    virtual void languageChange();

private:
    virtual void init();
    virtual void destroy();

};

#endif // LINKSETUPFORM_H
