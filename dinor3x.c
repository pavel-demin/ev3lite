#include <pthread.h>

#include "ev3.c"

void *dinor3x(void *arg)
{
  int i;

  /* calibrate legs */

  ev3_output_time_sync(0x06, 20, 50, 0, 0);

  while(ev3_analog->InPin6[0] > 500) usleep(1000);

  ev3_output_stop(0x06, 1);

  ev3_output_speed(0x02, 40);
  ev3_output_start(0x02);

  while(ev3_analog->InPin6[0] < 500) usleep(1000);

  ev3_output_stop(0x02, 1);

  ev3_output_step_speed(0x02, -50, 0, 72, 0,  1);
  ev3_output_wait(0x02);

  ev3_output_speed(0x04, 40);
  ev3_output_start(0x04);

  while(ev3_analog->InPin6[0] < 500) usleep(1000);

  ev3_output_stop(0x04, 1);

  ev3_output_step_speed(0x04, -50, 0, 72, 0,  1);
  ev3_output_wait(0x04);

  /* close jaws */

  ev3_output_time_speed(0x01, 20, 0, 500, 0,  0);
  ev3_output_wait(0x01);

  /* main loop */

  while(1)
  {
    ev3_output_time_sync(0x06, -40, 0, 0, 0);

    while(ev3_uart->Raw[3][ev3_uart->Actual[3]][0] > 25) usleep(1000);

    ev3_output_stop(0x06, 0);

    ev3_output_step_sync(0x06, 75, 0, 1800, 1);

    ev3_output_time_speed(0x01, 40, 0, 100, 0,  1);

    for(i = 0; i < 12; ++i)
    {
      ev3_output_time_speed(0x01, -40, 0, 100, 0,  1);
      ev3_output_wait(0x01);
      ev3_output_time_speed(0x01, 40, 0, 100, 0,  1);
      ev3_output_wait(0x01);
    }

    ev3_output_time_speed(0x01, 20, 0, 500, 0,  0);

    ev3_output_wait(0x06);
  }
}

int main()
{
  pthread_t thread;
  int value;

  ev3_init();

  if(pthread_create(&thread, NULL, dinor3x, NULL) < 0)
  {
    perror("pthread_create");
    return EXIT_FAILURE;
  }

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

  pthread_cancel(thread);
  pthread_join(thread, NULL);

  ev3_output_stop(0x0F, 0);

  return EXIT_SUCCESS;
}
