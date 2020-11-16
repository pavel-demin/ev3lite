#include <pthread.h>

#include "ev3.c"

float gyro_rate = 0.0;
float gyro_angle = 0.0;
float gyro_offset = 0.0;

float wheel_rate = 0.0;
float wheel_angle = 0.0;

int16_t power = 0;

void *control(void *arg)
{
  int16_t data;
  int32_t motor_angle, motor_previous;
  float motor_change;

  gyro_rate = 0.0;
  gyro_angle = 0.0;
  gyro_offset = 0.0;

  motor_change = 0.0;
  motor_previous = ev3_motor[0].TachoSensor + ev3_motor[3].TachoSensor;

  wheel_rate = 0.0;
  wheel_angle = 0.0;

  while(1)
  {
    memcpy(&data, ev3_uart->Raw[3][ev3_uart->Actual[3]], 2);

    gyro_offset = 0.999 * gyro_offset + 0.001 * data;
    gyro_rate = data - gyro_offset;
    gyro_angle += gyro_rate * 0.01;

    motor_angle = ev3_motor[0].TachoSensor + ev3_motor[3].TachoSensor;
    motor_change = motor_change * 0.6 + (motor_angle - motor_previous) * 0.4;
    motor_previous = motor_angle;

    wheel_angle += motor_change;
    wheel_rate = motor_change / 0.01;

    power = 15 * gyro_angle + 0.8 * gyro_rate + 0.08 * wheel_angle + 0.08 * wheel_rate;

    if(power > 100) power = 100;
    if(power < -100) power = -100;
    ev3_output_power(9, power);

    usleep(10000);
  }
}

int main()
{
  pthread_t thread;

  ev3_init();

  ev3_uart_mode(3, 1);

  ev3_output_clear(9);
  ev3_output_power(9, 0);
  ev3_output_start(9);

  if(pthread_create(&thread, NULL, control, NULL) < 0)
  {
    perror("pthread_create");
    return EXIT_FAILURE;
  }

  ev3_fb_clean();

  ev3_fb_printf(7, 2, "Press BACK");

  while(!ev3_ui->Pressed[5])
  {
    ev3_fb_printf(0, 0, "offset: %6.2f", gyro_offset);
    ev3_fb_printf(1, 0, "rate:   %6.2f", gyro_rate);
    ev3_fb_printf(2, 0, "angle:  %6.2f", gyro_angle);
    ev3_fb_printf(3, 0, "power:  %6d", power);

    usleep(10000);
  }

  pthread_cancel(thread);
  pthread_join(thread, NULL);

  ev3_output_stop(9, 0);

  return EXIT_SUCCESS;
}
