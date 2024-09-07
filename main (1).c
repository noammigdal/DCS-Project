#include  "../header/api.h"         // private library - API layer
#include  "../header/app.h"         // private library - APP layer
#include  <stdio.h>


enum FSMstate state;
enum main_states main_state;
enum SYSmode lpm_mode;


void main(void){
  
  state = state0;  // start in idle state on RESET
  main_state = stateDefault;
  lpm_mode = mode0;
  sysConfig();


  while(1){
    switch(state){

    case state0: //   Motor Using JoyStick
        IE2 |= UCA0RXIE;
        switch(main_state){
        case stateStartRotate:
            while(rotateIFG){
                curr_counter++;
                Motor_clockwise(300); }
            break;

        case stateStopRotate:
            break;

        case stateJoystickRotate:
            counter = 514;
            MotorByJoystick();
            break;
        case stateDefault:
            __bis_SR_register(LPM0_bits + GIE);       // Enter LPM0
            break;
        }
        break;

    case state1: // Paint
        JoyStickPBIntEN |= BIT5; //enable PB
        while (state == state1){
            paint_by_joystick();
        }
        JoyStickPBIntEN &= ~BIT5; //disable PB
        break;

    case state2: // Calibrate
        IE2 |= UCA0RXIE;                          // Enable USCI_A0 RX interrupt

        switch(main_state){
        case stateDefault:
            __bis_SR_register(LPM0_bits + GIE);       // Enter LPM0 w/ int until Byte RXed
            break;

        case stateStartRotate: // start rotate
            counter = 0;
            while(rotateIFG) {
                Motor_clockwise(300);
            }
            break;

        case stateStopRotate: // stop and set degree
            calibrate();
            break;
        }
        break;

    case state3:  //Script
        IE2 |= UCA0RXIE;                          // Enable USCI_A0 RX interrupt
        while ( state == state3){
            script_mode();
        }
        break;

    case state4: //

        break;

    case state5: //

        break;

    case state6: //

        break;

    case state7: //

        break;

    case state8: //

        break;

    }
  }
}
