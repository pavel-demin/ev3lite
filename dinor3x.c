#include "ev3.c"

int main()
{
  ev3_init();

  /* calibrate legs */

  ev3_output_speed(0x02, 10);
  ev3_output_speed(0x04, 20);
  ev3_output_start(0x06);

  while(1)
  {
    if(ev3_analog->InPin6[0] < 500) break;
    usleep(1000);
  }

  ev3_output_stop(0x06, 1);

  ev3_output_speed(0x02, 40);
  ev3_output_start(0x02);

  while(1)
  {
    if(ev3_analog->InPin6[0] > 500) break;
    usleep(1000);
  }

  ev3_output_stop(0x02, 1);

  ev3_output_step_speed(0x02, -50, 0, 72, 0,  1);
  ev3_output_wait(0x02);

  ev3_output_speed(0x04, 40);
  ev3_output_start(0x04);

  while(1)
  {
    if(ev3_analog->InPin6[0] > 500) break;
    usleep(1000);
  }

  ev3_output_stop(0x04, 1);

  ev3_output_step_speed(0x04, -50, 0, 72, 0,  1);
  ev3_output_wait(0x04);

  ev3_output_clear(0x06);

  /* close jaws */

  ev3_output_time_speed(0x01, 20, 0, 500, 0,  0);
  ev3_output_wait(0x01);

  /* main loop */

  ev3_output_time_sync(0x06, -40, 0, 0, 0);

  while(1)
  {
    if(ev3_uart->Raw[3][ev3_uart->Actual[3]][0] < 25) break;
    if(ev3_ui->Pressed[5]) break;
    usleep(1000);
  }

  ev3_output_stop(0x06, 0);

  return EXIT_SUCCESS;
}
