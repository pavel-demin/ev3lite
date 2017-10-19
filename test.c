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

  ev3_fb_printf(7, 2, "Press BACK");

  while(!ev3_ui->Pressed[5])
  {
    value = ev3_analog->InPin6[0] > 500;
    ev3_fb_printf(2, 1, "IN 1: %4d", value);

    value = ev3_uart->Raw[3][ev3_uart->Actual[3]][0];
    ev3_fb_printf(4, 1, "IN 4: %4d", value);

    usleep(1000);
  }

  return EXIT_SUCCESS;
}
