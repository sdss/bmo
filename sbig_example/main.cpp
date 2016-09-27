#include <qapplication.h>
#include "mainform.h"
#include "imagefip.h"
#include "globalT.h"

globalT globals;

int main( int argc, char ** argv )
{
	QApplication a( argc, argv );
	ImageIconProvider iip;
	QFileDialog::setIconProvider( &iip );
	
	globals.loadSettings();
	mainform *w = new mainform;    
	w->show();
	int ret = a.exec();
	delete w;// force close of forms so destructor updates global vars
	globals.saveSettings();
	return ret;
}
