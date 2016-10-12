#include "csbigcam.h"
#include <iostream>

int main() {
    using namespace std;

    SBIG_DEVICE_TYPE dev = DEV_USB1;
    // cout << dev << endl;
    CSBIGCam sbig(dev);
    QueryUSBResults results;
    int  *ptr_null = NULL;

    // cout << sbig.OpenDriver() << endl;
    // cout << sbig.GetError() << endl;

    SBIGUnivDrvCommand(CC_QUERY_USB, &ptr_null, &results);
    cout << results.usbInfo[0].name << endl;

    // cout << sbig.EstablishLink() << endl;
    // cout << sbig.GetError() << endl;
    // cout << sbig.GetCameraType() << endl;
    // cout << sbig.GetError() << endl;
}
