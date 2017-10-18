#include "ev3.c"

int main()
{
  int value;

  ev3_init();

  ev3_output_step_speed(0x06, 75, 180, 1800, 180,  1);
  ev3_output_wait(0x06);

  ev3_output_step_speed(0x06, -75, -180, -1800, -180,  1);
  ev3_output_wait(0x06);

  ev3_fb_clean();

  ev3_fb_printf(2, 7, "Press BACK");

  while(1)
  {
    usleep(1000);

    value = ev3_analog->Pin6[0][ev3_analog->Actual[0]] > 416;
    ev3_fb_printf(1, 2, "IN 1: %4d", value);

    value = ev3_uart->Raw[3][ev3_uart->Actual[3]][0];
    ev3_fb_printf(1, 4, "IN 4: %4d", value);

    if(ev3_ui->Pressed[5]) break;
  }

  return EXIT_SUCCESS;
}
