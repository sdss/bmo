/****************************************************************************
** ImageViewer meta object code from reading C++ file 'showimg.h'
**
** Created: Wed Feb 16 11:24:19 2005
**      by: The Qt MOC ($Id: qt/moc_yacc.cpp   3.3.3   edited Aug 5 16:40 $)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#undef QT_NO_COMPAT
#include "../showimg.h"
#include <qmetaobject.h>
#include <qapplication.h>

#include <private/qucomextra_p.h>
#if !defined(Q_MOC_OUTPUT_REVISION) || (Q_MOC_OUTPUT_REVISION != 26)
#error "This file was generated using the moc from 3.3.3. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

const char *ImageViewer::className() const
{
    return "ImageViewer";
}

QMetaObject *ImageViewer::metaObj = 0;
static QMetaObjectCleanUp cleanUp_ImageViewer( "ImageViewer", &ImageViewer::staticMetaObject );

#ifndef QT_NO_TRANSLATION
QString ImageViewer::tr( const char *s, const char *c )
{
    if ( qApp )
	return qApp->translate( "ImageViewer", s, c, QApplication::DefaultCodec );
    else
	return QString::fromLatin1( s );
}
#ifndef QT_NO_TRANSLATION_UTF8
QString ImageViewer::trUtf8( const char *s, const char *c )
{
    if ( qApp )
	return qApp->translate( "ImageViewer", s, c, QApplication::UnicodeUTF8 );
    else
	return QString::fromUtf8( s );
}
#endif // QT_NO_TRANSLATION_UTF8

#endif // QT_NO_TRANSLATION

QMetaObject* ImageViewer::staticMetaObject()
{
    if ( metaObj )
	return metaObj;
    QMetaObject* parentObject = QWidget::staticMetaObject();
    static const QUMethod slot_0 = {"hFlip", 0, 0 };
    static const QUMethod slot_1 = {"vFlip", 0, 0 };
    static const QUMethod slot_2 = {"rot180", 0, 0 };
    static const QUMethod slot_3 = {"showContrast", 0, 0 };
    static const QUMethod slot_4 = {"showImageInfo", 0, 0 };
    static const QUMethod slot_5 = {"zoom4To1", 0, 0 };
    static const QUMethod slot_6 = {"zoom2To1", 0, 0 };
    static const QUMethod slot_7 = {"zoom1To1", 0, 0 };
    static const QUMethod slot_8 = {"zoom1To2", 0, 0 };
    static const QUMethod slot_9 = {"zoom1To4", 0, 0 };
    static const QUMethod slot_10 = {"autoContrast", 0, 0 };
    static const QUMethod slot_11 = {"inverseVideo", 0, 0 };
    static const QUMethod slot_12 = {"newWindow", 0, 0 };
    static const QUMethod slot_13 = {"openFile", 0, 0 };
    static const QUParameter param_slot_14[] = {
	{ 0, &static_QUType_int, 0, QUParameter::In }
    };
    static const QUMethod slot_14 = {"savePixmap", 1, param_slot_14 };
    static const QUMethod slot_15 = {"saveImage", 0, 0 };
    static const QUMethod slot_16 = {"giveHelp", 0, 0 };
    static const QMetaData slot_tbl[] = {
	{ "hFlip()", &slot_0, QMetaData::Private },
	{ "vFlip()", &slot_1, QMetaData::Private },
	{ "rot180()", &slot_2, QMetaData::Private },
	{ "showContrast()", &slot_3, QMetaData::Private },
	{ "showImageInfo()", &slot_4, QMetaData::Private },
	{ "zoom4To1()", &slot_5, QMetaData::Private },
	{ "zoom2To1()", &slot_6, QMetaData::Private },
	{ "zoom1To1()", &slot_7, QMetaData::Private },
	{ "zoom1To2()", &slot_8, QMetaData::Private },
	{ "zoom1To4()", &slot_9, QMetaData::Private },
	{ "autoContrast()", &slot_10, QMetaData::Private },
	{ "inverseVideo()", &slot_11, QMetaData::Private },
	{ "newWindow()", &slot_12, QMetaData::Private },
	{ "openFile()", &slot_13, QMetaData::Private },
	{ "savePixmap(int)", &slot_14, QMetaData::Private },
	{ "saveImage()", &slot_15, QMetaData::Private },
	{ "giveHelp()", &slot_16, QMetaData::Private }
    };
    metaObj = QMetaObject::new_metaobject(
	"ImageViewer", parentObject,
	slot_tbl, 17,
	0, 0,
#ifndef QT_NO_PROPERTIES
	0, 0,
	0, 0,
#endif // QT_NO_PROPERTIES
	0, 0 );
    cleanUp_ImageViewer.setMetaObject( metaObj );
    return metaObj;
}

void* ImageViewer::qt_cast( const char* clname )
{
    if ( !qstrcmp( clname, "ImageViewer" ) )
	return this;
    return QWidget::qt_cast( clname );
}

bool ImageViewer::qt_invoke( int _id, QUObject* _o )
{
    switch ( _id - staticMetaObject()->slotOffset() ) {
    case 0: hFlip(); break;
    case 1: vFlip(); break;
    case 2: rot180(); break;
    case 3: showContrast(); break;
    case 4: showImageInfo(); break;
    case 5: zoom4To1(); break;
    case 6: zoom2To1(); break;
    case 7: zoom1To1(); break;
    case 8: zoom1To2(); break;
    case 9: zoom1To4(); break;
    case 10: autoContrast(); break;
    case 11: inverseVideo(); break;
    case 12: newWindow(); break;
    case 13: openFile(); break;
    case 14: savePixmap((int)static_QUType_int.get(_o+1)); break;
    case 15: saveImage(); break;
    case 16: giveHelp(); break;
    default:
	return QWidget::qt_invoke( _id, _o );
    }
    return TRUE;
}

bool ImageViewer::qt_emit( int _id, QUObject* _o )
{
    return QWidget::qt_emit(_id,_o);
}
#ifndef QT_NO_PROPERTIES

bool ImageViewer::qt_property( int id, int f, QVariant* v)
{
    return QWidget::qt_property( id, f, v);
}

bool ImageViewer::qt_static_property( QObject* , int , int , QVariant* ){ return FALSE; }
#endif // QT_NO_PROPERTIES
