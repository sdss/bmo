/****************************************************************************
** cameraControl meta object code from reading C++ file 'cameracontrol.h'
**
** Created: Wed Feb 16 11:24:28 2005
**      by: The Qt MOC ($Id: qt/moc_yacc.cpp   3.3.3   edited Aug 5 16:40 $)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#undef QT_NO_COMPAT
#include "../.ui/cameracontrol.h"
#include <qmetaobject.h>
#include <qapplication.h>

#include <private/qucomextra_p.h>
#if !defined(Q_MOC_OUTPUT_REVISION) || (Q_MOC_OUTPUT_REVISION != 26)
#error "This file was generated using the moc from 3.3.3. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

const char *cameraControl::className() const
{
    return "cameraControl";
}

QMetaObject *cameraControl::metaObj = 0;
static QMetaObjectCleanUp cleanUp_cameraControl( "cameraControl", &cameraControl::staticMetaObject );

#ifndef QT_NO_TRANSLATION
QString cameraControl::tr( const char *s, const char *c )
{
    if ( qApp )
	return qApp->translate( "cameraControl", s, c, QApplication::DefaultCodec );
    else
	return QString::fromLatin1( s );
}
#ifndef QT_NO_TRANSLATION_UTF8
QString cameraControl::trUtf8( const char *s, const char *c )
{
    if ( qApp )
	return qApp->translate( "cameraControl", s, c, QApplication::UnicodeUTF8 );
    else
	return QString::fromUtf8( s );
}
#endif // QT_NO_TRANSLATION_UTF8

#endif // QT_NO_TRANSLATION

QMetaObject* cameraControl::staticMetaObject()
{
    if ( metaObj )
	return metaObj;
    QMetaObject* parentObject = QDialog::staticMetaObject();
    static const QUMethod slot_0 = {"linkSetupClicked", 0, 0 };
    static const QUMethod slot_1 = {"grabClicked", 0, 0 };
    static const QUMethod slot_2 = {"establishLinkClicked", 0, 0 };
    static const QUMethod slot_3 = {"shutdownClicked", 0, 0 };
    static const QUMethod slot_4 = {"updateStatus", 0, 0 };
    static const QUMethod slot_5 = {"timerTick", 0, 0 };
    static const QUMethod slot_6 = {"updateCoolingClicked", 0, 0 };
    static const QUMethod slot_7 = {"languageChange", 0, 0 };
    static const QMetaData slot_tbl[] = {
	{ "linkSetupClicked()", &slot_0, QMetaData::Public },
	{ "grabClicked()", &slot_1, QMetaData::Public },
	{ "establishLinkClicked()", &slot_2, QMetaData::Public },
	{ "shutdownClicked()", &slot_3, QMetaData::Public },
	{ "updateStatus()", &slot_4, QMetaData::Public },
	{ "timerTick()", &slot_5, QMetaData::Public },
	{ "updateCoolingClicked()", &slot_6, QMetaData::Public },
	{ "languageChange()", &slot_7, QMetaData::Protected }
    };
    metaObj = QMetaObject::new_metaobject(
	"cameraControl", parentObject,
	slot_tbl, 8,
	0, 0,
#ifndef QT_NO_PROPERTIES
	0, 0,
	0, 0,
#endif // QT_NO_PROPERTIES
	0, 0 );
    cleanUp_cameraControl.setMetaObject( metaObj );
    return metaObj;
}

void* cameraControl::qt_cast( const char* clname )
{
    if ( !qstrcmp( clname, "cameraControl" ) )
	return this;
    return QDialog::qt_cast( clname );
}

bool cameraControl::qt_invoke( int _id, QUObject* _o )
{
    switch ( _id - staticMetaObject()->slotOffset() ) {
    case 0: linkSetupClicked(); break;
    case 1: grabClicked(); break;
    case 2: establishLinkClicked(); break;
    case 3: shutdownClicked(); break;
    case 4: updateStatus(); break;
    case 5: timerTick(); break;
    case 6: updateCoolingClicked(); break;
    case 7: languageChange(); break;
    default:
	return QDialog::qt_invoke( _id, _o );
    }
    return TRUE;
}

bool cameraControl::qt_emit( int _id, QUObject* _o )
{
    return QDialog::qt_emit(_id,_o);
}
#ifndef QT_NO_PROPERTIES

bool cameraControl::qt_property( int id, int f, QVariant* v)
{
    return QDialog::qt_property( id, f, v);
}

bool cameraControl::qt_static_property( QObject* , int , int , QVariant* ){ return FALSE; }
#endif // QT_NO_PROPERTIES
