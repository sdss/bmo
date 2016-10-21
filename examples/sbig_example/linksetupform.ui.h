/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you want to add, delete, or rename functions or slots, use
** Qt Designer to update this file, preserving your code.
**
** You should not define a constructor or destructor in this file.
** Instead, write your code in functions called init() and destroy().
** These will automatically be called by the form's constructor and
** destructor.
*****************************************************************************/

#include "globalT.h"

void linkSetupForm::onOK()
{
	globals.ip.setLength(0);
	globals.ip.append(ethAddr->text());
	globals.portType = radioButtonUSB->isChecked() ? 0:1;
	accept();
}


void linkSetupForm::init()
{
	ethAddr->setText(globals.ip.ascii());
	if (globals.portType == 0) {
		radioButtonUSB->setChecked(TRUE);
		radioButtonEth->setChecked(FALSE);
		radioButtonUSB->setFocus();
		ethAddr->setEnabled(FALSE);
	} else {
		radioButtonUSB->setChecked(FALSE);
		radioButtonEth->setChecked(TRUE);
		ethAddr->setEnabled(TRUE);
		ethAddr->setFocus();
	}
}


void linkSetupForm::destroy()
{

}


void linkSetupForm::portTypeSelected()
{
	ethAddr->setEnabled(radioButtonEth->isChecked());
}
