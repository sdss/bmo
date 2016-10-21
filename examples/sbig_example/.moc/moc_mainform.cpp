/****************************************************************************
** mainform meta object code from reading C++ file 'mainform.h'
**
** Created: Wed Feb 16 11:24:23 2005
**      by: The Qt MOC ($Id: qt/moc_yacc.cpp   3.3.3   edited Aug 5 16:40 $)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#undef QT_NO_COMPAT
#include "../.ui/mainform.h"
#include <qmetaobject.h>
#include <qapplication.h>

#include <private/qucomextra_p.h>
#if !defined(Q_MOC_OUTPUT_REVISION) || (Q_MOC_OUTPUT_REVISION != 26)
#error "This file was generated using the moc from 3.3.3. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

const char *mainform::className() const
{
    return "mainform";
}

QMetaObject *mainform::metaObj = 0;
static QMetaObjectCleanUp cleanUp_mainform( "mainform", &mainform::staticMetaObject );

#ifndef QT_NO_TRANSLATION
QString mainform::tr( const char *s, const char *c )
{
    if ( qApp )
	return qApp->translate( "mainform", s, c, QApplication::DefaultCodec );
    else
	return QString::fromLatin1( s );
}
#ifndef QT_NO_TRANSLATION_UTF8
QString mainform::trUtf8( const char *s, const char *c )
{
    if ( qApp )
	return qApp->translate( "mainform", s, c, QApplication::UnicodeUTF8 );
    else
	return QString::fromUtf8( s );
}
#endif // QT_NO_TRANSLATION_UTF8

#endif // QT_NO_TRANSLATION

QMetaObject* mainform::staticMetaObject()
{
    if ( metaObj )
	return metaObj;
    QMetaObject* parentObject = QMainWindow::staticMetaObject();
    static const QUMethod slot_0 = {"fileOpen", 0, 0 };
    static const QUParameter param_slot_1[] = {
	{ 0, &static_QUType_ptr, "QCloseEvent", QUParameter::In }
    };
    static const QUMethod slot_1 = {"closeEvent", 1, param_slot_1 };
    static const QUMethod slot_2 = {"fileExit", 0, 0 };
    static const QUMethod slot_3 = {"helpIndex", 0, 0 };
    static const QUMethod slot_4 = {"helpContents", 0, 0 };
    static const QUMethod slot_5 = {"helpAbout", 0, 0 };
    static const QUMethod slot_6 = {"editOptions", 0, 0 };
    static const QUMethod slot_7 = {"cameraSetup", 0, 0 };
    static const QUMethod slot_8 = {"languageChange", 0, 0 };
    static const QMetaData slot_tbl[] = {
	{ "fileOpen()", &slot_0, QMetaData::Public },
	{ "closeEvent(QCloseEvent*)", &slot_1, QMetaData::Public },
	{ "fileExit()", &slot_2, QMetaData::Public },
	{ "helpIndex()", &slot_3, QMetaData::Public },
	{ "helpContents()", &slot_4, QMetaData::Public },
	{ "helpAbout()", &slot_5, QMetaData::Public },
	{ "editOptions()", &slot_6, QMetaData::Public },
	{ "cameraSetup()", &slot_7, QMetaData::Public },
	{ "languageChange()", &slot_8, QMetaData::Protected }
    };
    metaObj = QMetaObject::new_metaobject(
	"mainform", parentObject,
	slot_tbl, 9,
	0, 0,
#ifndef QT_NO_PROPERTIES
	0, 0,
	0, 0,
#endif // QT_NO_PROPERTIES
	0, 0 );
    cleanUp_mainform.setMetaObject( metaObj );
    return metaObj;
}

void* mainform::qt_cast( const char* clname )
{
    if ( !qstrcmp( clname, "mainform" ) )
	return this;
    return QMainWindow::qt_cast( clname );
}

bool mainform::qt_invoke( int _id, QUObject* _o )
{
    switch ( _id - staticMetaObject()->slotOffset() ) {
    case 0: fileOpen(); break;
    case 1: closeEvent((QCloseEvent*)static_QUType_ptr.get(_o+1)); break;
    case 2: fileExit(); break;
    case 3: helpIndex(); break;
    case 4: helpContents(); break;
    case 5: helpAbout(); break;
    case 6: editOptions(); break;
    case 7: cameraSetup(); break;
    case 8: languageChange(); break;
    default:
	return QMainWindow::qt_invoke( _id, _o );
    }
    return TRUE;
}

bool mainform::qt_emit( int _id, QUObject* _o )
{
    return QMainWindow::qt_emit(_id,_o);
}
#ifndef QT_NO_PROPERTIES

bool mainform::qt_property( int id, int f, QVariant* v)
{
    return QMainWindow::qt_property( id, f, v);
}

bool mainform::qt_static_property( QObject* , int , int , QVariant* ){ return FALSE; }
#endif // QT_NO_PROPERTIES
