/****************************************************************************
** linkSetupForm meta object code from reading C++ file 'linksetupform.h'
**
** Created: Wed Feb 16 11:24:40 2005
**      by: The Qt MOC ($Id: qt/moc_yacc.cpp   3.3.3   edited Aug 5 16:40 $)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#undef QT_NO_COMPAT
#include "../.ui/linksetupform.h"
#include <qmetaobject.h>
#include <qapplication.h>

#include <private/qucomextra_p.h>
#if !defined(Q_MOC_OUTPUT_REVISION) || (Q_MOC_OUTPUT_REVISION != 26)
#error "This file was generated using the moc from 3.3.3. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

const char *linkSetupForm::className() const
{
    return "linkSetupForm";
}

QMetaObject *linkSetupForm::metaObj = 0;
static QMetaObjectCleanUp cleanUp_linkSetupForm( "linkSetupForm", &linkSetupForm::staticMetaObject );

#ifndef QT_NO_TRANSLATION
QString linkSetupForm::tr( const char *s, const char *c )
{
    if ( qApp )
	return qApp->translate( "linkSetupForm", s, c, QApplication::DefaultCodec );
    else
	return QString::fromLatin1( s );
}
#ifndef QT_NO_TRANSLATION_UTF8
QString linkSetupForm::trUtf8( const char *s, const char *c )
{
    if ( qApp )
	return qApp->translate( "linkSetupForm", s, c, QApplication::UnicodeUTF8 );
    else
	return QString::fromUtf8( s );
}
#endif // QT_NO_TRANSLATION_UTF8

#endif // QT_NO_TRANSLATION

QMetaObject* linkSetupForm::staticMetaObject()
{
    if ( metaObj )
	return metaObj;
    QMetaObject* parentObject = QDialog::staticMetaObject();
    static const QUMethod slot_0 = {"onOK", 0, 0 };
    static const QUMethod slot_1 = {"portTypeSelected", 0, 0 };
    static const QUMethod slot_2 = {"languageChange", 0, 0 };
    static const QMetaData slot_tbl[] = {
	{ "onOK()", &slot_0, QMetaData::Public },
	{ "portTypeSelected()", &slot_1, QMetaData::Public },
	{ "languageChange()", &slot_2, QMetaData::Protected }
    };
    metaObj = QMetaObject::new_metaobject(
	"linkSetupForm", parentObject,
	slot_tbl, 3,
	0, 0,
#ifndef QT_NO_PROPERTIES
	0, 0,
	0, 0,
#endif // QT_NO_PROPERTIES
	0, 0 );
    cleanUp_linkSetupForm.setMetaObject( metaObj );
    return metaObj;
}

void* linkSetupForm::qt_cast( const char* clname )
{
    if ( !qstrcmp( clname, "linkSetupForm" ) )
	return this;
    return QDialog::qt_cast( clname );
}

bool linkSetupForm::qt_invoke( int _id, QUObject* _o )
{
    switch ( _id - staticMetaObject()->slotOffset() ) {
    case 0: onOK(); break;
    case 1: portTypeSelected(); break;
    case 2: languageChange(); break;
    default:
	return QDialog::qt_invoke( _id, _o );
    }
    return TRUE;
}

bool linkSetupForm::qt_emit( int _id, QUObject* _o )
{
    return QDialog::qt_emit(_id,_o);
}
#ifndef QT_NO_PROPERTIES

bool linkSetupForm::qt_property( int id, int f, QVariant* v)
{
    return QDialog::qt_property( id, f, v);
}

bool linkSetupForm::qt_static_property( QObject* , int , int , QVariant* ){ return FALSE; }
#endif // QT_NO_PROPERTIES
