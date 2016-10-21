/****************************************************************************
** Form interface generated from reading ui file 'contrastform.ui'
**
** Created: Wed Feb 16 11:05:30 2005
**      by: The User Interface Compiler ($Id: qt/main.cpp   3.3.3   edited Nov 24 2003 $)
**
** WARNING! All changes made in this file will be lost!
****************************************************************************/

#ifndef CONTRASTFORM_H
#define CONTRASTFORM_H

#include <qvariant.h>
#include <qdialog.h>

class QVBoxLayout;
class QHBoxLayout;
class QGridLayout;
class QSpacerItem;
class QLabel;
class QLineEdit;
class QPushButton;

class contrastForm : public QDialog
{
    Q_OBJECT

public:
    contrastForm( QWidget* parent = 0, const char* name = 0, bool modal = FALSE, WFlags fl = 0 );
    ~contrastForm();

    QLabel* rangeLabel;
    QLabel* backLabel;
    QLineEdit* backEdit;
    QLineEdit* rangeEdit;
    QPushButton* applyButton;

    unsigned short m_uRange;
    unsigned short m_uBack;

public slots:
    virtual void onApply();
    virtual void setControls();

protected:
    QVBoxLayout* contrastFormLayout;
    QSpacerItem* spacer5;
    QGridLayout* layout36;

protected slots:
    virtual void languageChange();

    virtual bool validate();


};

#endif // CONTRASTFORM_H
