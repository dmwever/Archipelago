void AP_Write()
{
    xsCreateFile(false);
    xsWriteInt(1);
    xsWriteInt(xsGetGameTime());
    xsWriteFloat(6.5);
    xsWriteInt(2); 
    xsWriteInt(0);
    for (i = 0; < 12) {
    xsWriteInt(i);
    }
    for (i = 0; < 31) {
    xsWriteInt(i);
    }
    xsWriteInt(30);
    xsWriteInt(42);
    xsCloseFile();
}