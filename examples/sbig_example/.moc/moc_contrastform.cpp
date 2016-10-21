/****************************************************************************
** contrastForm meta object code from reading C++ file 'contrastform.h'
**
** Created: Wed Feb 16 11:24:32 2005
**      by: The Qt MOC ($Id: qt/moc_yacc.cpp   3.3.3   edited Aug 5 16:40 $)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#undef QT_NO_COMPAT
#include "../.ui/contrastform.h"
#include <qmetaobject.h>
#include <qapplication.h>

#include <private/qucomextra_p.h>
#if !defined(Q_MOC_OUTPUT_REVISION) || (Q_MOC_OUTPUT_REVISION != 26)
#error "This file was generated using the moc from 3.3.3. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

const char *contrastForm::className() const
{
    return "contrastForm";
}

QMetaObject *contrastForm::metaObj = 0;
static QMetaObjectCleanUp cleanUp_contrastForm( "contrastForm", &contrastForm::staticMetaObject );

#ifndef QT_NO_TRANSLATION
QString contrastForm::tr( const char *s, const char *c )
{
    if ( qApp )
	return qApp->translate( "contrastForm", s, c, QApplication::DefaultCodec );
    else
	return QString::fromLatin1( s );
}
#ifndef QT_NO_TRANSLATION_UTF8
QString contrastForm::trUtf8( const char *s, const char *c )
{
    if ( qApp )
	return qApp->translate( "contrastForm", s, c, QApplication::UnicodeUTF8 );
    else
	return QString::fromUtf8( s );
}
#endif // QT_NO_TRANSLATION_UTF8

#endif // QT_NO_TRANSLATION

QMetaObject* contrastForm::staticMetaObject()
{
    if ( metaObj )
	return metaObj;
    QMetaObject* parentObject = QDialog::staticMetaObject();
    static const QUMethod slot_0 = {"onApply", 0, 0 };
    static const QUMethod slot_1 = {"setControls", 0, 0 };
    static const QUMethod slot_2 = {"languageChange", 0, 0 };
    static const QUParameter param_slot_3[] = {
	{ 0, &static_QUType_bool, 0, QUParameter::Out }
    };
    static const QUMethod slot_3 = {"validate", 1, param_slot_3 };
    static const QMetaData slot_tbl[] = {
	{ "onApply()", &slot_0, QMetaData::Public },
	{ "setControls()", &slot_1, QMetaData::Public },
	{ "languageChange()", &slot_2, QMetaData::Protected },
	{ "validate()", &slot_3, QMetaData::Protected }
    };
    metaObj = QMetaObject::new_metaobject(
	"contrastForm", parentObject,
	slot_tbl, 4,
	0, 0,
#ifndef QT_NO_PROPERTIES
	0, 0,
	0, 0,
#endif // QT_NO_PROPERTIES
	0, 0 );
    cleanUp_contrastForm.setMetaObject( metaObj );
    return metaObj;
}

void* contrastForm::qt_cast( const char* clname )
{
    if ( !qstrcmp( clname, "contrastForm" ) )
	return this;
    return QDialog::qt_cast( clname );
}

bool contrastForm::qt_invoke( int _id, QUObject* _o )
{
    switch ( _id - staticMetaObject()->slotOffset() ) {
    case 0: onApply(); break;
    case 1: setControls(); break;
    case 2: languageChange(); break;
    case 3: static_QUType_bool.set(_o,validate()); break;
    default:
	return QDialog::qt_invoke( _id, _o );
    }
    return TRUE;
}

bool contrastForm::qt_emit( int _id, QUObject* _o )
{
    return QDialog::qt_emit(_id,_o);
}
#ifndef QT_NO_PROPERTIES

bool contrastForm::qt_property( int id, int f, QVariant* v)
{
    return QDialog::qt_property( id, f, v);
}

bool contrastForm::qt_static_property( QObject* , int , int , QVariant* ){ return FALSE; }
#endif // QT_NO_PROPERTIES
