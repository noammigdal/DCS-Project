#include  "../header/api.h"         // private library - API layer
#include  "../header/halGPIO.h"     // private library - HAL layer
#include  "../header/flash.h"     // private library - FLASH layer
#include "stdio.h"
#include "math.h"

int flag_script = 1;
int16_t Vrx = 0;
int16_t Vry = 0;
unsigned int count_num = 0;
char string_lcd[5];
unsigned int count_down = 65535;
char count_down_str[5];
unsigned int* count_down_address = &count_down;
char string_lcd[5];
unsigned char empty = ' ';

//-------------------------------------------------------------
//                Paint
//-------------------------------------------------------------
void paint_by_joystick(){
    JoyStickPBIntEN &= ~BIT5;
    i = 0;
    if(!state_toggle) { //send data
        ADC10CTL0 &= ~ENC;
        while (ADC10CTL1 & ADC10BUSY);
        ADC10SA = &Vr;                        // Data buffer start
        ADC10CTL0 |= ENC + ADC10SC; // Sampling start
        __bis_SR_register(LPM0_bits + GIE);

        UCA0TXBUF = Vr[i] & 0xFF;
        MSBIFG = 1;
        IE2 |= UCA0TXIE;
        __bis_SR_register(LPM0_bits + GIE);

    }

    else if (state_toggle) { //send state
        UCA0TXBUF = state_changed[i] & 0xFF;
        MSBIFG = 1;
        IE2 |= UCA0TXIE;
        __bis_SR_register(LPM0_bits + GIE);


        START_TIMERA0(5000); // wait for PC to sync
        JoyStickIntPend &= ~BIT5;

    }

    JoyStickPBIntEN |= BIT5; // allow interrupt only in the end of cycle
}
//-------------------------------------------------------------
//                MotorByJoystick
//-------------------------------------------------------------
void JoyStickADC_start(){
        ADC10CTL0 &= ~ENC;
        while (ADC10CTL1 & ADC10BUSY);
        ADC10SA = &Vr;                        // Data buffer start
        ADC10CTL0 |= ENC + ADC10SC; // Sampling start
        __bis_SR_register(LPM0_bits + GIE);

}
//-----------For Flash-------------------------------------
void script_mode() {

    if(download_flag){
        download_flag=0;
        FCTL2 = FWKEY + FSSEL0 + FN1;             // MCLK/3 for Flash Timing Generator
        file.file_size[file.num_of_files - 1] = strlen(file_content) - 1;
        copy_seg_flash();
        finish_Script(); // send ACK to PC
        IE2 |= UCA0RXIE;
    }
    if(ExecuteFlag){
        ExecuteFlag=0;
        flag_script = 1;
        delay_time = 500;  // delay default time
        RunScript();
        finish_Script(); // finish script
    }
    __bis_SR_register(LPM0_bits + GIE);
}

//---------------Execute Script--------------------------------
void RunScript(void)
{
    char *script_pointers;                         // Segment pointer
    char OPCstr[10], flash_argument[20], flash_argument2[20];
    unsigned int arg2ToInt, X, start, stop, y;
    if (flag_script)
        script_pointers = file.file_ptr[file.num_of_files - 1];
    flag_script = 0;
    for (y = 0; y < 64;)
    {
        OPCstr[0] = *script_pointers++;
        OPCstr[1] = *script_pointers++;
        y = y + 2;
        switch (OPCstr[1])
        {
        case '1':
            count_num = 0;
            flash_argument[0] = *script_pointers++;
            flash_argument[1] = *script_pointers++;
            y = y + 2;
            arg2ToInt = hex2int(flash_argument);
            while (arg2ToInt > 0)
            {
                count_up_LCD();    //count up on lcd
                arg2ToInt--;
            }
            break;

        case '2':
            flash_argument[0] = *script_pointers++;
            flash_argument[1] = *script_pointers++;
            y = y + 2;
            arg2ToInt = hex2int(flash_argument);
            count_down = arg2ToInt;
            while (arg2ToInt)
            {
                count_down_LCD();       //count down on lcd
                arg2ToInt--;
            }
            break;
        case '3':
            flash_argument[0] = *script_pointers++;
            flash_argument[1] = *script_pointers++;
            y = y + 2;
            arg2ToInt = hex2int(flash_argument);
            char ascii = (char)arg2ToInt;
            rrc_lcd(ascii);         //rotate char right
            break;
        case '4':
            flash_argument[0] = *script_pointers++;
            flash_argument[1] = *script_pointers++;
            y = y + 2;
            delay_time = hex2int(flash_argument);
            delay_time = delay_time * 10 ; //its in unit of 10ms
            break;
        case '5':
            lcd_clear();
            break;
        case '6': //motor to degree p
            case_6_script = 1;
            flash_argument[0] = *script_pointers++;
            flash_argument[1] = *script_pointers++;
            y = y + 2;
            X = hex2int(flash_argument);
            GoTo(X, OPCstr[1]);
            break;
        case '7': //scan between l to r
            flash_argument[0] = *script_pointers++;
            flash_argument[1] = *script_pointers++;
            y = y + 2;
            flash_argument2[0] = *script_pointers++;
            flash_argument2[1] = *script_pointers++;
            y = y + 2;
            X = hex2int(flash_argument);
            start = X;
            GoTo(X, OPCstr[1]);
            X = hex2int(flash_argument2);
            stop = X;
            GoTo(X, OPCstr[1]);

            break;
        case '8': // go sleep
            break;

        }
    }
}
//-------------------------------------------------------------
//*************************************************************
//****************Script Functions*****************************
//-------------------------------------------------------------
//                1. Count Up
//-------------------------------------------------------------
void count_up_LCD(){
    lcd_clear();
    lcd_home();
    lcd_puts("Count Up: ");
    lcd_new_line;
    put_on_lcd(string_lcd, count_num);
    timer_call_counter();
    count_num = (count_num + 1) % 65536;
    lcd_clear();
}
//-------------------------------------------------------------
//                2. Count Down
//-------------------------------------------------------------
void count_down_LCD() {
    unsigned int i = 0;
    lcd_clear();
    lcd_home();
    lcd_puts("Count Down: ");
    lcd_new_line;
    itoa_(count_down_str, *count_down_address);
    lcd_puts(count_down_str);
    timer_call_counter();
    *count_down_address = (*count_down_address - 1);
    if (*count_down_address == 0) *count_down_address = 65535;
    lcd_clear();
}


//-------------------------------------------------------------
//                 Rotate LCD
//-------------------------------------------------------------
void rrc_lcd(char asci){
    lcd_clear();
    lcd_home();
    int i = 0;
    for (i=0; i<16; i++) {
        lcd_data(asci);
        timer_call_counter();
        lcd_cursor_left();
        lcd_data(empty);
    }
    lcd_cmd(0xC0);
    int j = 0;
        for (j=0; j<16; j++) {
            lcd_data(asci);
            timer_call_counter();
            lcd_cursor_left();
            lcd_data(empty);
        }
}


//*************************************************************
//*************************************************************
//-------------------------------------------------------------
//                Stepper clockwise
//-------------------------------------------------------------
void Motor_clockwise(long delay){
    clockwise = 1;
    START_TIMERA0(delay); // (2^20/8)*(1/50[Hz]) = 2621
}

//-------------------------------------------------------------
//                Stepper counter-clockwise
//-------------------------------------------------------------
void Motor_counter_clockwise(long delay){
    clockwise = 0;
    START_TIMERA0(delay); // (2^20/8)*(1/50[Hz]) = 2621
}


//-------------------------------------------------------------
//                Stepper Motor Calibration
//-------------------------------------------------------------
void calibrate(){
    itoa_(counter_str, counter);
    tx_index = 0;
    UCA0TXBUF = counter_str[tx_index++];
    IE2 |= UCA0TXIE;                        // Enable USCI_A0 TX interrupt
    __bis_SR_register(LPM0_bits + GIE); // Sleep
    curr_counter = 0;
}
//--------------------------------------------------------------

//--------------------------------------------------------------
//-------------------------------------------------------------
//                motor Using JoyStick
//-------------------------------------------------------------
void MotorByJoystick(){
    uint32_t counter_degree;       //calculate the number of steps the motor should take according to the joystick's degree
    uint32_t degree;
    uint32_t temp;
    while (counter != 0 && state==state0 && main_state==stateJoystickRotate){
        JoyStickADC_start();
        if (!( Vr[1] > 400 && Vr[1] < 600 && Vr[0] > 400 && Vr[0] < 600)){
            Vrx = Vr[1] - 512;
            Vry = Vr[0] - 512;

            degree = atan2_fp(Vry, Vrx);
            temp = degree * counter;      //normalizes the angle to a specific number of steps

            if (270 < degree) {
                counter_degree = ((counter * 7) / 4) - (temp / 360);  // ((630-degree)/360)*counter;
                }
            else {
                counter_degree = ((counter * 3) / 4) - (temp / 360);  // ((270-degree)/360)*counter;
                }
            if ((int)(curr_counter - counter_degree) < 0) {
                Motor_clockwise(200);
                curr_counter++;
            }
            else {
                Motor_counter_clockwise(200);
                curr_counter--;
            }
        }
    }

}
