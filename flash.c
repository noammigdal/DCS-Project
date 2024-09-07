#include  "../header/flash.h"    // private library - flash layer
#include  "../header/halGPIO.h"    // private library - halGPIO layer
#include  "string.h"

//-----------------------------------------------------------------------------
//           FLASH driver
//-----------------------------------------------------------------------------

Files file;


void ScriptData(void)
{
    file.file_size[file.num_of_files - 1] = strlen(file_content) - 1;

}

void copy_seg_flash(void)
{
    char *Flash_ptr_write ;                          // Flash pointer
    unsigned int k;
    Flash_ptr_write = file.file_ptr[file.num_of_files - 1];      // Initialize Flash pointer
    FCTL1 = FWKEY + ERASE;                    // Set Erase bit
    FCTL3 = FWKEY;                            // Clear Lock bit
   *Flash_ptr_write = 0;                   // Dummy write to erase Flash segment

    FCTL1 = FWKEY + WRT;                      // Set WRT bit for write operation

    for (k = 0; k < file.file_size[file.num_of_files - 1]; k++)
    {
        if (file_content[k] == 0x0A || file_content[k] == 0x0D ){
            continue;
        }
        *Flash_ptr_write++ = file_content[k];            // Write value to flash
    }
    memset(DataFromPC,0,strlen(DataFromPC)); //clear file_content
    FCTL1 = FWKEY;                            // Clear WRT bit
    FCTL3 = FWKEY + LOCK;                     // Set LOCK bit
}
