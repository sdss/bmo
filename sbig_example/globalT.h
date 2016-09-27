#include <qmessagebox.h>
#include "stdio.h"

typedef enum { PT_USB, PT_ETHERNET } PORT_TYPE;

class globalT {
public:
    bool  connected;    
  
    int		portType;  //0=USB, 1=Ethernet
    QString	ip;
    double	exposure;
    int		activeCCD; //0=imaging, 1=tracking
    int		resolution; //0=low, 1=med, 3=high
 
public:
    globalT() {
	connected = FALSE;
    }
    
    void loadSettings() {	
		FILE *fp;
		char s[80], s1[80];
		int i;
		double d;
		
		ip.append("127.0.0.0");
		portType = PT_USB;
		exposure = 1.0;
		activeCCD = 0;
		resolution = 0;
		while ( (fp = fopen("CCDOpsLitePrefs.txt", "rt")) != 0 ) {
			if ( fscanf(fp, "%[^\n]%*c", s) != 1 ) break;		//  header line
			if ( fscanf(fp, "%[^\n]%*c", s) != 1 ) break;		//  IP Address
			if ( sscanf(s, "IP_address = %s", s1) != 1 ) break;
			ip = s1;
			if ( fscanf(fp, "%[^\n]%*c", s) != 1 ) break;		//  Port Type
			if ( sscanf(s, "Port_type = %d", &i) == 0 || i<0 || i > 1 ) break;
			portType = i;
			if ( fscanf(fp, "%[^\n]%*c", s) != 1 ) break;		//  Exposure
			if ( sscanf(s, "Exposure = %lf", &d) == 0 || d<0.001 ) break;
			exposure = d;
			if ( fscanf(fp, "%[^\n]%*c", s) != 1 ) break;		//  Active CCD
			if ( sscanf(s, "Active_ccd = %d", &i) == 0 || i<0 || i > 1 ) break;
			activeCCD = i;
			if ( fscanf(fp, "%[^\n]%*c", s) != 1 ) break;		//  Resolution
			if ( sscanf(s, "Resolution = %d", &i) == 0 || i<0 || i > 1 ) break;
			resolution = i;
			break; 
		}
		if ( fp )
			fclose(fp);
   }
    
    void saveSettings() {
		FILE *fp;
		if ( (fp = fopen("CCDOpsLitePrefs.txt", "wt")) != 0 ) {
			fprintf(fp, "CCDOpsLite Preferences\n");
			fprintf(fp, "IP_address = %s\n", ip.ascii());
			fprintf(fp, "Port_type = %d\n", portType);
			fprintf(fp, "Exposure = %1.3lf\n", exposure);
			fprintf(fp, "Active_ccd = %d\n", activeCCD);
			fprintf(fp, "Resolution = %d\n", resolution);
			fprintf(fp, "End\n");
			fclose(fp);
		} else
			QMessageBox::information((QWidget*)0, "CCDOpsLite", "Error saving settings.");
    }
};

extern globalT globals;
