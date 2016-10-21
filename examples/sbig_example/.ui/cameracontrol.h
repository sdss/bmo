/****************************************************************************
** Form interface generated from reading ui file 'cameracontrol.ui'
**
** Created: Wed Feb 16 11:05:30 2005
**      by: The User Interface Compiler ($Id: qt/main.cpp   3.3.3   edited Nov 24 2003 $)
**
** WARNING! All changes made in this file will be lost!
****************************************************************************/

#ifndef CAMERACONTROL_H
#define CAMERACONTROL_H

#include <qvariant.h>
#include <qdialog.h>

class QVBoxLayout;
class QHBoxLayout;
class QGridLayout;
class QSpacerItem;
class QGroupBox;
class QLabel;
class QTabWidget;
class QWidget;
class QPushButton;
class QComboBox;
class QCheckBox;
class QLineEdit;

class cameraControl : public QDialog
{
    Q_OBJECT

public:
    cameraControl( QWidget* parent = 0, const char* name = 0, bool modal = FALSE, WFlags fl = 0 );
    ~cameraControl();

    QGroupBox* groupBox3;
    QLabel* ccdTempLbl;
    QGroupBox* groupBox1_2;
    QLabel* statusLbl;
    QTabWidget* tabWidget;
    QWidget* tab;
    QLabel* linkLabel;
    QPushButton* shutdownButton;
    QLabel* textLabel9;
    QLabel* textLabel11;
    QComboBox* ccdCB;
    QComboBox* resolutionCB;
    QPushButton* linkSetupButton;
    QPushButton* establishButton;
    QGroupBox* groupBox1;
    QCheckBox* enableChkBox;
    QLabel* textLabel12;
    QPushButton* coolingUpdateButton;
    QLineEdit* coolingSetpoint;
    QWidget* TabPage;
    QLabel* textLabel7;
    QLabel* textLabel6;
    QComboBox* darkFrameCB;
    QPushButton* grabButton;
    QLineEdit* exposureFld;

public slots:
    virtual void linkSetupClicked();
    virtual void grabClicked();
    virtual void establishLinkClicked();
    virtual void shutdownClicked();
    virtual void updateStatus();
    virtual void timerTick();
    virtual void updateCoolingClicked();

protected:

protected slots:
    virtual void languageChange();

private:
    void init();
    void destroy();

};

#endif // CAMERACONTROL_H
