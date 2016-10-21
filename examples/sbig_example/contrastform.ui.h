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

#include <qstring.h>

bool contrastForm::validate()
{
    QString qs;
    unsigned short us;
    bool ok;
 
    qs = backEdit->text();
    us = qs.toUShort(&ok);
    if ( !ok )
 return FALSE;
    m_uBack = us;
    
    qs = rangeEdit->text();
    us = qs.toUShort(&ok);
    if ( !ok || us == 0 )
 return FALSE;
    m_uRange = us;
    
    return TRUE;
}


void contrastForm::onApply()
{
    if ( validate() )
 accept();
}


void contrastForm::setControls()
{
    QString qs;
    qs = QString("%1").arg(m_uBack);
    backEdit->setText(qs);
    qs = QString("%1").arg( m_uRange);
    rangeEdit->setText(qs);
}
