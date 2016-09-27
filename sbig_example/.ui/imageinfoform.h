/****************************************************************************
** Form interface generated from reading ui file 'imageinfoform.ui'
**
** Created: Wed Feb 16 11:05:30 2005
**      by: The User Interface Compiler ($Id: qt/main.cpp   3.3.3   edited Nov 24 2003 $)
**
** WARNING! All changes made in this file will be lost!
****************************************************************************/

#ifndef IMAGEINFOFORM_H
#define IMAGEINFOFORM_H

#include <qvariant.h>
#include <qdialog.h>

class QVBoxLayout;
class QHBoxLayout;
class QGridLayout;
class QSpacerItem;
class QTextEdit;
class QPushButton;

class imageInfoForm : public QDialog
{
    Q_OBJECT

public:
    imageInfoForm( QWidget* parent = 0, const char* name = 0, bool modal = FALSE, WFlags fl = 0 );
    ~imageInfoForm();

    QTextEdit* infoText;
    QPushButton* doneButton;

    QString m_msg;

public slots:
    virtual void setupDialog();

protected:

protected slots:
    virtual void languageChange();

};

#endif // IMAGEINFOFORM_H
