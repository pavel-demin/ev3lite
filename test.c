#include "ev3.c"

int main()
{
  int8_t value;
  uint8_t buffer[241];

  ev3_init();

  ev3_output_step_speed(0x06, 75, 180, 1800, 180,  1);
  ev3_output_wait(0x06);

  ev3_output_step_speed(0x06, -75, -180, -1800, -180,  1);
  ev3_output_wait(0x06);

  ev3_fb_clean();

  ev3_fb_print(2, 7, "Press BACK", 241);

  while(1)
  {
    usleep(1000);

    value = ev3_analog->Pin6[0][ev3_analog->Actual[0]] > 416;
    snprintf(buffer, 241, "IN 1: %4d", value);
    ev3_fb_print(1, 2, buffer, 241);

    value = ev3_uart->Raw[3][ev3_uart->Actual[3]][0];
    snprintf(buffer, 241, "IN 4: %4d", value);
    ev3_fb_print(1, 4, buffer, 241);

    if(ev3_ui->Pressed[5]) break;
  }

  return EXIT_SUCCESS;
}
